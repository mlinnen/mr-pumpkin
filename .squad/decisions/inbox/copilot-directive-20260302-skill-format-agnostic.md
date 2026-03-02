### 2026-03-02: User directive — skill format for issue #39

**By:** Mike Linnen (via Copilot)
**What:** The recording skill must be AI-agnostic (not tied to Copilot MCP or any single platform). It is a user-facing skill for the mr-pumpkin application — end users invoke it to generate and upload animations. It is NOT a squad developer tool.
**Why:** User decision — defines the packaging and audience for the skill. Influences how the CLI entry point is structured (standalone Python tool, invokable by any AI assistant or human user directly).
