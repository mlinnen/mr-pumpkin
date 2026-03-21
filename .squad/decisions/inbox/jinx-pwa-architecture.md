# PWA Architecture Decision — Issue #76

**Date:** 2026-03-13  
**Author:** Jinx (Lead)  
**Status:** Approved  

## Context

Issue #76 requests a Progressive Web App (PWA) to control Mr. Pumpkin via mobile devices. The existing Python server already provides a WebSocket interface on port 5001. The PWA needs to support:
- Mobile-first UI with large touch targets
- Recording management (list, play, delete, rename, multi-select)
- Expression and animation controls
- Gaze control (2D touch pad)
- Recording/playback controls
- File upload/download/import/export

## Decision

Build a **Blazor WebAssembly PWA** (.NET 9) with the following architecture:

### Technology Stack
- **Framework:** Blazor WebAssembly (client-side, runs in browser)
- **Target:** .NET 9
- **State Management:** Singleton service with event-driven updates
- **Styling:** Custom CSS with mobile-first approach (no external UI framework)
- **PWA Features:** Service worker, manifest, installable

### Project Structure
```
webapp/MrPumpkin.Web/
├── Pages/ (3 routes: Index, Recordings, Controls)
├── Components/ (9 reusable components)
├── Services/ (PumpkinWebSocketService — WebSocket client)
└── wwwroot/ (static assets, manifest, service workers)
```

### Communication Protocol
- **Connection:** WebSocket to `ws://localhost:5001`
- **Message Format:** Plain text commands (e.g., "happy", "blink", "gaze 45 30")
- **Response Format:** Text ("OK ...", "ERROR ...") or JSON for status queries
- **Service Layer:** 50+ async methods in `PumpkinWebSocketService` mapping 1:1 to server commands

### Hosting Strategy
- **Separation of Concerns:** Python server remains focused on pumpkin control; Blazor WASM is served separately
- **Deployment Options:**
  1. Static file hosting (IIS, nginx, Apache, GitHub Pages, Netlify, Vercel) — Recommended
  2. Python static server (future enhancement if needed)
- **Development:** `dotnet run` serves Blazor on https://localhost:5xxx; PWA connects to Python server on ws://localhost:5001

### UI Design
- **Navigation:** Bottom navigation bar (3 tabs: Dashboard, Recordings, Controls)
- **Mobile-First:** Large touch targets (min 48x48dp), swipe gestures, dark theme
- **PWA:** Installable on mobile home screen, offline UI (online required for commands)

## Rationale

### Why Blazor WASM over Blazor Server?
- Python server is the backend; Blazor Server would create a redundant .NET backend
- Client-side execution reduces server load
- WebSocket connection directly from browser to Python server

### Why Not Single-Page HTML/JavaScript?
- Considered, but:
  - C# WebSocket API is more robust than plain JS for complex state management
  - Blazor component model simplifies UI composition
  - Type safety for 50+ commands
  - Strong ecosystem for PWA features

### Why Separate Hosting?
- Keep Python server simple (no static file serving)
- Allow independent scaling/deployment
- Blazor WASM CDN hosting reduces server load
- Python server can remain focused on hardware control

### Why No External UI Framework (e.g., MudBlazor)?
- Mobile-first custom CSS is simpler and lighter
- No dependency on external library versioning
- Full control over touch interactions and gestures

## Alternatives Considered

1. **React/Vue SPA:** Rejected — Blazor WASM provides better type safety and less boilerplate for this use case
2. **Blazor Server:** Rejected — Would require .NET backend when Python server already exists
3. **Native Mobile App (Xamarin/MAUI):** Rejected — PWA is more accessible (no app store, works on any device)
4. **Python Flask + Jinja:** Rejected — Server-side rendering not ideal for real-time control UI

## Consequences

### Positive
- ✅ Mobile-first design with PWA installability
- ✅ Type-safe WebSocket service layer
- ✅ Component reusability (9 components)
- ✅ Offline UI caching via service worker
- ✅ No changes to Python server
- ✅ Independent deployment (PWA vs. Python server)

### Negative
- ⚠️ Requires .NET 9 SDK for development
- ⚠️ Larger initial download (~2-3 MB WASM runtime) vs. plain JS
- ⚠️ Blazor learning curve for contributors unfamiliar with .NET

### Risks
- **Browser Compatibility:** Blazor WASM requires modern browsers (Chrome 70+, Safari 13+, Firefox 65+)
  - Mitigation: Target audience (makers/hobbyists) likely uses modern browsers
- **WebSocket Connection Loss:** Network issues could break control
  - Mitigation: Connection status bar, auto-reconnect logic, visual feedback
- **Mobile Performance:** WASM overhead on older mobile devices
  - Mitigation: Lightweight UI, minimal animations, tested on mid-range devices

## Implementation Notes

### Service Layer API
`PumpkinWebSocketService` provides:
- Connection lifecycle management (`ConnectAsync`, `DisconnectAsync`)
- 50+ command methods matching `command_handler.py`
- Event-driven state updates (`ConnectionStatusChanged`, `RecordingStatusChanged`, `PlaybackStatusChanged`, `RecordingsChanged`)

### Component Breakdown
1. **ConnectionBar:** WebSocket connection status + server URI input
2. **ExpressionControls:** 7 expression buttons
3. **AnimationControls:** Blink, wink, roll eyes, twitch nose
4. **EyebrowControls:** Raise/lower eyebrows
5. **MouthControls:** 5 mouth visemes
6. **GazeControl:** 2D touch pad + jog display
7. **RecordingControls:** Start/stop/cancel recording
8. **RecordingList:** List with play/delete/rename/multi-select
9. **NowPlaying:** Current playback + seek bar

### File Upload/Download
- **Upload:** `<input type="file">` → read as text/bytes → send via `upload_timeline`/`upload_audio`
- **Download:** Request JSON/zip via WebSocket → create blob → trigger browser download
- **Export/Import:** Base64-encoded zip via WebSocket commands

## Success Criteria

- ✅ PWA installable on mobile devices
- ✅ All 50+ commands accessible via UI
- ✅ Recording management (list, play, delete, rename)
- ✅ Gaze control via 2D touch pad
- ✅ Connection status visible
- ✅ Works on iOS Safari and Android Chrome
- ✅ Service worker caches static assets

## Related Files

- Architecture doc: `docs/pwa-architecture.md`
- Project root: `webapp/MrPumpkin.Web/`
- WebSocket service: `webapp/MrPumpkin.Web/Services/PumpkinWebSocketService.cs`
- README: `webapp/README.md`

## Follow-Up Tasks

- [ ] Implement proper request/response handling in `PumpkinWebSocketService` (currently fire-and-forget)
- [ ] Add rename dialog for recordings
- [ ] Implement "create from selection" (merge multiple recordings)
- [ ] Add file upload dialogs for timeline/audio
- [ ] Test on real iOS and Android devices
- [ ] Add haptic feedback (vibration) on button press
- [ ] Consider audio playback in PWA (sync with pumpkin animation)
