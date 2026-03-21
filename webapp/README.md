# Mr. Pumpkin PWA

A Blazor WebAssembly Progressive Web App (PWA) for controlling the Mr. Pumpkin animated face.

## Prerequisites

- .NET 9 SDK: [Download here](https://dotnet.microsoft.com/download/dotnet/9.0)
- Mr. Pumpkin Python server running on `localhost:5001` (WebSocket)

## Getting Started

### 1. Start the Python Server

Make sure the Mr. Pumpkin server is running:

```bash
cd F:\mr-pumpkin
python pumpkin_face.py
```

The server will start:
- TCP Socket: `localhost:5000`
- **WebSocket**: `localhost:5001` ← Used by PWA

### 2. Build the PWA

```bash
cd webapp\MrPumpkin.Web
dotnet build
```

### 3. Run the PWA (Development)

```bash
dotnet run
```

Or for hot reload during development:

```bash
dotnet watch
```

The PWA will open in your browser at `https://localhost:5xxx` (port varies).

### 4. Connect to Pumpkin

1. Open the PWA in your browser
2. Click "Connect" in the connection bar (default: `ws://localhost:5001`)
3. Start controlling your pumpkin! 🎃

## Project Structure

```
MrPumpkin.Web/
├── Pages/                     # Blazor pages (routes)
│   ├── Index.razor            # Dashboard (default page)
│   ├── Recordings.razor       # Recording management
│   └── Controls.razor         # Full control panel
├── Components/                # Reusable UI components
│   ├── ConnectionBar.razor    # WebSocket connection status
│   ├── ExpressionControls.razor
│   ├── AnimationControls.razor
│   ├── EyebrowControls.razor
│   ├── MouthControls.razor
│   ├── GazeControl.razor
│   ├── RecordingControls.razor
│   ├── RecordingList.razor
│   └── NowPlaying.razor
├── Services/                  # Business logic
│   └── PumpkinWebSocketService.cs  # WebSocket client
├── wwwroot/                   # Static assets
│   ├── index.html             # SPA host page
│   ├── manifest.json          # PWA manifest
│   ├── service-worker.js      # Service worker (dev)
│   └── css/app.css            # Global styles
├── Program.cs                 # App entry point
├── App.razor                  # Root component
└── MainLayout.razor           # Main layout (bottom nav)
```

## Features

### Dashboard
- Quick expression buttons (happy, sad, angry, etc.)
- Quick action buttons (blink, wink, roll eyes)
- WebSocket connection status
- Now playing widget (if something is playing)

### Recordings
- List all recordings with metadata
- Play/pause/stop recordings
- Delete recordings
- Rename recordings
- Multi-select recordings (for future: create from selection)
- Upload/download recordings
- Export/import all recordings as zip

### Controls
- **Expressions**: 7 expressions (neutral, happy, sad, angry, surprised, scared, sleeping)
- **Animations**: Blink, wink left/right, roll eyes clockwise/counterclockwise, twitch nose
- **Eyebrows**: Raise/lower both/left/right, reset to neutral
- **Mouth**: 5 visemes (closed, open, wide, rounded, neutral) for speech animation
- **Gaze**: 2D touch pad for eye gaze control
- **Projection Jog**: Adjust display position (up/down/left/right/center)
- **Recording**: Start/stop/cancel command recording

## Building for Production

```bash
dotnet publish -c Release
```

Output: `bin\Release\net9.0\publish\wwwroot\`

### Deployment Options

#### Option 1: Static File Server (Recommended)
Serve the `wwwroot` folder using:
- IIS / nginx / Apache
- GitHub Pages / Netlify / Vercel
- Python SimpleHTTPServer: `python -m http.server 8080 --directory wwwroot`

#### Option 2: Blazor Dev Server (Development Only)
```bash
dotnet run
```

The PWA connects via WebSocket to the Python server on `localhost:5001`.

## PWA Installation

On mobile (Chrome/Safari):
1. Open the PWA in your browser
2. Tap the "Share" button (Safari) or "⋮" menu (Chrome)
3. Select "Add to Home Screen"
4. Tap "Add"

The app will appear on your home screen like a native app!

## Troubleshooting

### "Not connected" error
- Make sure the Python server is running: `python pumpkin_face.py`
- Check that WebSocket is on port 5001 (look for "WebSocket server listening on port 5001" in console)
- If on a different machine, update the server URI in ConnectionBar

### Hot reload not working
- Use `dotnet watch` instead of `dotnet run`
- If hot reload breaks, restart with `Ctrl+C` then `dotnet watch` again

### Service worker errors in dev mode
- Ignore service worker errors in development
- Service worker only fully works in production builds

### Mobile gestures not working
- Make sure you're using Chrome or Safari (not Firefox mobile)
- Some gestures require `touch-action: none` CSS (already applied to gaze pad)

## Development Tips

### Adding a New Command
1. Add method to `PumpkinWebSocketService.cs`:
   ```csharp
   public Task MyNewCommandAsync() => SendCommandAsync("my_new_command");
   ```
2. Add button to appropriate component:
   ```html
   <button class="btn btn-control" @onclick="MyNewCommand">My Button</button>
   ```
3. Add code-behind:
   ```csharp
   private async Task MyNewCommand()
   {
       if (!PumpkinService.IsConnected) return;
       await PumpkinService.MyNewCommandAsync();
   }
   ```

### Testing WebSocket Messages
Open browser DevTools → Network → WS → Click on connection → Messages tab

### Mobile Testing
- Chrome DevTools → Toggle device toolbar (Ctrl+Shift+M)
- Or use real device on same network (change `localhost` to your PC's IP)

## Architecture Notes

- **WebSocket**: All communication uses text-based WebSocket protocol (port 5001)
- **State Management**: Service events trigger component re-renders via `StateHasChanged()`
- **Offline Support**: Service worker caches static assets (works offline for browsing UI)
- **Mobile-First**: Bottom navigation bar, large touch targets, responsive grid layout

## See Also

- [Architecture Document](../docs/pwa-architecture.md) - Full architecture design
- [Python Server](../pumpkin_face.py) - Backend WebSocket server
- [Command Reference](../command_handler.py) - All available commands
