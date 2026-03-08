#!/bin/bash
set -e

echo "🎃 Mr. Pumpkin - Installation Script"
echo "======================================"
echo ""

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
    if command -v apt-get &> /dev/null; then
        echo "  Running: sudo apt-get update && sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev"
        sudo apt-get update
        sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
        echo "  ✓ SDL2 dependencies installed"
        echo ""
    else
        echo "  ⚠ apt-get not found. Please install SDL2 manually:"
        echo "    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev"
        echo ""
    fi
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if command -v pip &> /dev/null; then
    pip install -r requirements.txt
    echo "  ✓ Python dependencies installed"
elif command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
    echo "  ✓ Python dependencies installed"
else
    echo "  ❌ pip not found. Please install Python and pip first."
    exit 1
fi

# Install skill dependencies if present
if [ -f "skill/requirements.txt" ]; then
    echo "🧠 Installing skill dependencies..."
    if command -v pip &> /dev/null; then
        pip install -r skill/requirements.txt
        echo "  ✓ Skill dependencies installed"
    elif command -v pip3 &> /dev/null; then
        pip3 install -r skill/requirements.txt
        echo "  ✓ Skill dependencies installed"
    fi
    echo ""
fi

echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  python pumpkin_face.py              # Run fullscreen on default monitor"
echo "  python pumpkin_face.py --window     # Run in windowed mode"
echo "  python client_example.py            # Send commands to pumpkin face"
echo ""
echo "Press ESC to exit the application."
