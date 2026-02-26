### 2026-02-26: Remove .ai-team/ guard workflow and gitignore restrictions
**By:** Jinx  
**Issue:** #40  
**What:** Removed all mechanisms preventing `.ai-team/` from being committed to `preview` and `main` branches: deleted `squad-main-guard.yml` workflow, removed `.gitignore` entries, removed validation check from `squad-preview.yml`.  
**Why:** Squad team state (decisions, histories, routing rules, agent charters) should flow through normal git workflow like any other project directory. This preserves team evolution history and shares it across branches. The original guard design kept squad coordination files off release branches, but this prevented team knowledge from being versioned and distributed with the codebase.  
**Impact:** `.ai-team/` is now fully git-tracked. Future merges to `preview` and `main` will include squad state files. Release artifacts may need explicit exclusion patterns if `.ai-team/` should not ship to end users.
