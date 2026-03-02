#!/bin/bash
# Mr. Pumpkin Auto-Update Script (Linux/macOS/Raspberry Pi)
# Checks for new releases on GitHub and updates the installation automatically
# Usage: ./update.sh
# Exit codes: 0 = success (updated or already up-to-date), 1 = failure

set -e

# Configuration
REPO="mlinnen/mr-pumpkin"
INSTALL_DIR="${INSTALL_DIR:-$(pwd)}"
LOG_FILE="$INSTALL_DIR/mr-pumpkin-update.log"
TEMP_DIR=$(mktemp -d /tmp/mr-pumpkin-update.XXXXXX)

# Set PATH for cron job compatibility
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Cleanup on exit
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Log message with timestamp
log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp | $message" | tee -a "$LOG_FILE"
}

# Get local version
get_local_version() {
    if [ -f "$INSTALL_DIR/VERSION" ]; then
        cat "$INSTALL_DIR/VERSION" | tr -d '[:space:]'
    else
        echo "0.0.0"
    fi
}

# Get remote version from GitHub API
get_remote_version() {
    local url="https://api.github.com/repos/$REPO/releases/latest"
    
    # Try using gh CLI first
    if command -v gh &> /dev/null; then
        gh release view --repo "$REPO" --json tagName -q .tagName 2>/dev/null | sed 's/^v//' || echo ""
    # Fallback to curl with jq
    elif command -v jq &> /dev/null; then
        curl -s "$url" | jq -r .tag_name | sed 's/^v//' || echo ""
    # Fallback to curl with grep/sed
    else
        curl -s "$url" | grep -o '"tag_name": *"[^"]*"' | sed 's/"tag_name": *"v\{0,1\}//' | sed 's/"$//' || echo ""
    fi
}

# Compare semantic versions (returns 0 if update needed, 1 if not)
compare_versions() {
    local current="$1"
    local latest="$2"
    
    if [ "$current" = "$latest" ]; then
        return 1  # Already up-to-date
    fi
    
    # Split versions into arrays
    IFS='.' read -ra current_parts <<< "$current"
    IFS='.' read -ra latest_parts <<< "$latest"
    
    # Compare major, minor, patch
    for i in 0 1 2; do
        local cur=${current_parts[$i]:-0}
        local lat=${latest_parts[$i]:-0}
        
        # Remove any pre-release suffix (e.g., "1-beta" -> "1")
        cur=$(echo "$cur" | grep -o '^[0-9]*')
        lat=$(echo "$lat" | grep -o '^[0-9]*')
        
        if [ "$lat" -gt "$cur" ]; then
            return 0  # Update available
        elif [ "$lat" -lt "$cur" ]; then
            return 1  # Local is newer
        fi
    done
    
    return 1  # Versions are equal
}

# Find running pumpkin_face.py process
find_pumpkin_process() {
    # Use bracket trick to avoid matching grep itself
    local pid=$(pgrep -f "[p]ython.*pumpkin_face.py" | head -n 1)
    if [ -n "$pid" ]; then
        echo "$pid"
    fi
}

# Get command line arguments from process
get_process_args() {
    local pid="$1"
    # Extract args after pumpkin_face.py
    ps -p "$pid" -o args= | sed 's/.*pumpkin_face.py//' || echo ""
}

# Stop pumpkin_face.py gracefully
stop_pumpkin() {
    local pid="$1"
    if [ -z "$pid" ]; then
        return 0
    fi
    
    log "Stopping process $pid..."
    kill -TERM "$pid" 2>/dev/null || true
    
    # Wait up to 5 seconds for graceful exit
    for i in {1..5}; do
        if ! ps -p "$pid" > /dev/null 2>&1; then
            log "Process stopped gracefully"
            return 0
        fi
        sleep 1
    done
    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        log "Force killing process $pid..."
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
    fi
    
    return 0
}

# Download release ZIP
download_release() {
    local version="$1"
    local zip_name="mr-pumpkin-v${version}.zip"
    local zip_path="$TEMP_DIR/$zip_name"
    
    log "Downloading version $version..."
    
    # Try gh CLI first
    if command -v gh &> /dev/null; then
        cd "$TEMP_DIR"
        if gh release download "v$version" --repo "$REPO" --pattern "$zip_name" 2>/dev/null; then
            log "Downloaded via gh CLI"
            echo "$zip_path"
            return 0
        fi
    fi
    
    # Fallback to direct URL download
    local url="https://github.com/$REPO/releases/download/v${version}/${zip_name}"
    if command -v curl &> /dev/null; then
        curl -L -o "$zip_path" "$url" 2>/dev/null || return 1
    elif command -v wget &> /dev/null; then
        wget -O "$zip_path" "$url" 2>/dev/null || return 1
    else
        log "ERROR: Neither curl nor wget found"
        return 1
    fi
    
    # Verify download
    if [ ! -f "$zip_path" ] || [ ! -s "$zip_path" ]; then
        log "ERROR: Download failed or file is empty"
        return 1
    fi
    
    log "Downloaded successfully"
    echo "$zip_path"
    return 0
}

# Deploy release files
deploy_release() {
    local zip_path="$1"
    local extract_dir="$TEMP_DIR/extract"
    
    log "Extracting release..."
    mkdir -p "$extract_dir"
    
    if ! unzip -q "$zip_path" -d "$extract_dir"; then
        log "ERROR: Failed to extract ZIP"
        return 1
    fi
    
    # Find the extracted folder (should be mr-pumpkin-v*)
    local source_dir=$(find "$extract_dir" -maxdepth 1 -type d -name "mr-pumpkin-v*" | head -n 1)
    if [ -z "$source_dir" ]; then
        log "ERROR: Could not find extracted folder"
        return 1
    fi
    
    # Validate required files
    local required_files=("pumpkin_face.py" "VERSION" "requirements.txt")
    for file in "${required_files[@]}"; do
        if [ ! -f "$source_dir/$file" ]; then
            log "ERROR: Missing required file: $file"
            return 1
        fi
    done
    
    log "Deploying files to $INSTALL_DIR..."
    
    # Copy files (preserve existing user data/configs)
    cp -rf "$source_dir"/* "$INSTALL_DIR/"
    
    log "Installing Python dependencies..."
    cd "$INSTALL_DIR"
    
    if command -v pip &> /dev/null; then
        pip install -r requirements.txt >> "$LOG_FILE" 2>&1
    elif command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
    else
        log "WARNING: pip not found, skipping dependency install"
    fi
    
    log "Deployment complete"
    return 0
}

# Start pumpkin_face.py as background process
start_pumpkin() {
    local args="$1"
    
    log "Starting pumpkin_face.py with args: $args"
    
    # Wait for file system sync
    sleep 2
    
    # Find python command
    local python_cmd=""
    if command -v python &> /dev/null; then
        python_cmd="python"
    elif command -v python3 &> /dev/null; then
        python_cmd="python3"
    else
        log "ERROR: Python not found"
        return 1
    fi
    
    cd "$INSTALL_DIR"
    nohup $python_cmd pumpkin_face.py $args > /dev/null 2>&1 &
    
    log "Process started (PID: $!)"
    return 0
}

# Main workflow
main() {
    log "========== Auto-update check started =========="
    
    # Phase 1: Check versions
    log "CHECK | Reading local version..."
    local current_version=$(get_local_version)
    log "CHECK | Local version: $current_version"
    
    log "CHECK | Fetching latest release from GitHub..."
    local latest_version=$(get_remote_version)
    
    if [ -z "$latest_version" ]; then
        log "ERROR: Could not fetch latest version from GitHub"
        exit 1
    fi
    
    log "CHECK | Latest version: $latest_version"
    
    if ! compare_versions "$current_version" "$latest_version"; then
        log "CHECK | Already up-to-date"
        log "========== Auto-update check complete =========="
        exit 0
    fi
    
    log "CHECK | Update available: $current_version → $latest_version"
    
    # Phase 2: Download
    local zip_path=$(download_release "$latest_version")
    if [ $? -ne 0 ] || [ -z "$zip_path" ]; then
        log "ERROR: Download failed"
        exit 1
    fi
    
    # Phase 3: Stop process (if running)
    local was_running=0
    local process_args=""
    local pid=$(find_pumpkin_process)
    
    if [ -n "$pid" ]; then
        log "STOP | Found running process (PID: $pid)"
        process_args=$(get_process_args "$pid")
        log "STOP | Command line args: $process_args"
        was_running=1
        
        if ! stop_pumpkin "$pid"; then
            log "ERROR: Failed to stop process"
            exit 1
        fi
    else
        log "STOP | No running process found"
    fi
    
    # Phase 4: Deploy
    if ! deploy_release "$zip_path"; then
        log "ERROR: Deployment failed"
        exit 1
    fi
    
    # Phase 5: Restart (if was running)
    if [ $was_running -eq 1 ]; then
        if ! start_pumpkin "$process_args"; then
            log "WARNING: Failed to restart process"
        fi
    fi
    
    log "SUCCESS | Updated to version $latest_version"
    log "========== Auto-update complete =========="
    exit 0
}

# Run main workflow
main "$@"
