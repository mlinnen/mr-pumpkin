using System.Net.WebSockets;
using System.Text;
using System.Text.Json;

namespace MrPumpkin.Web.Services;

public class PumpkinWebSocketService : IAsyncDisposable
{
    private ClientWebSocket? _websocket;
    private CancellationTokenSource? _cts;
    private Task? _receiveTask;

    public bool IsConnected => _websocket?.State == WebSocketState.Open;
    public string ServerUri { get; set; } = "ws://localhost:5001";

    public event EventHandler<bool>? ConnectionStatusChanged;
    public event EventHandler? RecordingStatusChanged;
    public event EventHandler<TimelineStatus>? PlaybackStatusChanged;
    public event EventHandler? RecordingsChanged;

    public async Task ConnectAsync(CancellationToken ct = default)
    {
        if (IsConnected) return;

        _websocket = new ClientWebSocket();
        _cts = new CancellationTokenSource();

        try
        {
            await _websocket.ConnectAsync(new Uri(ServerUri), ct);
            ConnectionStatusChanged?.Invoke(this, true);

            // Start receive loop
            _receiveTask = Task.Run(() => ReceiveLoop(_cts.Token), _cts.Token);
        }
        catch
        {
            _websocket?.Dispose();
            _websocket = null;
            _cts?.Dispose();
            _cts = null;
            throw;
        }
    }

    public async Task DisconnectAsync()
    {
        if (_websocket == null) return;

        try
        {
            _cts?.Cancel();
            if (_websocket.State == WebSocketState.Open)
            {
                await _websocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "User disconnect", CancellationToken.None);
            }
        }
        catch { }
        finally
        {
            _websocket?.Dispose();
            _websocket = null;
            _cts?.Dispose();
            _cts = null;
            ConnectionStatusChanged?.Invoke(this, false);
        }
    }

    private async Task ReceiveLoop(CancellationToken ct)
    {
        var buffer = new byte[8192];
        while (!ct.IsCancellationRequested && _websocket?.State == WebSocketState.Open)
        {
            try
            {
                var result = await _websocket.ReceiveAsync(new ArraySegment<byte>(buffer), ct);
                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await DisconnectAsync();
                    break;
                }

                var message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                HandleResponse(message);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch
            {
                await DisconnectAsync();
                break;
            }
        }
    }

    private void HandleResponse(string response)
    {
        // Check for JSON responses (status queries)
        if (response.StartsWith("{"))
        {
            try
            {
                var json = JsonDocument.Parse(response);
                if (json.RootElement.TryGetProperty("state", out _))
                {
                    var status = JsonSerializer.Deserialize<TimelineStatus>(response);
                    if (status != null)
                    {
                        PlaybackStatusChanged?.Invoke(this, status);
                    }
                }
                else if (json.RootElement.TryGetProperty("is_recording", out _))
                {
                    RecordingStatusChanged?.Invoke(this, EventArgs.Empty);
                }
            }
            catch { }
        }
    }

    private async Task SendCommandAsync(string command)
    {
        if (!IsConnected) throw new InvalidOperationException("Not connected");
        
        var bytes = Encoding.UTF8.GetBytes(command);
        await _websocket!.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, CancellationToken.None);
    }

    // Expression commands
    public Task SendExpressionAsync(string expression) => SendCommandAsync(expression);

    // Animation commands
    public Task BlinkAsync() => SendCommandAsync("blink");
    public Task WinkLeftAsync() => SendCommandAsync("wink_left");
    public Task WinkRightAsync() => SendCommandAsync("wink_right");
    public Task RollClockwiseAsync() => SendCommandAsync("roll_clockwise");
    public Task RollCounterclockwiseAsync() => SendCommandAsync("roll_counterclockwise");

    // Gaze commands
    public Task SetGazeAsync(float x, float y) => SendCommandAsync($"gaze {x} {y}");
    public Task SetGazeIndependentAsync(float lx, float ly, float rx, float ry) => SendCommandAsync($"gaze {lx} {ly} {rx} {ry}");

    // Eyebrow commands
    public Task RaiseEyebrowsAsync() => SendCommandAsync("eyebrow_raise");
    public Task LowerEyebrowsAsync() => SendCommandAsync("eyebrow_lower");
    public Task RaiseEyebrowLeftAsync() => SendCommandAsync("eyebrow_raise_left");
    public Task LowerEyebrowLeftAsync() => SendCommandAsync("eyebrow_lower_left");
    public Task RaiseEyebrowRightAsync() => SendCommandAsync("eyebrow_raise_right");
    public Task LowerEyebrowRightAsync() => SendCommandAsync("eyebrow_lower_right");
    public Task ResetEyebrowsAsync() => SendCommandAsync("eyebrow_reset");
    public Task SetEyebrowAsync(float value) => SendCommandAsync($"eyebrow {value}");
    public Task SetEyebrowLeftAsync(float value) => SendCommandAsync($"eyebrow_left {value}");
    public Task SetEyebrowRightAsync(float value) => SendCommandAsync($"eyebrow_right {value}");

    // Mouth commands
    public Task SetMouthClosedAsync() => SendCommandAsync("mouth_closed");
    public Task SetMouthOpenAsync() => SendCommandAsync("mouth_open");
    public Task SetMouthWideAsync() => SendCommandAsync("mouth_wide");
    public Task SetMouthRoundedAsync() => SendCommandAsync("mouth_rounded");
    public Task SetMouthNeutralAsync() => SendCommandAsync("mouth_neutral");
    public Task SetMouthAsync(string viseme) => SendCommandAsync($"mouth {viseme}");

    // Nose commands
    public Task WiggleNoseAsync(float magnitude = 50f) => SendCommandAsync($"wiggle_nose {magnitude}");
    public Task TwitchNoseAsync(float magnitude = 50f) => SendCommandAsync($"twitch_nose {magnitude}");
    public Task ScrunchNoseAsync(float magnitude = 50f) => SendCommandAsync($"scrunch_nose {magnitude}");
    public Task ResetNoseAsync() => SendCommandAsync("reset_nose");

    // Head/projection commands
    public Task TurnLeftAsync(int amount = 50) => SendCommandAsync($"turn_left {amount}");
    public Task TurnRightAsync(int amount = 50) => SendCommandAsync($"turn_right {amount}");
    public Task TurnUpAsync(int amount = 50) => SendCommandAsync($"turn_up {amount}");
    public Task TurnDownAsync(int amount = 50) => SendCommandAsync($"turn_down {amount}");
    public Task CenterHeadAsync() => SendCommandAsync("center_head");
    public Task JogOffsetAsync(int dx, int dy) => SendCommandAsync($"jog_offset {dx} {dy}");
    public Task JogOffsetNoSaveAsync(int dx, int dy) => SendCommandAsync($"jog_offset_nosave {dx} {dy}");
    public Task SetOffsetAsync(int x, int y) => SendCommandAsync($"set_offset {x} {y}");
    public Task ResetProjectionAsync() => SendCommandAsync("projection_reset");

    // Recording commands
    public Task RecordStartAsync() => SendCommandAsync("record_start");
    public Task RecordStopAsync(string filename) => SendCommandAsync($"record_stop {filename}");
    public Task RecordCancelAsync() => SendCommandAsync("record_cancel");

    public async Task<RecordingStatus> GetRecordingStatusAsync()
    {
        await SendCommandAsync("recording_status");
        // TODO: Implement proper request/response handling
        return new RecordingStatus { IsRecording = false, CommandCount = 0, DurationMs = 0 };
    }

    // Playback commands
    public Task PlayAsync(string filename) => SendCommandAsync($"play {filename}");
    public Task PauseAsync() => SendCommandAsync("pause");
    public Task ResumeAsync() => SendCommandAsync("resume");
    public Task StopAsync() => SendCommandAsync("stop");
    public Task SeekAsync(int positionMs) => SendCommandAsync($"seek {positionMs}");

    public async Task<TimelineStatus> GetTimelineStatusAsync()
    {
        await SendCommandAsync("timeline_status");
        // TODO: Implement proper request/response handling
        return new TimelineStatus 
        { 
            State = "stopped", 
            Filename = null, 
            PositionMs = 0, 
            DurationMs = 0, 
            IsPlaying = false 
        };
    }

    // File management
    public async Task<List<RecordingInfo>> ListRecordingsAsync()
    {
        await SendCommandAsync("list_recordings");
        // TODO: Implement proper request/response handling
        return new List<RecordingInfo>();
    }

    public async Task DeleteRecordingAsync(string filename)
    {
        await SendCommandAsync($"delete_recording {filename}");
        RecordingsChanged?.Invoke(this, EventArgs.Empty);
    }

    public Task RenameRecordingAsync(string oldName, string newName) => SendCommandAsync($"rename_recording {oldName} {newName}");

    public async Task<string> DownloadTimelineAsync(string filename)
    {
        await SendCommandAsync($"download_timeline {filename}");
        // TODO: Implement proper request/response handling
        return "{}";
    }

    public Task UploadTimelineAsync(string filename, string jsonContent) => 
        SendCommandAsync($"upload_timeline {filename} {jsonContent}");

    public async Task UploadAudioAsync(string filename, byte[] audioBytes)
    {
        var base64 = Convert.ToBase64String(audioBytes);
        await SendCommandAsync($"upload_audio {filename} {base64}");
    }

    public async Task<byte[]> ExportRecordingsAsync()
    {
        await SendCommandAsync("export_recordings");
        // TODO: Implement proper request/response handling
        return Array.Empty<byte>();
    }

    public async Task ImportRecordingsAsync(byte[] zipBytes)
    {
        var base64 = Convert.ToBase64String(zipBytes);
        await SendCommandAsync($"import_recordings {base64}");
        RecordingsChanged?.Invoke(this, EventArgs.Empty);
    }

    // Utility
    public Task ResetAsync() => SendCommandAsync("reset");
    public Task<string> GetHelpAsync()
    {
        // Return help text without network call
        return Task.FromResult("Use the UI controls to send commands to the pumpkin.");
    }

    public async ValueTask DisposeAsync()
    {
        await DisconnectAsync();
    }
}

// Data models
public class RecordingStatus
{
    public bool IsRecording { get; set; }
    public int CommandCount { get; set; }
    public int DurationMs { get; set; }
}

public class TimelineStatus
{
    public string State { get; set; } = "stopped";
    public string? Filename { get; set; }
    public int PositionMs { get; set; }
    public int DurationMs { get; set; }
    public bool IsPlaying { get; set; }
}

public class RecordingInfo
{
    public string Filename { get; set; } = "";
    public int CommandCount { get; set; }
    public int DurationMs { get; set; }
}
