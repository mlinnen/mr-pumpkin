# Mr. Pumpkin PWA Architecture

## Overview
A Blazor WebAssembly Progressive Web App (PWA) that provides a mobile-first remote control interface for Mr. Pumpkin. The PWA connects to the existing Python server via WebSocket and sends commands to control the pumpkin face.

## Server Architecture (Existing)
- **Python Server**: `pumpkin_face.py` running on localhost
  - TCP Socket: Port 5000 (legacy, not used by PWA)
  - **WebSocket**: Port 5001 (used by PWA)
- **Protocol**: Text-based command strings
  - Send: Raw command string (e.g., "happy", "blink", "gaze 45 30")
  - Receive: Text response ("OK ...", "ERROR ...", or JSON data)
- **Commands**: 50+ commands defined in `command_handler.py` (see CommandRouter.execute)

## WebSocket Message Format
```
Client → Server: "happy"
Server → Client: "OK Expression changed to happy"

Client → Server: "list_recordings"
Server → Client: [{"filename": "demo.json", "command_count": 42, "duration_ms": 5000}]

Client → Server: "play demo"
Server → Client: "OK Playing demo.json (5000ms)"
```

Special cases:
- `upload_timeline <filename> <json>`: Inline JSON upload
- `upload_audio <filename> <base64>`: Inline audio upload
- `import_recordings <base64-zip>`: Import recordings from base64 zip
- `export_recordings`: Returns `RECORDINGS_ZIP:<base64>`

## Project Structure
```
webapp/
├── MrPumpkin.Web/
│   ├── MrPumpkin.Web.csproj          # Blazor WASM project (.NET 9)
│   ├── Program.cs                     # Entry point + PWA setup
│   ├── App.razor                      # Root component
│   ├── MainLayout.razor               # Mobile-first layout (bottom nav)
│   ├── _Imports.razor                 # Global using statements
│   ├── wwwroot/
│   │   ├── index.html                 # SPA host page
│   │   ├── manifest.json              # PWA manifest
│   │   ├── service-worker.js          # Service worker (dev)
│   │   ├── service-worker.published.js # Service worker (prod)
│   │   ├── css/
│   │   │   └── app.css                # Global styles (mobile-first)
│   │   └── icon-*.png                 # PWA icons (placeholder)
│   ├── Pages/
│   │   ├── Index.razor                # Dashboard (connection + quick actions)
│   │   ├── Recordings.razor           # Recordings management
│   │   └── Controls.razor             # Expression & animation controls
│   ├── Components/
│   │   ├── ConnectionBar.razor        # WebSocket connection status
│   │   ├── RecordingList.razor        # Recording list (play/delete/rename)
│   │   ├── NowPlaying.razor           # Currently playing + seek bar
│   │   ├── ExpressionControls.razor   # Expression buttons
│   │   ├── AnimationControls.razor    # Blink, wink, roll eyes
│   │   ├── GazeControl.razor          # Gaze/jog control (2D pad)
│   │   ├── EyebrowControls.razor      # Eyebrow buttons
│   │   ├── MouthControls.razor        # Mouth viseme buttons
│   │   └── RecordingControls.razor    # Start/stop recording
│   └── Services/
│       └── PumpkinWebSocketService.cs # WebSocket service layer
└── README.md                          # Getting started guide
```

## Component Breakdown

### Pages
1. **Index.razor** (Dashboard)
   - ConnectionBar component
   - Quick expression buttons (happy, sad, angry, etc.)
   - NowPlaying component (if something is playing)
   - Navigation to Recordings and Controls pages

2. **Recordings.razor**
   - ConnectionBar component
   - RecordingList component
   - Upload/download recording buttons
   - Export/import all recordings

3. **Controls.razor**
   - ConnectionBar component
   - ExpressionControls component
   - AnimationControls component
   - EyebrowControls component
   - MouthControls component
   - GazeControl component
   - RecordingControls component
   - Projection jog controls

### Shared Components
- **ConnectionBar**: Shows connection status (connected/disconnected), server address input, connect/disconnect button
- **RecordingList**: List of recordings with play/pause/stop, delete, rename, multi-select, create from selection
- **NowPlaying**: Current playback status, filename, seek bar, pause/resume/stop
- **ExpressionControls**: 7 expression buttons (neutral, happy, sad, angry, surprised, scared, sleeping)
- **AnimationControls**: Blink, wink left/right, roll eyes clockwise/counterclockwise
- **GazeControl**: 2D touch/drag control for gaze direction + jog display buttons
- **EyebrowControls**: Raise/lower eyebrows (both/left/right), reset
- **MouthControls**: Mouth viseme buttons (closed, open, wide, rounded, neutral)
- **RecordingControls**: Start/stop recording, cancel, recording status indicator

## State Management
- **PumpkinWebSocketService**: Singleton service managing:
  - WebSocket connection lifecycle
  - Command sending + response handling
  - State notifications via events (`ConnectionStatusChanged`, `RecordingsChanged`, `PlaybackStatusChanged`)
  - Automatic reconnection logic
  - Connection URI (default: `ws://localhost:5001`)

State flow:
1. Components inject `PumpkinWebSocketService`
2. Components call service methods (e.g., `SendExpressionAsync("happy")`)
3. Service sends command via WebSocket
4. Service raises events when state changes
5. Components subscribe to events and re-render via `StateHasChanged()`

## WebSocket Service API
```csharp
public class PumpkinWebSocketService : IAsyncDisposable
{
    // Connection management
    public bool IsConnected { get; }
    public string ServerUri { get; set; }
    public event EventHandler<bool> ConnectionStatusChanged;
    public Task ConnectAsync(CancellationToken ct = default);
    public Task DisconnectAsync();
    
    // Expression commands
    public Task SendExpressionAsync(string expression);
    
    // Animation commands
    public Task BlinkAsync();
    public Task WinkLeftAsync();
    public Task WinkRightAsync();
    public Task RollClockwiseAsync();
    public Task RollCounterclockwiseAsync();
    
    // Gaze commands
    public Task SetGazeAsync(float x, float y);
    public Task SetGazeIndependentAsync(float lx, float ly, float rx, float ry);
    
    // Eyebrow commands
    public Task RaiseEyebrowsAsync();
    public Task LowerEyebrowsAsync();
    public Task RaiseEyebrowLeftAsync();
    public Task LowerEyebrowLeftAsync();
    public Task RaiseEyebrowRightAsync();
    public Task LowerEyebrowRightAsync();
    public Task ResetEyebrowsAsync();
    public Task SetEyebrowAsync(float value);
    public Task SetEyebrowLeftAsync(float left, float right);
    public Task SetEyebrowRightAsync(float left, float right);
    
    // Mouth commands
    public Task SetMouthClosedAsync();
    public Task SetMouthOpenAsync();
    public Task SetMouthWideAsync();
    public Task SetMouthRoundedAsync();
    public Task SetMouthNeutralAsync();
    public Task SetMouthAsync(string viseme);
    
    // Nose commands
    public Task WiggleNoseAsync(float magnitude = 50f);
    public Task TwitchNoseAsync(float magnitude = 50f);
    public Task ScrunchNoseAsync(float magnitude = 50f);
    public Task ResetNoseAsync();
    
    // Head/projection commands
    public Task TurnLeftAsync(int amount = 50);
    public Task TurnRightAsync(int amount = 50);
    public Task TurnUpAsync(int amount = 50);
    public Task TurnDownAsync(int amount = 50);
    public Task CenterHeadAsync();
    public Task JogOffsetAsync(int dx, int dy);
    public Task JogOffsetNoSaveAsync(int dx, int dy);
    public Task SetOffsetAsync(int x, int y);
    public Task ResetProjectionAsync();
    
    // Recording commands
    public event EventHandler RecordingStatusChanged;
    public Task RecordStartAsync();
    public Task RecordStopAsync(string filename);
    public Task RecordCancelAsync();
    public Task<RecordingStatus> GetRecordingStatusAsync();
    
    // Playback commands
    public event EventHandler<TimelineStatus> PlaybackStatusChanged;
    public Task PlayAsync(string filename);
    public Task PauseAsync();
    public Task ResumeAsync();
    public Task StopAsync();
    public Task SeekAsync(int positionMs);
    public Task<TimelineStatus> GetTimelineStatusAsync();
    
    // File management
    public event EventHandler RecordingsChanged;
    public Task<List<RecordingInfo>> ListRecordingsAsync();
    public Task DeleteRecordingAsync(string filename);
    public Task RenameRecordingAsync(string oldName, string newName);
    public Task<string> DownloadTimelineAsync(string filename);
    public Task UploadTimelineAsync(string filename, string jsonContent);
    public Task UploadAudioAsync(string filename, byte[] audioBytes);
    public Task<byte[]> ExportRecordingsAsync();
    public Task ImportRecordingsAsync(byte[] zipBytes);
    
    // Utility
    public Task ResetAsync();
    public Task<string> GetHelpAsync();
}
```

## Mobile-First Design
- Bottom navigation bar (3 tabs: Dashboard, Recordings, Controls)
- Large touch-friendly buttons (min 48x48 dp)
- Responsive grid layout (CSS Grid + Flexbox)
- Swipe gestures for seek bar, gaze control
- Haptic feedback (vibration) on button press (optional)
- Dark theme by default (easier on eyes when controlling pumpkin at night)

## PWA Features
- **Installable**: Add to home screen
- **Offline-capable**: Service worker caches static assets
- **Responsive**: Works on mobile, tablet, desktop
- **Manifest**: Themed with pumpkin orange (#FF6B35)

## Hosting Strategy
The Python server does NOT host the Blazor app. Two options:

### Option 1: Static File Hosting (Recommended)
- Build Blazor WASM: `dotnet publish -c Release`
- Output: `webapp/MrPumpkin.Web/bin/Release/net9.0/publish/wwwroot/`
- Serve via:
  - IIS / nginx / Apache
  - GitHub Pages / Netlify / Vercel (for public demo)
  - Local file:// (development only — WebSocket won't work in file://)

### Option 2: Python Static Server (Simple Dev Server)
- Add Flask/aiohttp static file serving to pumpkin_face.py (future enhancement)
- Serve Blazor WASM build from `/wwwroot/` on port 8080
- WebSocket remains on port 5001

**Recommendation**: Use Option 1 (external hosting) to keep the Python server simple and focused on pumpkin control.

## Development Workflow
1. Run Python server: `python pumpkin_face.py`
2. Build Blazor app: `dotnet build` (or `dotnet watch` for hot reload)
3. Run Blazor dev server: `dotnet run` (serves on https://localhost:5002 or similar)
4. PWA connects to `ws://localhost:5001`

## Security Considerations
- WebSocket runs on localhost only (no remote access by default)
- No authentication (local network only)
- For remote access: Add reverse proxy (nginx) with TLS + basic auth
- File upload validation: Check file extensions, size limits

## Future Enhancements
- Audio playback in PWA (sync with pumpkin animation)
- Timeline editor (visual timeline builder)
- Touch gesture recording (record gestures as animations)
- Preset library (save favorite expressions)
- Multi-pumpkin support (connect to multiple pumpkins)
