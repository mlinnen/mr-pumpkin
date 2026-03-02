# Implementation Decisions — Vi: Skill Package (Issue #39)

**Date:** 2026-03-02
**By:** Vi (Backend)
**Relates to:** WI-1, WI-2, WI-3, WI-7 from jinx-issue39-architecture.md

---

## Decision 1: Gemini as Default LLM Provider (Resolved)

**Decision:** Use `GeminiProvider` (gemini-1.5-flash) as the default per Mike's directive in `copilot-directive-20260302-llm-provider.md`.

**API key strategy:** `GEMINI_API_KEY` env var, fallback to `GOOGLE_API_KEY`. Clear `EnvironmentError` if neither present.

**Model choice:** `gemini-1.5-flash` — cheap, fast, strong at JSON generation. Per Mike's input.

---

## Decision 2: Provider Abstraction (Resolved)

**Decision:** Abstract base class `LLMProvider` with single `generate(system_prompt, user_prompt) -> str` method. `GeminiProvider` is the first implementation.

**Rationale:** Mike explicitly requested provider-agnostic design. Future providers (OpenAI, Anthropic, local Ollama) can be added without touching call sites.

**Note:** `GeminiProvider.__init__` embeds the system instruction in the model object at construction time, so the `system_prompt` parameter to `generate()` is ignored. This is a known trade-off — the interface is clean but the system prompt must be set at construction, not at call time. If a future provider needs per-call system prompts, the interface signature supports it.

---

## Decision 3: System Prompt Embedding Strategy (Resolved)

**Decision:** Embed full command vocabulary table and two example timelines directly in `_SYSTEM_PROMPT` constant in `generator.py`.

**Rationale:** Architecture doc (WI-1) recommended embedding rather than importing from codebase. This makes `generator.py` self-contained and testable in isolation without running pumpkin_face.py.

**Few-shot examples chosen:** "surprised then relieved" (emotion transition) and "getting sleepy" (progressive animation). These cover the most common use cases and teach the model timing conventions.

---

## Decision 4: No Autoplay After Upload (Resolved)

**Decision:** `upload_timeline()` returns after successful upload without sending a `play` command. Per Mike's directive in `copilot-directive-20260302-upload-no-autoplay.md`.

---

## Decision 5: Error on Duplicate Filename (Resolved)

**Decision:** If the server responds with an ERROR (including "already exists"), `upload_timeline()` raises `ValueError(response)`. No silent overwrite, no rename. Per Mike's directive in `copilot-directive-20260302-upload-error-on-duplicate.md`.

---

## Decision 6: WebSocket Optional Dependency (Resolved)

**Decision:** Check `importlib.util.find_spec("websockets")` before attempting WebSocket upload. Fall back to TCP with `RuntimeWarning` if `ws` protocol was requested but the library is unavailable.

**Rationale:** Matches pattern described in architecture doc — WebSocket support is optional. Users without the library should still be able to use TCP.

---

## ⚠️ Open Issue: Root requirements.txt Websocket Version Conflict

**Problem:** Root `requirements.txt` pins `websockets>=11.0,<12.0`. The `skill/requirements.txt` needs `websockets>=12.0` (for updated API compatibility). These ranges are mutually exclusive.

**Impact:** If a user installs both, pip will conflict. The root requirement prevents upgrading to >=12.0.

**Recommended resolution (for Jinx / Mike):**
- Option A: Relax root constraint to `websockets>=11.0` (no upper bound) — test that pumpkin_face.py WebSocket server still works on websockets 12.x
- Option B: Add skill dependencies to root `requirements.txt` and bump websockets to `>=12.0` — requires regression test of WS server on new version
- Option C: Keep `skill/requirements.txt` separate and document that users must upgrade websockets manually for skill features

**Current state:** Left `requirements.txt` unchanged pending this decision. Did NOT silently modify the root requirements to avoid breaking the existing WebSocket server.

---

## Decision 7: sys.path Manipulation for timeline Import (Resolved)

**Decision:** Use `sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))` at the top of `generator.py` to import `timeline.py` from the project root.

**Rationale:** `skill/` is co-located with `timeline.py` in the same repo. This is the cleanest approach without requiring packaging or a setup.py. The path manipulation is idempotent (inserting the same directory twice has no effect on lookups).

**Alternative considered:** Relative import `from ..timeline import Timeline` — but this requires `skill/` to be installed as a package, which conflicts with the simple "run from repo root" model.
