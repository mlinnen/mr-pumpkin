### 2026-03-02: User directive — LLM provider for issue #39 skill

**By:** Mike Linnen (via Copilot)
**What:** Use Gemini as the initial LLM provider for the mr-pumpkin recording skill (issue #39). Design the provider layer to be pluggable so other providers (OpenAI, Anthropic, local models) can be swapped in later without rearchitecting.
**Why:** User decision — captured for team memory and to guide Vi's implementation of the generator module.
