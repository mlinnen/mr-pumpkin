### 2026-02-20: .ai-team/ tracking policy
**By:** Jinx
**What:** .ai-team/ and .ai-team-templates/ are tracked on dev but NOT on preview or main. These directories are in .gitignore on preview and main. When merging dev→preview, untrack them with `git rm -r --cached .ai-team/ .ai-team-templates/` before committing the merge.
**Why:** .ai-team/ is squad internal state — it should not ship with the product.
