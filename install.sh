#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPENDENCY_HELPER="$SCRIPT_DIR/scripts/unix_dependency_plan.py"

echo "🎃 Mr. Pumpkin - Installation Script"
echo "======================================"
echo ""

# Helpers
find_python_command() {
    if command -v python3 &> /dev/null; then
        echo "python3"
    elif command -v python &> /dev/null; then
        echo "python"
    fi
}

find_pip_command() {
    if command -v pip3 &> /dev/null; then
        echo "pip3"
    elif command -v pip &> /dev/null; then
        echo "pip"
    fi
}

pip_supports_break_system_packages() {
    local pip_cmd="$1"
    "$pip_cmd" help install 2>&1 | grep -q -- "--break-system-packages"
}

install_apt_packages() {
    local packages=("$@")
    if [ ${#packages[@]} -eq 0 ]; then
        return 0
    fi

    if ! command -v apt-get &> /dev/null; then
        return 1
    fi

    echo "  Running: apt-get install -y ${packages[*]}"
    if [ "$(id -u)" -eq 0 ]; then
        apt-get update
        apt-get install -y "${packages[@]}"
    elif command -v sudo &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y "${packages[@]}"
    else
        return 1
    fi
}

install_pip_requirements() {
    local pip_cmd="$1"
    shift

    local requirements=("$@")
    if [ ${#requirements[@]} -eq 0 ]; then
        return 0
    fi

    local pip_args=("install")
    if [[ "$OS" == "raspberry-pi" ]] && pip_supports_break_system_packages "$pip_cmd"; then
        pip_args+=("--break-system-packages")
    fi

    "$pip_cmd" "${pip_args[@]}" "${requirements[@]}"
}

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    # Check if it's Raspberry Pi
    if [ -f /proc/device-tree/model ]; then
        if grep -q "Raspberry Pi" /proc/device-tree/model; then
            OS="raspberry-pi"
        fi
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
fi

echo "Detected OS: $OS"
echo ""

# Install SDL2 system dependencies on Raspberry Pi / Debian / Ubuntu
if [[ "$OS" == "raspberry-pi" ]] || [[ "$OS" == "linux" ]]; then
    echo "📦 Installing SDL2 system dependencies..."
    if install_apt_packages libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev; then
        echo "  ✓ SDL2 dependencies installed"
        echo ""
    else
        echo "  ⚠ Could not install SDL2 packages automatically. Please install them manually:"
        echo "    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev"
        echo ""
    fi
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if [[ "$OS" == "raspberry-pi" ]]; then
    PYTHON_CMD="$(find_python_command)"
    if [ -z "$PYTHON_CMD" ]; then
        echo "  ❌ Python not found. Please install Python 3 first."
        exit 1
    fi

    PLAN_FILES=("$SCRIPT_DIR/requirements.txt")
    if [ -f "$SCRIPT_DIR/skill/requirements.txt" ]; then
        PLAN_FILES+=("$SCRIPT_DIR/skill/requirements.txt")
    fi

    eval "$("$PYTHON_CMD" "$DEPENDENCY_HELPER" --raspberry-pi --emit-shell "${PLAN_FILES[@]}")"

    if [ ${#APT_PACKAGES[@]} -gt 0 ]; then
        echo "🍓 Installing Raspberry Pi system Python packages..."
        if [ -z "$(find_pip_command)" ] && [ ${#PIP_REQUIREMENTS[@]} -gt 0 ]; then
            APT_PACKAGES+=("python3-pip")
        fi
        if install_apt_packages "${APT_PACKAGES[@]}"; then
            echo "  ✓ Raspberry Pi apt-managed Python packages installed"
        else
            echo "  ⚠ Could not install Raspberry Pi apt-managed Python packages automatically."
            echo "    Falling back to pip for any remaining packages."
            PIP_REQUIREMENTS+=(
                "mutagen>=1.45.0"
                "pygame>=2.0.0,<3.0.0"
                "websockets>=13.0,<15.1"
            )
        fi
        echo ""
    fi

    PIP_CMD="$(find_pip_command)"
    if [ ${#PIP_REQUIREMENTS[@]} -gt 0 ]; then
        if [ -z "$PIP_CMD" ]; then
            echo "  ❌ pip not found. Please install python3-pip first."
            exit 1
        fi
        install_pip_requirements "$PIP_CMD" "${PIP_REQUIREMENTS[@]}"
    fi

    echo "  ✓ Python dependencies installed"
    echo ""
else
    if command -v pip &> /dev/null; then
        pip install -r "$SCRIPT_DIR/requirements.txt"
        echo "  ✓ Python dependencies installed"
    elif command -v pip3 &> /dev/null; then
        pip3 install -r "$SCRIPT_DIR/requirements.txt"
        echo "  ✓ Python dependencies installed"
    else
        echo "  ❌ pip not found. Please install Python and pip first."
        exit 1
    fi

    if [ -f "$SCRIPT_DIR/skill/requirements.txt" ]; then
        echo "🧠 Installing skill dependencies..."
        if command -v pip &> /dev/null; then
            pip install -r "$SCRIPT_DIR/skill/requirements.txt"
            echo "  ✓ Skill dependencies installed"
        elif command -v pip3 &> /dev/null; then
            pip3 install -r "$SCRIPT_DIR/skill/requirements.txt"
            echo "  ✓ Skill dependencies installed"
        fi
        echo ""
    fi
fi

echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  python pumpkin_face.py              # Run fullscreen on default monitor"
echo "  python pumpkin_face.py --window     # Run in windowed mode"
echo "  python client_example.py            # Send commands to pumpkin face"
echo ""
echo "Press ESC to exit the application."
