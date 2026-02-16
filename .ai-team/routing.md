# Work Routing — Mr. Pumpkin Squad

| Domain | Primary Agent | Secondary | Example Tasks |
|--------|---------------|-----------|----------------|
| **Architecture & Vision** | Jinx (Lead) | — | Project structure, decisions, code review, expression logic design |
| **Graphics & Animation** | Ekko (Graphics Dev) | — | Rendering, animation frames, visual effects, UI layout |
| **Core Engine & Commands** | Vi (Backend Dev) | — | State management, command parsing, expression state machines |
| **Testing & Quality** | Mylo (Tester) | Jinx | Test coverage, expression validation, edge cases, quality gates |
| **Memory & Decisions** | Scribe | — | Session logs, decision merging, team context, history |
| **Work Queue & Pipeline** | Ralph | — | Issue triage, work assignments, backlog monitoring |

---

## Default Routing Rules

1. **Multi-domain tasks:** Spawn Lead (Jinx) first for architecture decision, then parallel fan-out to domain experts.
2. **Graphics-heavy work:** Route to Ekko; if testing needed, loop in Mylo.
3. **Backend/state work:** Route to Vi; Mylo writes tests in parallel.
4. **Triage/review:** Lead (Jinx) makes final call.
5. **Documentation:** Any agent can do it; Scribe consolidates.
