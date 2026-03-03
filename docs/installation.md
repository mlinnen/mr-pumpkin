---
layout: page
title: Installation & Usage
permalink: /installation
description: How to install Mr. Pumpkin and set it up to run as a service.
---

# Installing Mr. Pumpkin as a Service

This guide shows how to set up Mr. Pumpkin to run automatically as a background service on Linux (Raspberry Pi) or Windows, so it starts on boot and runs continuously.

## Before You Begin

### Install Dependencies First

Before setting up the service, run the included installation script to install Python dependencies and system libraries (SDL2):

**Linux/Raspberry Pi:**
```bash
cd /path/to/mr-pumpkin
chmod +x install.sh
./install.sh
```

**Windows:**
```powershell
cd C:\path\to\mr-pumpkin
powershell -ExecutionPolicy Bypass -File install.ps1
```

These scripts install everything Mr. Pumpkin needs to run:
- Python packages (pygame, websockets, pytest)
- SDL2 graphics libraries (Linux only — Windows uses pygame's bundled SDL2)

### Test It First

Before creating a service, verify Mr. Pumpkin runs correctly:

```bash
python pumpkin_face.py
```

You should see a fullscreen pumpkin face. Press **ESC** to exit. If it works, proceed to service setup below.

---

## Linux / Raspberry Pi — systemd Service

### 1. Create the Service File

Create a systemd service unit file at `/etc/systemd/system/mr-pumpkin.service`:

```bash
sudo nano /etc/systemd/system/mr-pumpkin.service
```

Paste the following configuration (adjust paths to match your installation):

```ini
[Unit]
Description=Mr. Pumpkin Animated Face
After=network.target graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/mr-pumpkin
Environment="DISPLAY=:0"
ExecStart=/usr/bin/python3 /home/pi/mr-pumpkin/pumpkin_face.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
```

**Configuration Notes:**

- **User**: Replace `pi` with your username
- **WorkingDirectory**: Full path to your Mr. Pumpkin installation folder
- **ExecStart**: Full path to `python3` (find with `which python3`) and full path to `pumpkin_face.py`
- **DISPLAY=:0**: Required for Raspberry Pi with desktop environment (tells SDL2 where to display graphics)
- **graphical.target**: Ensures service starts after the display is ready

**For headless systems** (Raspberry Pi Lite without desktop):
- You'll need to configure a framebuffer (beyond this guide's scope)
- Or run a minimal X server with `startx`

**Optional flags in ExecStart:**
- `--window`: Run in windowed mode (useful for debugging)
- `1` or `2`: Specify monitor number for multi-display setups

### 2. Enable and Start the Service

Reload systemd to recognize the new service:

```bash
sudo systemctl daemon-reload
```

Enable the service to start on boot:

```bash
sudo systemctl enable mr-pumpkin
```

Start the service immediately:

```bash
sudo systemctl start mr-pumpkin
```

### 3. Check Service Status

Verify the service is running:

```bash
sudo systemctl status mr-pumpkin
```

You should see:
- **Active: active (running)** in green
- Recent log output showing "Socket server listening on port 5000"

### 4. View Logs

If the service fails or you need to troubleshoot:

```bash
# Recent logs
sudo journalctl -u mr-pumpkin -n 50

# Follow live logs
sudo journalctl -u mr-pumpkin -f
```

### 5. Stop or Disable the Service

```bash
# Stop the service (temporary)
sudo systemctl stop mr-pumpkin

# Disable auto-start on boot
sudo systemctl disable mr-pumpkin
```

---

## Windows — Task Scheduler (Simplest Method)

This approach runs Mr. Pumpkin at system startup using Windows Task Scheduler. It's simpler than installing a Windows Service and works well for most users.

### 1. Create a PowerShell Startup Script

Create a file `start-pumpkin.ps1` in your Mr. Pumpkin folder:

```powershell
# Navigate to Mr. Pumpkin directory
Set-Location "C:\mr-pumpkin"

# Start Mr. Pumpkin (fullscreen on default monitor)
python pumpkin_face.py
```

**Optional variations:**
- For windowed mode: `python pumpkin_face.py --window`
- For specific monitor: `python pumpkin_face.py 1`

### 2. Register a Scheduled Task

Open PowerShell **as Administrator** and run:

```powershell
$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File C:\mr-pumpkin\start-pumpkin.ps1" `
    -WorkingDirectory "C:\mr-pumpkin"

$Trigger = New-ScheduledTaskTrigger -AtStartup

$Principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName "MrPumpkin" `
    -Action $Action `
    -Trigger $Trigger `
    -Principal $Principal `
    -Description "Start Mr. Pumpkin animated face at system startup"
```

**Configuration Notes:**

- **-UserId**: Uses your current username. Change if running under a different account.
- **-LogonType Interactive**: Allows graphical display (required for pygame/SDL2).
- **-RunLevel Highest**: Runs with elevated privileges (may be needed for display access).
- Replace `C:\mr-pumpkin` with your actual installation path.

### 3. Verify the Task

Open **Task Scheduler** (search in Start menu):
1. Navigate to "Task Scheduler Library"
2. Find "MrPumpkin" in the task list
3. Right-click → **Properties** to review settings
4. Right-click → **Run** to test immediately

The pumpkin face should launch. Press **ESC** to close it.

### 4. Reboot Test

Restart your computer. Mr. Pumpkin should start automatically after login.

### 5. Manage the Task

```powershell
# Disable auto-start
Disable-ScheduledTask -TaskName "MrPumpkin"

# Re-enable auto-start
Enable-ScheduledTask -TaskName "MrPumpkin"

# Remove task completely
Unregister-ScheduledTask -TaskName "MrPumpkin" -Confirm:$false
```

---

## Windows — NSSM (Advanced: True Windows Service)

For users who want Mr. Pumpkin to run as a proper Windows Service (background process, no user login required), use [NSSM (Non-Sucking Service Manager)](https://nssm.cc/).

### 1. Download and Install NSSM

1. Download NSSM from [https://nssm.cc/download](https://nssm.cc/download)
2. Extract the ZIP file
3. Copy `nssm.exe` (from `win64` or `win32` folder) to `C:\Windows\System32\`

### 2. Install the Service

Open PowerShell **as Administrator**:

```powershell
nssm install MrPumpkin "C:\Python311\python.exe" "C:\mr-pumpkin\pumpkin_face.py"
```

**Adjust paths:**
- `C:\Python311\python.exe`: Path to your Python executable (find with `where python`)
- `C:\mr-pumpkin\pumpkin_face.py`: Path to your Mr. Pumpkin installation

### 3. Configure Service Parameters

```powershell
# Set working directory
nssm set MrPumpkin AppDirectory "C:\mr-pumpkin"

# Set startup type (automatic)
nssm set MrPumpkin Start SERVICE_AUTO_START

# Set display name
nssm set MrPumpkin DisplayName "Mr. Pumpkin Animated Face"

# Set description
nssm set MrPumpkin Description "Animated pumpkin face for projection mapping"
```

**Optional flags:**
```powershell
# Windowed mode
nssm set MrPumpkin AppParameters "pumpkin_face.py --window"

# Specific monitor
nssm set MrPumpkin AppParameters "pumpkin_face.py 1"
```

### 4. Start the Service

```powershell
nssm start MrPumpkin
```

### 5. Check Service Status

```powershell
# Via NSSM
nssm status MrPumpkin

# Via Windows Services
Get-Service MrPumpkin
```

Or open **Services** app (search in Start menu) and find "Mr. Pumpkin Animated Face".

### 6. View Logs

NSSM redirects output to log files. Configure log paths:

```powershell
nssm set MrPumpkin AppStdout "C:\mr-pumpkin\logs\output.log"
nssm set MrPumpkin AppStderr "C:\mr-pumpkin\logs\error.log"
```

Create the logs folder first:
```powershell
mkdir C:\mr-pumpkin\logs
```

### 7. Stop or Remove the Service

```powershell
# Stop the service
nssm stop MrPumpkin

# Remove the service completely
nssm remove MrPumpkin confirm
```

---

## Troubleshooting

### "No display available" or "SDL could not initialize"

**Linux/Raspberry Pi:**
- Ensure `DISPLAY=:0` is set in the systemd service file
- Verify X server is running: `echo $DISPLAY` (should show `:0` or similar)
- For headless systems, configure a virtual framebuffer or run a minimal X server

**Windows:**
- Ensure Task Scheduler uses **Interactive** logon type (not batch/service)
- If using NSSM, the service may not have access to the desktop (limitation of background services)
- Consider Task Scheduler method for graphical apps like Mr. Pumpkin

### Service starts but nothing displays

- **Monitor number**: If you have multiple displays, specify the correct monitor:
  - Systemd: `ExecStart=/usr/bin/python3 /path/to/pumpkin_face.py 1`
  - Task Scheduler: Update `start-pumpkin.ps1` to `python pumpkin_face.py 1`
- **Fullscreen mode**: The face runs fullscreen by default. Switch to `--window` mode for testing.

### "Address already in use" (port 5000)

Another Mr. Pumpkin instance is already running:
- **Linux**: `sudo systemctl stop mr-pumpkin`
- **Windows**: `Stop-ScheduledTask -TaskName "MrPumpkin"` or kill the process

### Service won't start after reboot

**Linux:**
- Check dependencies: `WantedBy=graphical.target` ensures graphical environment is ready
- Verify service is enabled: `sudo systemctl is-enabled mr-pumpkin` (should return "enabled")

**Windows:**
- Task Scheduler: Ensure trigger is set to **At startup** (not "At log on")
- NSSM: Check startup type is `SERVICE_AUTO_START`

---

## What's Next?

- **Test remote control**: Use `client_example.py` to send commands:
  ```bash
  python client_example.py
  ```
- **Automated updates**: See [auto-update.md](auto-update.md) to keep Mr. Pumpkin current
- **Build custom clients**: See [building-a-client.md](building-a-client.md) to create your own control software

---

## Summary

You've now configured Mr. Pumpkin to run automatically as a service:
- **Linux/Raspberry Pi**: systemd service with `graphical.target` dependency
- **Windows**: Task Scheduler (simplest) or NSSM (advanced service)

The pumpkin face will start on boot and listen for commands on **TCP port 5000** and **WebSocket port 5001**.
