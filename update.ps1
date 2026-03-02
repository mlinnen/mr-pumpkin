# Mr. Pumpkin Auto-Update Script (Windows)
# Checks for new releases on GitHub and updates the installation automatically
# Usage: .\update.ps1
# Exit codes: 0 = success (updated or already up-to-date), 1 = failure

$ErrorActionPreference = "Stop"

# Configuration
$REPO = "mlinnen/mr-pumpkin"
$INSTALL_DIR = if ($env:INSTALL_DIR) { $env:INSTALL_DIR } else { Get-Location }
$LOG_FILE = Join-Path $INSTALL_DIR "mr-pumpkin-update.log"
$TEMP_DIR = Join-Path $env:TEMP "mr-pumpkin-update-$(Get-Random)"

# Create temp directory
New-Item -ItemType Directory -Path $TEMP_DIR -Force | Out-Null

# Cleanup function
function Cleanup {
    if (Test-Path $TEMP_DIR) {
        Remove-Item -Recurse -Force $TEMP_DIR -ErrorAction SilentlyContinue
    }
}

# Register cleanup on exit
trap { Cleanup }

# Log message with timestamp
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp | $Message"
    Write-Host $logMessage
    Add-Content -Path $LOG_FILE -Value $logMessage
}

# Get local version
function Get-LocalVersion {
    $versionFile = Join-Path $INSTALL_DIR "VERSION"
    if (Test-Path $versionFile) {
        return (Get-Content $versionFile).Trim()
    }
    return "0.0.0"
}

# Get remote version from GitHub API
function Get-RemoteVersion {
    try {
        # Try using gh CLI first
        if (Get-Command gh -ErrorAction SilentlyContinue) {
            $ghOutput = gh release view --repo $REPO --json tagName -q .tagName 2>$null
            if ($ghOutput) {
                return $ghOutput -replace '^v', ''
            }
        }
        
        # Fallback to REST API
        $url = "https://api.github.com/repos/$REPO/releases/latest"
        $response = Invoke-RestMethod -Uri $url -ErrorAction Stop
        return $response.tag_name -replace '^v', ''
    }
    catch {
        return $null
    }
}

# Compare semantic versions (returns $true if update needed)
function Compare-Versions {
    param(
        [string]$Current,
        [string]$Latest
    )
    
    if ($Current -eq $Latest) {
        return $false
    }
    
    # Split versions
    $currentParts = $Current -split '\.' | ForEach-Object { 
        # Extract numeric part only (remove pre-release suffix)
        if ($_ -match '^(\d+)') { [int]$matches[1] } else { 0 }
    }
    $latestParts = $Latest -split '\.' | ForEach-Object { 
        if ($_ -match '^(\d+)') { [int]$matches[1] } else { 0 }
    }
    
    # Ensure we have 3 parts
    while ($currentParts.Count -lt 3) { $currentParts += 0 }
    while ($latestParts.Count -lt 3) { $latestParts += 0 }
    
    # Compare major, minor, patch
    for ($i = 0; $i -lt 3; $i++) {
        if ($latestParts[$i] -gt $currentParts[$i]) {
            return $true  # Update available
        }
        elseif ($latestParts[$i] -lt $currentParts[$i]) {
            return $false  # Local is newer
        }
    }
    
    return $false  # Versions are equal
}

# Find running pumpkin_face.py process
function Find-PumpkinProcess {
    try {
        $process = Get-WmiObject Win32_Process | Where-Object { 
            $_.CommandLine -like "*pumpkin_face.py*" 
        } | Select-Object -First 1
        
        if ($process) {
            return @{
                PID = $process.ProcessId
                CommandLine = $process.CommandLine
            }
        }
    }
    catch {
        # WMI might not be available, try Get-Process
        $processes = Get-Process python* -ErrorAction SilentlyContinue
        foreach ($proc in $processes) {
            try {
                # This won't give us command line, but at least we know python is running
                # We'll have to make a best guess
                return @{
                    PID = $proc.Id
                    CommandLine = "python pumpkin_face.py"
                }
            }
            catch {
                continue
            }
        }
    }
    
    return $null
}

# Extract arguments from command line
function Get-ProcessArgs {
    param([string]$CommandLine)
    
    # Extract args after pumpkin_face.py
    if ($CommandLine -match 'pumpkin_face\.py\s*(.*)$') {
        return $matches[1].Trim()
    }
    return ""
}

# Stop pumpkin_face.py gracefully
function Stop-Pumpkin {
    param([int]$PID)
    
    if (-not $PID) {
        return $true
    }
    
    Write-Log "Stopping process $PID..."
    
    try {
        Stop-Process -Id $PID -ErrorAction Stop
        
        # Wait up to 5 seconds for graceful exit
        for ($i = 0; $i -lt 5; $i++) {
            Start-Sleep -Seconds 1
            if (-not (Get-Process -Id $PID -ErrorAction SilentlyContinue)) {
                Write-Log "Process stopped gracefully"
                return $true
            }
        }
        
        # Force kill if still running
        if (Get-Process -Id $PID -ErrorAction SilentlyContinue) {
            Write-Log "Force killing process $PID..."
            Stop-Process -Id $PID -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
        
        return $true
    }
    catch {
        Write-Log "WARNING: Error stopping process: $_"
        return $true  # Continue anyway
    }
}

# Download release ZIP
function Download-Release {
    param([string]$Version)
    
    $zipName = "mr-pumpkin-v$Version.zip"
    $zipPath = Join-Path $TEMP_DIR $zipName
    
    Write-Log "Downloading version $Version..."
    
    try {
        # Try gh CLI first
        if (Get-Command gh -ErrorAction SilentlyContinue) {
            Push-Location $TEMP_DIR
            try {
                gh release download "v$Version" --repo $REPO --pattern $zipName 2>$null
                if (Test-Path $zipPath) {
                    Write-Log "Downloaded via gh CLI"
                    Pop-Location
                    return $zipPath
                }
            }
            finally {
                Pop-Location
            }
        }
        
        # Fallback to direct URL download
        $url = "https://github.com/$REPO/releases/download/v$Version/$zipName"
        Invoke-WebRequest -Uri $url -OutFile $zipPath -ErrorAction Stop
        
        # Verify download
        if (-not (Test-Path $zipPath) -or (Get-Item $zipPath).Length -eq 0) {
            Write-Log "ERROR: Download failed or file is empty"
            return $null
        }
        
        Write-Log "Downloaded successfully"
        return $zipPath
    }
    catch {
        Write-Log "ERROR: Download failed: $_"
        return $null
    }
}

# Deploy release files
function Deploy-Release {
    param([string]$ZipPath)
    
    Write-Log "Extracting release..."
    
    $extractDir = Join-Path $TEMP_DIR "extract"
    New-Item -ItemType Directory -Path $extractDir -Force | Out-Null
    
    try {
        Expand-Archive -Path $ZipPath -DestinationPath $extractDir -Force -ErrorAction Stop
    }
    catch {
        Write-Log "ERROR: Failed to extract ZIP: $_"
        return $false
    }
    
    # Find the extracted folder (should be mr-pumpkin-v*)
    $sourceDir = Get-ChildItem -Path $extractDir -Directory -Filter "mr-pumpkin-v*" | Select-Object -First 1
    if (-not $sourceDir) {
        Write-Log "ERROR: Could not find extracted folder"
        return $false
    }
    
    # Validate required files
    $requiredFiles = @("pumpkin_face.py", "VERSION", "requirements.txt")
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $sourceDir.FullName $file
        if (-not (Test-Path $filePath)) {
            Write-Log "ERROR: Missing required file: $file"
            return $false
        }
    }
    
    Write-Log "Deploying files to $INSTALL_DIR..."
    
    try {
        # Copy files (preserve existing user data/configs)
        Copy-Item -Path "$($sourceDir.FullName)\*" -Destination $INSTALL_DIR -Recurse -Force -ErrorAction Stop
        
        Write-Log "Installing Python dependencies..."
        Push-Location $INSTALL_DIR
        
        try {
            if (Get-Command pip -ErrorAction SilentlyContinue) {
                pip install -r requirements.txt *>> $LOG_FILE
            }
            elseif (Get-Command pip3 -ErrorAction SilentlyContinue) {
                pip3 install -r requirements.txt *>> $LOG_FILE
            }
            else {
                Write-Log "WARNING: pip not found, skipping dependency install"
            }
        }
        finally {
            Pop-Location
        }
        
        Write-Log "Deployment complete"
        return $true
    }
    catch {
        Write-Log "ERROR: Deployment failed: $_"
        return $false
    }
}

# Start pumpkin_face.py as background process
function Start-Pumpkin {
    param([string]$Args)
    
    Write-Log "Starting pumpkin_face.py with args: $Args"
    
    # Wait for file system sync
    Start-Sleep -Seconds 2
    
    try {
        # Find python command
        $pythonCmd = $null
        if (Get-Command python -ErrorAction SilentlyContinue) {
            $pythonCmd = "python"
        }
        elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
            $pythonCmd = "python3"
        }
        else {
            Write-Log "ERROR: Python not found"
            return $false
        }
        
        Push-Location $INSTALL_DIR
        
        try {
            # Build argument list
            $argList = "pumpkin_face.py"
            if ($Args) {
                $argList = "$argList $Args"
            }
            
            # Start as hidden background process
            $process = Start-Process -FilePath $pythonCmd -ArgumentList $argList -WindowStyle Hidden -PassThru
            Write-Log "Process started (PID: $($process.Id))"
            return $true
        }
        finally {
            Pop-Location
        }
    }
    catch {
        Write-Log "ERROR: Failed to start process: $_"
        return $false
    }
}

# Main workflow
function Main {
    Write-Log "========== Auto-update check started =========="
    
    try {
        # Phase 1: Check versions
        Write-Log "CHECK | Reading local version..."
        $currentVersion = Get-LocalVersion
        Write-Log "CHECK | Local version: $currentVersion"
        
        Write-Log "CHECK | Fetching latest release from GitHub..."
        $latestVersion = Get-RemoteVersion
        
        if (-not $latestVersion) {
            Write-Log "ERROR: Could not fetch latest version from GitHub"
            Cleanup
            exit 1
        }
        
        Write-Log "CHECK | Latest version: $latestVersion"
        
        if (-not (Compare-Versions -Current $currentVersion -Latest $latestVersion)) {
            Write-Log "CHECK | Already up-to-date"
            Write-Log "========== Auto-update check complete =========="
            Cleanup
            exit 0
        }
        
        Write-Log "CHECK | Update available: $currentVersion → $latestVersion"
        
        # Phase 2: Download
        $zipPath = Download-Release -Version $latestVersion
        if (-not $zipPath) {
            Write-Log "ERROR: Download failed"
            Cleanup
            exit 1
        }
        
        # Phase 3: Stop process (if running)
        $wasRunning = $false
        $processArgs = ""
        $processInfo = Find-PumpkinProcess
        
        if ($processInfo) {
            Write-Log "STOP | Found running process (PID: $($processInfo.PID))"
            $processArgs = Get-ProcessArgs -CommandLine $processInfo.CommandLine
            Write-Log "STOP | Command line args: $processArgs"
            $wasRunning = $true
            
            if (-not (Stop-Pumpkin -PID $processInfo.PID)) {
                Write-Log "ERROR: Failed to stop process"
                Cleanup
                exit 1
            }
        }
        else {
            Write-Log "STOP | No running process found"
        }
        
        # Phase 4: Deploy
        if (-not (Deploy-Release -ZipPath $zipPath)) {
            Write-Log "ERROR: Deployment failed"
            Cleanup
            exit 1
        }
        
        # Phase 5: Restart (if was running)
        if ($wasRunning) {
            if (-not (Start-Pumpkin -Args $processArgs)) {
                Write-Log "WARNING: Failed to restart process"
            }
        }
        
        Write-Log "SUCCESS | Updated to version $latestVersion"
        Write-Log "========== Auto-update complete =========="
        Cleanup
        exit 0
    }
    catch {
        Write-Log "ERROR: Unexpected error: $_"
        Cleanup
        exit 1
    }
}

# Run main workflow
Main
