# Architecture Decision — Issue #39: Mr. Pumpkin Recording Skill

**Date:** 2026-03-02  
**By:** Jinx (Lead)  
**Issue:** #39 — Create a mr-pumpkin skill that allows a CLI with LLM capabilities to generate recordings using an AI prompt  
**Status:** Proposed

---

## 1. Problem Statement

Users want to create animated pumpkin face sequences (timeline recordings) using natural language instead of manually constructing JSON. A "skill" should translate prompts like *"make the pumpkin look surprised, then blink twice, look left, and smile"* into valid timeline JSON and upload it to the mr-pumpkin server.

---

## 2. Key Findings from Codebase Analysis

### 2.1 Timeline JSON Format (Canonical)

From `timeline.py`, the **authoritative** schema is:

```json
{
  "version": "1.0",
  "duration_ms": 5000,
  "commands": [
    {
      "time_ms": 0,
      "command": "set_expression",
      "args": { "expression": "happy" }
    },
    {
      "time_ms": 1000,
      "command": "blink"
    },
    {
      "time_ms": 2500,
      "command": "gaze",
      "args": { "x": 45.0, "y": 30.0 }
    }
  ]
}
```

**Critical fields:**
- `version`: Must be `"1.0"`
- `duration_ms`: Integer, must equal or exceed the largest `time_ms`
- `commands[].time_ms`: Integer milliseconds from start
- `commands[].command`: String command name
- `commands[].args`: Optional dict of command arguments

**⚠️ Documentation discrepancy:** `docs/building-a-client.md` shows `timestamp_ms` as the key, but `TimelineEntry.from_dict()` reads `data["time_ms"]`. The skill must use `time_ms` (the code-level truth).

### 2.2 Complete Command Vocabulary for Recordings

From `_capture_command_for_recording()` in `pumpkin_face.py`, the recordable commands are:

| Command | Args | Notes |
|---------|------|-------|
| `set_expression` | `{"expression": "<name>"}` | neutral, happy, sad, angry, surprised, scared, sleeping |
| `blink` | *(none)* | Both eyes blink |
| `wink_left` | *(none)* | Left eye wink |
| `wink_right` | *(none)* | Right eye wink |
| `roll_clockwise` | *(none)* | Eyes roll clockwise |
| `roll_counterclockwise` | *(none)* | Eyes roll counter-clockwise |
| `gaze` | `{"x": float, "y": float}` or `{"lx": float, "ly": float, "rx": float, "ry": float}` | -90 to +90 degrees |
| `eyebrow_raise` | *(none)* | Raise both |
| `eyebrow_lower` | *(none)* | Lower both |
| `eyebrow_raise_left` | *(none)* | Raise left |
| `eyebrow_lower_left` | *(none)* | Lower left |
| `eyebrow_raise_right` | *(none)* | Raise right |
| `eyebrow_lower_right` | *(none)* | Lower right |
| `eyebrow_reset` | *(none)* | Reset to neutral |
| `eyebrow` | `{"value": float}` or `{"left": float, "right": float}` | Numeric eyebrow control |
| `turn_left` | `{"amount": int}` | Default 50px |
| `turn_right` | `{"amount": int}` | Default 50px |
| `turn_up` | `{"amount": int}` | Default 50px |
| `turn_down` | `{"amount": int}` | Default 50px |
| `center_head` | *(none)* | Return to center |
| `twitch_nose` | `{"magnitude": float}` | Default 50.0 |
| `wiggle_nose` | `{"magnitude": float}` | Default 50.0 |
| `scrunch_nose` | `{"magnitude": float}` | Default 50.0 |
| `reset_nose` | *(none)* | Return to neutral |
| `projection_reset` | *(none)* | Reset projection offset |
| `jog_offset` | `{"dx": int, "dy": int}` | Nudge projection |
| `set_offset` | `{"x": int, "y": int}` | Absolute projection offset |

### 2.3 Upload Mechanisms

**TCP (Port 5000) — Multi-step handshake:**
1. Send `upload_timeline <filename>\n`
2. Wait for `READY` response
3. Send JSON content + `\n`
4. Send `END_UPLOAD\n`
5. Read `OK Uploaded <filename>.json` or `ERROR ...`

**WebSocket (Port 5001) — Single message:**
1. Send `upload_timeline <filename> <json_string>`
2. Read `OK Uploaded <filename>.json` or `ERROR ...`

Both paths call `FileManager.upload_timeline()` which validates JSON structure via `Timeline.from_dict()` before saving to `~/.mr-pumpkin/recordings/`.

### 2.4 What "Skill" Means Here

This is **not** a squad skill (`.squad/skills/` contains team knowledge patterns). This is a **user-facing tool** — specifically, a capability that can be invoked from a CLI assistant (like GitHub Copilot CLI, or any LLM-powered CLI) to generate and upload timeline recordings.

The closest analogy: a **Copilot Extension** or **MCP tool** that exposes mr-pumpkin animation generation as a callable capability.

---

## 3. Proposed Architecture

### 3.1 Component: Prompt-to-Timeline Generator (Core)

A Python module that:
1. Takes a natural language description of an animation
2. Constructs a system prompt containing the command vocabulary, JSON schema, and animation timing guidelines
3. Calls an LLM API to generate timeline JSON
4. Validates the generated JSON against the Timeline schema
5. Returns a valid `Timeline` object

**File:** `skill/generator.py` (new package)

**Key design:** The LLM prompt engineering is the heart of this feature. The system prompt must include:
- The full command vocabulary table (above)
- The exact JSON schema with `time_ms` / `command` / `args`
- Timing guidelines (e.g., "blinks take ~300ms", "allow 500ms between expressions for transitions")
- Example timelines for few-shot learning
- Constraints: version must be "1.0", time_ms must be sorted ascending, duration_ms must match

### 3.2 Component: Upload Client

A Python module that:
1. Takes a `Timeline` object and a filename
2. Connects to mr-pumpkin via TCP or WebSocket
3. Uploads the timeline using the established protocol
4. Returns success/failure status

**File:** `skill/uploader.py`

This is largely a refactored version of `client_example.py`'s `upload_timeline()` function, made importable and robust (retry, connection error handling, configurable host/port).

### 3.3 Component: CLI Entry Point

A command-line interface that:
1. Accepts a natural language prompt (interactive or via argument)
2. Calls the generator to produce timeline JSON
3. Optionally previews the timeline (show commands, duration)
4. Uploads to mr-pumpkin server (with `--upload` flag or interactive confirmation)
5. Optionally saves to a local file (with `--save` flag)

**File:** `skill/cli.py` or integrated into a Copilot extension

### 3.4 Component: MCP Tool Definition (Optional/Future)

If Mike wants this integrated as an MCP server for Copilot or other LLM CLIs:
- Define as an MCP tool with `generate_animation` and `upload_animation` capabilities
- Register in `.copilot/mcp-config.json`
- This would allow Copilot CLI to call it directly

---

## 4. Work Breakdown

### WI-1: Command Vocabulary Reference Document
**Owner:** Jinx  
**Effort:** 1 hour  
**Description:** Create a machine-readable reference of all recordable commands with their args schemas. This becomes the system prompt material for the LLM and the validation schema for generated output.  
**Dependencies:** None  
**Deliverable:** `skill/command_reference.json` or embedded in generator module

### WI-2: Prompt-to-Timeline Generator
**Owner:** Vi (Backend)  
**Effort:** 4-6 hours  
**Description:** Core module that takes natural language → LLM API call → validated Timeline JSON. Includes system prompt engineering, LLM API integration, response parsing, and schema validation.  
**Dependencies:** WI-1 (command vocabulary)  
**Key decisions needed:**
- LLM provider (OpenAI / Anthropic / configurable)
- API key management (env var `MR_PUMPKIN_LLM_API_KEY` or provider-specific)
- Model selection (GPT-4o-mini / Claude Haiku for cost efficiency, or configurable)

### WI-3: Upload Client Library
**Owner:** Vi (Backend)  
**Effort:** 2-3 hours  
**Description:** Refactor upload logic from `client_example.py` into an importable module with TCP and WebSocket support, connection error handling, and configurable host/port.  
**Dependencies:** None (existing protocol is stable)  
**Deliverable:** `skill/uploader.py`

### WI-4: CLI Entry Point
**Owner:** Vi (Backend)  
**Effort:** 2-3 hours  
**Description:** Command-line interface that orchestrates generation + upload. Supports `--prompt`, `--upload`, `--save`, `--host`, `--port`, `--preview` flags.  
**Dependencies:** WI-2, WI-3  
**Deliverable:** `skill/cli.py` (runnable as `python -m skill`)

### WI-5: Test Suite
**Owner:** Mylo (Tester)  
**Effort:** 4-6 hours  
**Description:** Tests covering:
- Generator produces valid Timeline JSON for various prompts (mock LLM responses)
- Generator rejects/repairs invalid LLM output (malformed JSON, unknown commands)
- Uploader handles connection success, failure, timeout
- CLI end-to-end with mocked LLM and mocked server
- Edge cases: empty prompts, extremely long sequences, invalid command references  
**Dependencies:** WI-2, WI-3, WI-4  
**Deliverable:** `tests/test_skill_generator.py`, `tests/test_skill_uploader.py`, `tests/test_skill_cli.py`

### WI-6: Documentation
**Owner:** Jinx (with Vi)  
**Effort:** 2 hours  
**Description:** User-facing docs for the skill: how to install, configure LLM API key, run, example prompts. Add section to README and/or dedicated `docs/recording-skill.md`.  
**Dependencies:** WI-4  
**Deliverable:** `docs/recording-skill.md`, README update

### WI-7 (Optional): MCP Tool Integration
**Owner:** Vi (Backend)  
**Effort:** 3-4 hours  
**Description:** Package the skill as an MCP server so LLM CLIs (Copilot, etc.) can call it as a tool. Register in `.copilot/mcp-config.json`.  
**Dependencies:** WI-4  
**Deliverable:** `skill/mcp_server.py`, updated `.copilot/mcp-config.json`

---

## 5. Dependency Graph

```
WI-1 (Command Vocabulary)
  └─► WI-2 (Generator) ──┐
                          ├─► WI-4 (CLI) ──► WI-6 (Docs)
WI-3 (Upload Client) ────┘                     │
                                                └─► WI-7 (MCP, optional)
WI-5 (Tests) depends on WI-2, WI-3, WI-4
```

---

## 6. Key Design Decisions Required

### Decision 1: LLM Provider
**Options:**
- **A) OpenAI (GPT-4o-mini)** — Widely available, cheap, good at structured JSON output, `response_format: json_object` mode
- **B) Anthropic (Claude Haiku)** — Good at following structured prompts, XML/JSON output
- **C) Configurable** — Support multiple providers via env var (`MR_PUMPKIN_LLM_PROVIDER=openai|anthropic`)

**Recommendation:** Option C (configurable) with OpenAI as default. The generator module should abstract the LLM call behind an interface, making provider changes a config change, not a code change.

### Decision 2: Where the Skill Lives
**Options:**
- **A) `skill/` package in the mr-pumpkin repo** — Co-located, shares timeline.py imports
- **B) Separate repository** — Independent release cycle, pip-installable
- **C) Single file** — Minimal footprint, easy distribution

**Recommendation:** Option A (`skill/` package in-repo). The skill must import `Timeline` and `TimelineEntry` from `timeline.py` for validation. Keeping it co-located avoids version drift and circular dependencies. Can always be extracted later if it grows.

### Decision 3: JSON Validation Strategy
**Options:**
- **A) Parse-and-validate** — Use `Timeline.from_dict()` to validate LLM output, reject if invalid
- **B) Parse-repair-validate** — Attempt to fix common LLM errors (wrong key names, missing fields) before validation
- **C) Schema-constrained generation** — Use OpenAI structured output or similar to force valid JSON

**Recommendation:** Option B (parse-repair-validate). LLMs commonly make small errors like using `timestamp_ms` instead of `time_ms` (our own docs have this inconsistency!). A repair layer that normalizes known aliases before validation will dramatically improve success rate.

### Decision 4: API Key Management
**Recommendation:** Environment variable (`MR_PUMPKIN_LLM_API_KEY` or provider-specific like `OPENAI_API_KEY`). No keys in config files or source code. The CLI should error clearly if no key is found.

---

## 7. Risks and Open Questions

### Risks
1. **LLM output quality** — LLMs may generate plausible but invalid timelines (wrong command names, impossible arg values). Mitigation: strong system prompt + validation layer + repair heuristics.
2. **Timing realism** — LLMs have no concept of how long animations "feel." A blink at 50ms would be invisible; 5000ms would be absurdly slow. Mitigation: include timing guidelines and examples in system prompt.
3. **Cost** — Each generation call costs money. Mitigation: use efficient models (GPT-4o-mini, Haiku), cache common patterns, keep prompts concise.
4. **API dependency** — Feature requires external API access. Mitigation: support local models (ollama) as future provider option.

### Open Questions (Need Mike's Input)
1. **LLM provider preference?** Does Mike have an existing OpenAI or Anthropic key/account?
2. **Scope of "skill"?** Is this just a CLI tool, or should it integrate as an MCP tool for Copilot?
3. **Playback after upload?** Should the skill automatically trigger `play <filename>` after upload, or just upload and let the user play manually?
4. **Overwrite behavior?** If a recording with the same name exists, should the skill error, prompt, or auto-rename?

---

## 8. Recommended Starting Point

**Build WI-1 (Command Vocabulary) and WI-2 (Generator) first.**

The generator is the core value of this feature — everything else (upload, CLI, tests) is plumbing around existing patterns. Start with:

1. Create the `skill/` package directory
2. Build the command vocabulary reference (this is also useful documentation)
3. Build the generator with a hardcoded OpenAI call, validate output against `Timeline.from_dict()`
4. Test manually with real prompts to tune the system prompt

Once the generator reliably produces valid JSON, WI-3 (uploader) and WI-4 (CLI) can be built quickly since they reuse existing protocol patterns.

**Parallel work:** Mylo can write test stubs (WI-5) against the generator interface while Vi builds the implementation (WI-2), following the same test-first pattern used for timeline and projection mapping.

---

## 9. Ekko's Role

Ekko (Graphics) has limited direct work here, but provides critical domain knowledge:
- **Timing guidelines** for the system prompt — how long do expression transitions take? What's a natural blink duration? How fast should gaze movements be?
- **Animation choreography review** — review generated timelines for visual quality
- **Expression combination advice** — what combinations look good vs. glitchy (e.g., raising eyebrows during scared expression)

This knowledge should be captured in WI-1 (command vocabulary) as timing annotations.
