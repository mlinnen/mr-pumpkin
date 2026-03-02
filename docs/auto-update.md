# Auto-Update Guide

## Overview

Mr. Pumpkin includes automated update scripts that simplify keeping your installation up-to-date. The scripts check for new releases on GitHub and handle the entire update process automatically.

## Architecture

### Why External Scripts?

The update system uses external scripts (`update.sh` for Unix-like systems, `update.ps1` for Windows) rather than building update logic into the pumpkin_face.py application itself. This design provides:

- **Separation of concerns**: Pumpkin face remains a focused graphics application
- **Reliability**: Update script runs independently of the application
- **Simplicity**: Can be scheduled via system tools (cron, Task Scheduler)
- **Safety**: Graceful process handling prevents corruption

### Update Workflow (5 Phases)

1. **Check**: Compare local VERSION file against latest GitHub release tag
2. **Download**: Fetch new release ZIP if a newer version is available
3. **Stop**: Gracefully stop pumpkin_face.py if running (preserves process arguments)
4. **Deploy**: Extract ZIP, validate files, copy to installation directory, update dependencies
5. **Restart**: Launch pumpkin_face.py if it was running before the update

### Version Detection

- **Local version**: Read from `VERSION` file in installation directory
- **Remote version**: Fetched from GitHub API endpoint: `https://api.github.com/repos/mlinnen/mr-pumpkin/releases/latest`
- **Comparison**: Semantic versioning (major.minor.patch)

### Download Strategy

The scripts prefer the GitHub CLI (`gh`) when available, with fallback to direct URL download:

1. **First attempt**: `gh release download` (handles authentication and retries)
2. **Fallback**: Direct HTTPS download from GitHub release URL

## Platform-Specific Setup

### Linux/macOS/Raspberry Pi

#### Manual Execution

```bash
cd /path/to/mr-pumpkin
./update.sh
```

The script will:
- Set PATH for cron job compatibility
- Use `pgrep` to detect running pumpkin_face.py process
- Capture original command line arguments (monitor number, --window flag)
- Stop process with SIGTERM (5-second timeout, then SIGKILL if needed)
- Extract release ZIP and validate structure
- Copy files to installation directory
- Run `pip install -r requirements.txt` to update dependencies
- Restart with original arguments: `nohup python pumpkin_face.py [args] > /dev/null 2>&1 &`

#### Cron Job Setup

Edit your crontab:
```bash
crontab -e
```

**Daily at 3 AM:**
```cron
0 3 * * * /absolute/path/to/mr-pumpkin/update.sh
```

**Every 6 hours:**
```cron
0 */6 * * * /absolute/path/to/mr-pumpkin/update.sh
```

**Every Sunday at midnight:**
```cron
0 0 * * 0 /absolute/path/to/mr-pumpkin/update.sh
```

**Important for cron jobs:**
- Use absolute paths
- Set `INSTALL_DIR` environment variable if needed
- Script automatically sets PATH for compatibility

Example with environment variable:
```cron
INSTALL_DIR=/home/pi/mr-pumpkin
0 3 * * * /home/pi/mr-pumpkin/update.sh
```

### Windows

#### Manual Execution

```powershell
cd C:\path\to\mr-pumpkin
.\update.ps1
```

The script will:
- Use WMI to detect running pumpkin_face.py process by command line
- Capture original command line arguments
- Stop process with `Stop-Process` (5-second timeout, then `-Force` if needed)
- Extract release ZIP using `Expand-Archive`
- Copy files to installation directory
- Run `pip install -r requirements.txt` to update dependencies
- Restart with hidden window: `Start-Process python -ArgumentList "pumpkin_face.py [args]" -WindowStyle Hidden`

#### Task Scheduler Setup (PowerShell)

Create a scheduled task:
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\path\to\mr-pumpkin\update.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "MrPumpkinAutoUpdate" -Description "Daily check for Mr. Pumpkin updates"
```

**Other scheduling options:**

Weekly on Sunday at midnight:
```powershell
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 12am
```

Every 6 hours:
```powershell
$trigger = New-ScheduledTaskTrigger -Once -At 12am -RepetitionInterval (New-TimeSpan -Hours 6)
```

#### Task Scheduler Setup (GUI)

1. Open Task Scheduler (Win+R → `taskschd.msc`)
2. Click "Create Basic Task"
3. Name: "Mr Pumpkin Auto Update"
4. Description: "Automated version check and update"
5. Trigger: Choose frequency (Daily, Weekly, etc.)
6. Time: Set preferred time (e.g., 3:00 AM)
7. Action: "Start a program"
8. Program/script: `powershell.exe`
9. Add arguments: `-ExecutionPolicy Bypass -File "C:\path\to\mr-pumpkin\update.ps1"`
10. Finish and test the task

**Optional settings (in Task Properties):**
- General → Run whether user is logged on or not
- Settings → Allow task to be run on demand
- Settings → If task fails, restart every 1 hour

## Configuration

### Environment Variables

**INSTALL_DIR** - Override the installation directory:

Linux/macOS/Raspberry Pi:
```bash
export INSTALL_DIR=/custom/path/to/mr-pumpkin
./update.sh
```

Windows:
```powershell
$env:INSTALL_DIR = "C:\custom\path\to\mr-pumpkin"
.\update.ps1
```

For cron jobs:
```cron
INSTALL_DIR=/custom/path
0 3 * * * /custom/path/mr-pumpkin/update.sh
```

For Task Scheduler, set environment variable system-wide or in the script wrapper.

## Log File

All update operations are logged to `mr-pumpkin-update.log` in the installation directory.

### Log Format

```
YYYY-MM-DD HH:MM:SS | PHASE | Message
```

### Example Log

```
2026-03-02 03:00:01 | ========== Auto-update check started ==========
2026-03-02 03:00:01 | CHECK | Reading local version...
2026-03-02 03:00:01 | CHECK | Local version: 0.5.4
2026-03-02 03:00:01 | CHECK | Fetching latest release from GitHub...
2026-03-02 03:00:02 | CHECK | Latest version: 0.6.0
2026-03-02 03:00:02 | CHECK | Update available: 0.5.4 → 0.6.0
2026-03-02 03:00:03 | Downloading version 0.6.0...
2026-03-02 03:00:05 | Downloaded successfully
2026-03-02 03:00:05 | STOP | Found running process (PID: 1234)
2026-03-02 03:00:05 | STOP | Command line args: 1 --window
2026-03-02 03:00:05 | Stopping process 1234...
2026-03-02 03:00:06 | Process stopped gracefully
2026-03-02 03:00:06 | Extracting release...
2026-03-02 03:00:07 | Deploying files to /home/user/mr-pumpkin...
2026-03-02 03:00:08 | Installing Python dependencies...
2026-03-02 03:00:12 | Deployment complete
2026-03-02 03:00:12 | Starting pumpkin_face.py with args: 1 --window
2026-03-02 03:00:14 | Process started (PID: 5678)
2026-03-02 03:00:14 | SUCCESS | Updated to version 0.6.0
2026-03-02 03:00:14 | ========== Auto-update complete ==========
```

### When Already Up-to-Date

```
2026-03-02 03:00:01 | ========== Auto-update check started ==========
2026-03-02 03:00:01 | CHECK | Reading local version...
2026-03-02 03:00:01 | CHECK | Local version: 0.6.0
2026-03-02 03:00:01 | CHECK | Fetching latest release from GitHub...
2026-03-02 03:00:02 | CHECK | Latest version: 0.6.0
2026-03-02 03:00:02 | CHECK | Already up-to-date
2026-03-02 03:00:02 | ========== Auto-update check complete ==========
```

## Troubleshooting

### Update Check Fails

**Symptom**: `ERROR: Could not fetch latest version from GitHub`

**Possible causes:**
- No internet connection
- GitHub API rate limit exceeded
- GitHub API temporarily unavailable

**Solutions:**
1. Check internet connection
2. Wait 10 minutes and try again (rate limit resets)
3. Install GitHub CLI (`gh`) for authenticated requests (higher rate limits)

### Download Fails

**Symptom**: `ERROR: Download failed or file is empty`

**Possible causes:**
- Network interruption
- Release ZIP not yet available (rare)
- Insufficient disk space

**Solutions:**
1. Check available disk space
2. Manually download from GitHub: https://github.com/mlinnen/mr-pumpkin/releases
3. Try again after a few minutes

### Deployment Fails

**Symptom**: `ERROR: Missing required file: pumpkin_face.py`

**Possible causes:**
- Corrupted ZIP download
- Incomplete release package

**Solutions:**
1. Delete the log file and try again (forces fresh download)
2. Manually download and extract the release
3. Report issue on GitHub if problem persists

### Process Won't Stop

**Symptom**: `Force killing process...` in log

**Possible causes:**
- Application is hung
- Resource lock (file I/O in progress)

**Solutions:**
- This is handled automatically (force kill after 5 seconds)
- Check if process actually stopped: `ps aux | grep pumpkin` (Linux) or `tasklist | findstr python` (Windows)
- If orphaned process remains, manually kill it

### Process Won't Restart

**Symptom**: `WARNING: Failed to restart process`

**Possible causes:**
- Python not in PATH (cron job environment)
- Missing dependencies
- Port 5000/5001 already in use

**Solutions:**
1. Check log file for specific error
2. Manually start: `python pumpkin_face.py [args]`
3. Verify Python and pip are in system PATH
4. For cron jobs, set PATH explicitly in script or crontab

### Permission Denied

**Linux/macOS symptom**: `Permission denied` when running `./update.sh`

**Solution:**
```bash
chmod +x update.sh
```

**Windows symptom**: Script execution blocked by policy

**Solution:**
```powershell
powershell -ExecutionPolicy Bypass -File update.ps1
```

Or set execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Manual Rollback

If an update causes issues, you can manually roll back to a previous version:

### Step 1: Stop pumpkin_face.py

Linux/macOS:
```bash
pkill -f pumpkin_face.py
```

Windows:
```powershell
Stop-Process -Name python -Force
```

### Step 2: Download Previous Release

Visit https://github.com/mlinnen/mr-pumpkin/releases and download the desired version ZIP.

### Step 3: Extract and Deploy

Linux/macOS/Raspberry Pi:
```bash
unzip mr-pumpkin-v0.5.4.zip
cd mr-pumpkin-v0.5.4
cp -rf * /path/to/installation/
```

Windows:
```powershell
Expand-Archive mr-pumpkin-v0.5.4.zip
cd mr-pumpkin-v0.5.4
Copy-Item * C:\path\to\installation\ -Recurse -Force
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Restart

```bash
python pumpkin_face.py
```

## Security Considerations

### HTTPS Enforcement

All downloads use HTTPS to prevent man-in-the-middle attacks. The scripts reject HTTP redirects.

### GitHub CLI Authentication

For better security and higher API rate limits, install and authenticate the GitHub CLI:

```bash
# Install gh (Linux/macOS)
# Visit: https://cli.github.com/

# Install gh (Windows)
# Download from: https://cli.github.com/

# Authenticate
gh auth login
```

### Least Privilege

The update scripts run as the current user. They do NOT require root/Administrator privileges except:
- On Linux/Raspberry Pi: Initial SDL2 installation (one-time, via install.sh)

### Dependency Trust

Python dependencies are installed from PyPI using the same trust model as manual installation. The `pip install` step uses the requirements.txt from the verified GitHub release.

## Exit Codes

- **0**: Success (updated or already up-to-date)
- **1**: Failure (network error, invalid ZIP, deployment failed, etc.)

Use exit codes for monitoring:

```bash
./update.sh
if [ $? -eq 0 ]; then
    echo "Update check succeeded"
else
    echo "Update check failed"
fi
```

## GitHub API Rate Limits

**Unauthenticated requests**: 60 per hour per IP address  
**Authenticated requests (gh CLI)**: 5,000 per hour

If running update checks frequently (e.g., every 15 minutes), authenticate with `gh` to avoid rate limiting.

## Support

For issues with the auto-update system:

1. Check the log file: `mr-pumpkin-update.log`
2. Review troubleshooting section above
3. Open an issue on GitHub: https://github.com/mlinnen/mr-pumpkin/issues
4. Include your log file (sanitize any sensitive paths)
