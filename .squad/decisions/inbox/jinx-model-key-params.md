# Decision: CLI Parameter Override Pattern for Provider Configuration

**Date**: 2026-03-08  
**Decider**: Jinx (Lead)  
**Issue**: #77 — Add `--model` and `--api-key` CLI parameters to lipsync_cli  
**PR**: #83  
**Status**: Approved

## Context

Users needed the ability to override LLM provider model names and API keys without modifying environment variables or code. This is particularly important for:
- Testing different model versions (e.g., `gemini-1.5-pro` vs `gemini-2.5-flash`)
- Using organization-specific or project-specific API keys
- Experimentation and debugging without global environment changes
- CI/CD pipelines with dynamic credentials

## Decision

Establish a consistent pattern for provider configuration across the `skill/` module:

### Pattern: Optional Constructor Parameters with Fallback Chain

1. **Provider constructors accept optional `api_key` and `model` parameters**
   - `GeminiProvider(api_key: str = None, model: str = None)`
   - `GeminiAudioProvider(api_key: str = None, model: str = None)`

2. **Fallback chain for API key**: CLI arg → env var → error
   ```python
   if api_key is None:
       api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
   if not api_key:
       raise EnvironmentError("No API key found...")
   ```

3. **Fallback chain for model**: CLI arg → DEFAULT_MODEL constant
   ```python
   DEFAULT_MODEL = "gemini-flash-latest"
   self.model = model or self.DEFAULT_MODEL
   ```

4. **CLI arguments in lipsync_cli.py**:
   - `--model` — override LLM provider model
   - `--audio-model` — override audio analysis provider model
   - `--api-key` — override API key for both providers

5. **Usage in CLI**:
   ```python
   provider_kwargs = {}
   if args.api_key:
       provider_kwargs["api_key"] = args.api_key
   if args.model:
       provider_kwargs["model"] = args.model
   llm_provider = GeminiProvider(**provider_kwargs)
   ```

## Consequences

### Positive
- **Explicit overrides**: Users can specify model/key per-invocation without global changes
- **Backward compatible**: Existing code using env vars continues to work unchanged
- **Testable**: Unit tests can inject custom models/keys without environment manipulation
- **Discoverable**: CLI help shows all configuration options in one place
- **Flexible**: Supports both convenience (env vars) and precision (CLI args)

### Negative
- **Parameter proliferation**: Each new provider may need `api_key` and `model` params
- **Repetition**: Fallback logic duplicated across providers (acceptable given clarity)

### Neutral
- **No validation**: CLI doesn't validate model names (deferred to provider API)
- **No interactive prompts**: Missing API key triggers immediate error, not prompt

## Alternatives Considered

1. **Config file (YAML/JSON)** — Rejected as overkill for 2-3 parameters
2. **Only env vars** — Rejected; insufficient for multi-tenant or testing scenarios
3. **Global provider registry** — Rejected as premature abstraction

## Implementation Notes

- **DEFAULT_MODEL vs MODEL**: Changed class attribute from `MODEL` to `DEFAULT_MODEL` to clarify it's a fallback, not a requirement
- **Instance attribute**: Use `self.model` (not `self.MODEL`) for runtime value to enable overrides
- **Tests unaffected**: All 54 skill module tests pass; mocked providers remain compatible

## Future Extensions

- Consider adding `--base-url` for OpenAI-compatible endpoints
- May extend pattern to timeouts, retries, temperature if needed
- Could add validation/autocomplete for known model names

---

**This pattern is now the standard for all provider classes in `skill/` module.**
