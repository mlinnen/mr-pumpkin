### 2026-02-20: Python versioning via VERSION file

**By:** Jinx  
**What:** Replaced Node.js tooling in all three GitHub Actions workflows with Python equivalents; versioning via a flat `VERSION` file at repo root.  
**Why:** This is a Python project — workflows were scaffolded for Node.js by default. `actions/setup-node`, `node --test`, and `package.json` version reads have no place here. `actions/setup-python` + `python -m pytest` + `cat VERSION` is the correct stack. The `VERSION` file is the simplest possible versioning mechanism for shell-friendly CI scripts.
