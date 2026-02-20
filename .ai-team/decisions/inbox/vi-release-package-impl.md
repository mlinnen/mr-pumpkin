### 2026-02-20: Release Package Implementation — ZIP with Cross-Platform Install Scripts

**By:** Vi (Backend Dev)

**Issue:** #3 — create a release package

**What:** Implemented ZIP-based distribution system with shell install scripts for cross-platform deployment.

**Implementation:**

1. **Package Builder** (`scripts/package_release.py`):
   - Python script using zipfile module
   - Reads VERSION file dynamically
   - Creates `mr-pumpkin-v{VERSION}.zip` with nested folder structure
   - Includes: source files, docs/, LICENSE, requirements.txt, install scripts
   - Excludes: .ai-team/, .github/, .git/, __pycache__/, .copilot/

2. **Install Scripts**:
   - `install.sh` (Linux/macOS/Raspberry Pi):
     - Detects OS via `$OSTYPE` and `/proc/device-tree/model`
     - On Raspberry Pi/Debian/Ubuntu: installs SDL2 system libs via apt-get
     - Runs `pip install -r requirements.txt` (global, not venv)
   - `install.ps1` (Windows):
     - PowerShell with error handling
     - Runs pip install with colored output

3. **CI/CD Integration** (`.github/workflows/squad-release.yml`):
   - After tests pass: `python scripts/package_release.py`
   - Attaches ZIP to GitHub Release: `gh release create ... {zipfile}`

4. **Dependency Pinning** (`requirements.txt`):
   - Changed from unpinned (`pygame`, `pytest`) to range constraints
   - `pygame>=2.0.0,<3.0.0` and `pytest>=7.0.0,<9.0.0`
   - Allows patch/minor updates, blocks breaking major versions

5. **Documentation** (`README.md`):
   - Added "Option 1: Download Release Package" section at top of Installation
   - Shows how to unzip and run install scripts
   - Kept "Option 2: Install from Source" below
   - Added SDL2 dependency note for Raspberry Pi/Linux

**Why:**

- **Raspberry Pi target:** Requires SDL2 system libraries before pygame installs. Shell script automates this.
- **Simple distribution:** ZIP archive is simpler than PyPI packaging for this use case (no wheel building, no setup.py complexity).
- **Cross-platform:** Python packaging script works on all platforms; shell scripts are idiomatic for their target OS.
- **Version management:** Single VERSION file at repo root is simpler than package.json or git-based versioning.
- **User experience:** "Download ZIP, unzip, run install script" is the simplest possible workflow for non-Python users.
- **CI/CD automation:** Building ZIP in GitHub Actions ensures every release is consistent and reproducible.

**Raspberry Pi SDL2 dependencies:** Required for Pi 3, 4, and 5:
```
libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

**Owner override:** Initial decision excluded docs/ folder. Owner explicitly requested inclusion of docs/ in release package.
