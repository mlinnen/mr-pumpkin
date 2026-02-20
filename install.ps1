# Mr. Pumpkin - Windows Installation Script
$ErrorActionPreference = "Stop"

Write-Host "🎃 Mr. Pumpkin - Installation Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Detected OS: Windows" -ForegroundColor Yellow
Write-Host ""

# Install Python dependencies
Write-Host "🐍 Installing Python dependencies..." -ForegroundColor Cyan
try {
    if (Get-Command pip -ErrorAction SilentlyContinue) {
        pip install -r requirements.txt
        Write-Host "  ✓ Python dependencies installed" -ForegroundColor Green
    } elseif (Get-Command pip3 -ErrorAction SilentlyContinue) {
        pip3 install -r requirements.txt
        Write-Host "  ✓ Python dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "  ❌ pip not found. Please install Python first." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ❌ Failed to install dependencies: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  python pumpkin_face.py              # Run fullscreen on default monitor"
Write-Host "  python pumpkin_face.py --window     # Run in windowed mode"
Write-Host "  python client_example.py            # Send commands to pumpkin face"
Write-Host ""
Write-Host "Press ESC to exit the application." -ForegroundColor Yellow
