import base64
import json
import time

class CommandRouter:
    """
    Protocol-agnostic command router for PumpkinFace.
    Accepts text commands, executes against PumpkinFace state, returns text responses.
    """
    
    def __init__(self, pumpkin_face, expression_class):
        """Initialize router with PumpkinFace instance."""
        self.pumpkin = pumpkin_face
        self.Expression = expression_class
    
    def execute(self, command_str: str) -> str:
        """
        Parse and execute command, return response string.
        
        Args:
            command_str: Raw command string (e.g., "blink", "happy", "gaze 0 45")
        
        Returns:
            Response string: "OK ...", "ERROR ...", or JSON data
        """
        data = command_str.strip().lower()
        
        # Handle blink command
        if data == "blink":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.blink()
            print("Blink animation triggered")
            return ""
        
        # Handle wink commands
        if data == "wink_left":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.wink_left()
            print("Left wink animation triggered")
            return ""
        elif data == "wink_right":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.wink_right()
            print("Right wink animation triggered")
            return ""
        
        # Handle rolling eyes commands
        if data == "roll_clockwise":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.roll_clockwise()
            print("Rolling eyes clockwise")
            return ""
        
        if data == "roll_counterclockwise":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.roll_counterclockwise()
            print("Rolling eyes counter-clockwise")
            return ""
        
        # Handle gaze command
        if data.startswith("gaze "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                args = [float(x) for x in parts[1:]]
                
                if len(args) == 2:
                    # Two args: apply same angles to both eyes
                    self.pumpkin.set_gaze(args[0], args[1])
                    print(f"Gaze set to: both eyes ({args[0]}°, {args[1]}°)")
                elif len(args) == 4:
                    # Four args: independent eye control
                    self.pumpkin.set_gaze(args[0], args[1], args[2], args[3])
                    print(f"Gaze set to: left ({args[0]}°, {args[1]}°), right ({args[2]}°, {args[3]}°)")
                else:
                    print(f"Error: gaze command requires 2 or 4 numeric arguments, got {len(args)}")
            except (ValueError, IndexError) as e:
                print(f"Error parsing gaze command: {e}")
            return ""
        
        # Handle eyebrow commands
        if data == "eyebrow_raise":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.raise_eyebrows()
            print("Eyebrows raised")
            return ""
        
        if data == "eyebrow_lower":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.lower_eyebrows()
            print("Eyebrows lowered")
            return ""
        
        if data == "eyebrow_raise_left":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.raise_eyebrow_left()
            print("Left eyebrow raised")
            return ""
        
        if data == "eyebrow_lower_left":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.lower_eyebrow_left()
            print("Left eyebrow lowered")
            return ""
        
        if data == "eyebrow_raise_right":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.raise_eyebrow_right()
            print("Right eyebrow raised")
            return ""
        
        if data == "eyebrow_lower_right":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.lower_eyebrow_right()
            print("Right eyebrow lowered")
            return ""
        
        if data == "eyebrow_reset":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.reset_eyebrows()
            print("Eyebrows reset to neutral")
            return ""
        
        if data.startswith("eyebrow "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                val = float(parts[1])
                self.pumpkin.set_eyebrow(val)
                print(f"Both eyebrows set to: {val}")
            except (ValueError, IndexError) as e:
                print(f"Error parsing eyebrow command: {e}")
            return ""
        
        if data.startswith("eyebrow_left "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                val = float(parts[1])
                self.pumpkin.set_eyebrow(val, self.pumpkin.eyebrow_right_offset)
                print(f"Left eyebrow set to: {val}")
            except (ValueError, IndexError) as e:
                print(f"Error parsing eyebrow_left command: {e}")
            return ""
        
        if data.startswith("eyebrow_right "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                val = float(parts[1])
                self.pumpkin.set_eyebrow(self.pumpkin.eyebrow_left_offset, val)
                print(f"Right eyebrow set to: {val}")
            except (ValueError, IndexError) as e:
                print(f"Error parsing eyebrow_right command: {e}")
            return ""
        
        # Handle projection offset commands
        if data == "projection_reset":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.reset_projection_offset()
            return ""
        
        if data.startswith("jog_offset "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                dx = int(parts[1])
                dy = int(parts[2])
                self.pumpkin.jog_projection(dx, dy, save=True)
            except (ValueError, IndexError) as e:
                print(f"Error parsing jog_offset command: {e}")
            return ""
        
        if data.startswith("jog_offset_nosave "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                dx = int(parts[1])
                dy = int(parts[2])
                self.pumpkin.jog_projection(dx, dy, save=False)
            except (ValueError, IndexError) as e:
                print(f"Error parsing jog_offset_nosave command: {e}")
            return ""
        
        if data.startswith("set_offset "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                x = int(parts[1])
                y = int(parts[2])
                self.pumpkin.set_projection_offset(x, y)
            except (ValueError, IndexError) as e:
                print(f"Error parsing set_offset command: {e}")
            return ""
        
        # Handle head movement commands
        if data == "turn_left" or data.startswith("turn_left "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                amount = int(parts[1]) if len(parts) > 1 else 50
                self.pumpkin.turn_head_left(amount)
                print(f"Turning head left by {amount}px")
            except (ValueError, IndexError) as e:
                print(f"Error parsing turn_left command: {e}")
            return ""
        
        if data == "turn_right" or data.startswith("turn_right "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                amount = int(parts[1]) if len(parts) > 1 else 50
                self.pumpkin.turn_head_right(amount)
                print(f"Turning head right by {amount}px")
            except (ValueError, IndexError) as e:
                print(f"Error parsing turn_right command: {e}")
            return ""
        
        if data == "turn_up" or data.startswith("turn_up "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                amount = int(parts[1]) if len(parts) > 1 else 50
                self.pumpkin.turn_head_up(amount)
                print(f"Turning head up by {amount}px")
            except (ValueError, IndexError) as e:
                print(f"Error parsing turn_up command: {e}")
            return ""
        
        if data == "turn_down" or data.startswith("turn_down "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                amount = int(parts[1]) if len(parts) > 1 else 50
                self.pumpkin.turn_head_down(amount)
                print(f"Turning head down by {amount}px")
            except (ValueError, IndexError) as e:
                print(f"Error parsing turn_down command: {e}")
            return ""
        
        if data == "center_head":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.center_head()
            print("Centering head position")
            return ""
        
        # Handle nose animation commands
        if data == "wiggle_nose" or data.startswith("wiggle_nose "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                magnitude = float(parts[1]) if len(parts) > 1 else 50.0
                self.pumpkin._start_nose_twitch(magnitude)
                print(f"Wiggling nose (magnitude={magnitude})")
            except (ValueError, IndexError) as e:
                print(f"Error parsing wiggle_nose command: {e}")
            return ""
        
        if data == "twitch_nose" or data.startswith("twitch_nose "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                magnitude = float(parts[1]) if len(parts) > 1 else 50.0
                self.pumpkin._start_nose_twitch(magnitude)
                print(f"Twitching nose (magnitude={magnitude})")
            except (ValueError, IndexError) as e:
                print(f"Error parsing twitch_nose command: {e}")
            return ""
        
        if data == "scrunch_nose" or data.startswith("scrunch_nose "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                magnitude = float(parts[1]) if len(parts) > 1 else 50.0
                self.pumpkin._start_nose_scrunch(magnitude)
                print(f"Scrunching nose (magnitude={magnitude})")
            except (ValueError, IndexError) as e:
                print(f"Error parsing scrunch_nose command: {e}")
            return ""
        
        if data == "reset_nose":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin._reset_nose()
            print("Resetting nose to neutral")
            return ""
        
        # Handle mouth speech commands
        if data == "mouth_closed":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.set_mouth_viseme("closed")
            print("Mouth set to closed viseme")
            return ""
        
        if data == "mouth_open":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.set_mouth_viseme("open")
            print("Mouth set to open viseme")
            return ""
        
        if data == "mouth_wide":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.set_mouth_viseme("wide")
            print("Mouth set to wide viseme")
            return ""
        
        if data == "mouth_rounded":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.set_mouth_viseme("rounded")
            print("Mouth set to rounded viseme")
            return ""
        
        if data == "mouth_neutral":
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            self.pumpkin.set_mouth_viseme("neutral")
            print("Mouth released to expression control")
            return ""
        
        # Handle parameterized mouth command: "mouth <viseme_name>"
        if data.startswith("mouth "):
            if self.pumpkin.recording_session.is_recording:
                self.pumpkin._capture_command_for_recording(data)
            try:
                parts = data.split()
                viseme = parts[1]
                valid_visemes = {"closed", "open", "wide", "rounded", "neutral"}
                if viseme not in valid_visemes:
                    print(f"Error: unknown viseme '{viseme}'. Valid: {', '.join(sorted(valid_visemes))}")
                else:
                    self.pumpkin.set_mouth_viseme(viseme)
                    print(f"Mouth set to viseme: {viseme}")
            except (ValueError, IndexError) as e:
                print(f"Error parsing mouth command: {e}")
            return ""
        
        # ===== TIMELINE COMMANDS =====
        
        # Reset command (clears recording and playback state)
        if data == "reset":
            self.pumpkin.recording_session.cancel()
            self.pumpkin.timeline_playback.stop()
            self.pumpkin.timeline_playback.filename = None  # Clear loaded filename
            self.pumpkin.timeline_playback.timeline = None  # Clear loaded timeline
            response = "OK Reset complete"
            print(response)
            return response
        
        # Recording commands
        if data == "record_start" or data == "record start":
            if self.pumpkin.recording_session.is_recording:
                response = "ERROR Recording already in progress"
            elif self.pumpkin.timeline_playback.state.value == "playing":
                response = "ERROR Cannot start recording while playback active"
            else:
                self.pumpkin.recording_session.start()
                response = "OK Recording started"
            print(response)
            return response
        
        if data.startswith("record_stop") or data.startswith("record stop"):
            try:
                # Handle both "record_stop filename" and "record stop filename"
                if data.startswith("record_stop"):
                    parts = data.split(maxsplit=1)
                    filename = parts[1] if len(parts) > 1 else None
                else:  # "record stop filename"
                    parts = data.split(maxsplit=2)
                    filename = parts[2] if len(parts) > 2 else None
                
                # Validate filename (no path separators)
                if filename and ('/' in filename or '\\' in filename):
                    response = "ERROR Invalid filename: path separators not allowed"
                    print(response)
                    return response
                
                # Check if recording is active
                if not self.pumpkin.recording_session.is_recording:
                    response = "ERROR No active recording"
                else:
                    saved_filename = self.pumpkin.recording_session.stop(filename)
                    response = f"OK Saved to {saved_filename}"
            except ValueError as e:
                response = f"ERROR {e}"
            except FileExistsError as e:
                response = f"ERROR {e}"
            except Exception as e:
                response = f"ERROR {e}"
            
            print(response)
            return response
        
        if data == "record_cancel" or data == "record cancel":
            if not self.pumpkin.recording_session.is_recording:
                response = "ERROR No active recording"
            else:
                self.pumpkin.recording_session.cancel()
                response = "OK Recording cancelled"
            print(response)
            return response
        
        # Playback commands
        if data.startswith("play "):
            try:
                parts = data.split(maxsplit=1)
                if len(parts) < 2:
                    response = "ERROR Missing filename"
                    print(response)
                    return response
                
                filename = parts[1]
                
                # Validate filename (no path separators)
                if '/' in filename or '\\' in filename:
                    response = "ERROR Invalid filename: path separators not allowed"
                    print(response)
                    return response
                
                if self.pumpkin.timeline_playback.state.value == "playing":
                    response = f"ERROR Playback already active: {self.pumpkin.timeline_playback.filename}"
                elif self.pumpkin.recording_session.is_recording:
                    response = "ERROR Cannot control playback while recording"
                else:
                    self.pumpkin.timeline_playback.play(filename)
                    duration = self.pumpkin.timeline_playback.timeline.duration_ms
                    response = f"OK Playing {self.pumpkin.timeline_playback.filename} ({duration}ms)"
            except FileNotFoundError as e:
                response = f"ERROR File not found: {filename}"
            except ValueError as e:
                response = f"ERROR Invalid timeline file: {filename}"
            except Exception as e:
                response = f"ERROR {e}"
            
            print(response)
            return response
        
        if data == "pause":
            if self.pumpkin.timeline_playback.state.value != "playing":
                response = "ERROR No active playback"
            else:
                self.pumpkin.timeline_playback.pause()
                position = int(self.pumpkin.timeline_playback.current_position_ms)
                response = f"OK Paused at {position}ms"
            print(response)
            return response
        
        if data == "resume":
            if self.pumpkin.timeline_playback.state.value != "paused":
                response = "ERROR Playback not paused"
            else:
                self.pumpkin.timeline_playback.resume()
                position = int(self.pumpkin.timeline_playback.current_position_ms)
                response = f"OK Resumed from {position}ms"
            print(response)
            return response
        
        if data == "stop":
            if self.pumpkin.timeline_playback.state.value == "stopped":
                response = "ERROR No active playback"
            else:
                self.pumpkin.timeline_playback.stop()
                response = "OK Playback stopped"
            print(response)
            return response
        
        if data.startswith("seek "):
            try:
                parts = data.split()
                if len(parts) < 2:
                    response = "ERROR Missing position argument"
                    print(response)
                    return response
                
                position_ms = int(parts[1])
                
                if self.pumpkin.timeline_playback.timeline is None:
                    response = "ERROR No timeline loaded"
                else:
                    duration = self.pumpkin.timeline_playback.timeline.duration_ms
                    if position_ms < 0 or position_ms > duration:
                        response = f"ERROR Seek position out of range (0-{duration}ms)"
                    else:
                        self.pumpkin.timeline_playback.seek(position_ms)
                        response = f"OK Seeked to {position_ms}ms"
            except ValueError:
                response = "ERROR Invalid position (must be integer milliseconds)"
            except Exception as e:
                response = f"ERROR {e}"
            
            print(response)
            return response
        
        # Help command
        if data == "help":
            help_text = (
                "Commands:\n"
                "  blink                              - Trigger a blink animation\n"
                "  wink_left                          - Trigger left eye wink animation\n"
                "  wink_right                         - Trigger right eye wink animation\n"
                "  roll_clockwise                     - Roll eyes clockwise\n"
                "  roll_counterclockwise              - Roll eyes counter-clockwise\n"
                "  gaze <h> <v>                       - Set gaze for both eyes (horizontal/vertical degrees)\n"
                "  gaze <lh> <lv> <rh> <rv>          - Set gaze independently per eye (degrees)\n"
                "  eyebrow_raise                      - Raise both eyebrows one step\n"
                "  eyebrow_lower                      - Lower both eyebrows one step\n"
                "  eyebrow_raise_left                 - Raise left eyebrow one step\n"
                "  eyebrow_lower_left                 - Lower left eyebrow one step\n"
                "  eyebrow_raise_right                - Raise right eyebrow one step\n"
                "  eyebrow_lower_right                - Lower right eyebrow one step\n"
                "  eyebrow_reset                      - Reset both eyebrows to neutral position\n"
                "  eyebrow <value>                    - Set both eyebrows to absolute offset value\n"
                "  eyebrow_left <value>               - Set left eyebrow to absolute offset value\n"
                "  eyebrow_right <value>              - Set right eyebrow to absolute offset value\n"
                "  projection_reset                   - Reset projection offset to default\n"
                "  jog_offset <dx> <dy>               - Jog projection offset by dx/dy pixels (saves to disk)\n"
                "  jog_offset_nosave <dx> <dy>        - Jog projection offset by dx/dy pixels (in memory only, no save)\n"
                "  set_offset <x> <y>                 - Set projection offset to absolute x/y pixels\n"
                "  turn_left [amount]                 - Turn head left by amount pixels (default: 50)\n"
                "  turn_right [amount]                - Turn head right by amount pixels (default: 50)\n"
                "  turn_up [amount]                   - Turn head up by amount pixels (default: 50)\n"
                "  turn_down [amount]                 - Turn head down by amount pixels (default: 50)\n"
                "  center_head                        - Center head position\n"
                "  wiggle_nose [magnitude]            - Wiggle nose (default magnitude: 50)\n"
                "  twitch_nose [magnitude]            - Twitch nose (default magnitude: 50)\n"
                "  scrunch_nose [magnitude]           - Scrunch nose (default magnitude: 50)\n"
                "  reset_nose                         - Reset nose to neutral\n"
                "  mouth_closed                       - Set mouth to closed viseme (M, B, P sounds)\n"
                "  mouth_open                         - Set mouth to open viseme (AH, AA sounds)\n"
                "  mouth_wide                         - Set mouth to wide viseme (EE, IH sounds)\n"
                "  mouth_rounded                      - Set mouth to rounded viseme (OO, OH sounds)\n"
                "  mouth_neutral                      - Release mouth to expression-driven control\n"
                "  mouth <viseme>                     - Set mouth to named viseme (closed/open/wide/rounded/neutral)\n"
                "  reset                              - Clear recording and playback state\n"
                "  record_start                       - Start recording commands\n"
                "  record_stop [filename]             - Stop recording and save (optional filename)\n"
                "  record_cancel                      - Cancel active recording without saving\n"
                "  play <filename>                    - Play a saved timeline file\n"
                "  pause                              - Pause active playback\n"
                "  resume                             - Resume paused playback\n"
                "  stop                               - Stop active playback\n"
                "  seek <ms>                          - Seek timeline to position in milliseconds\n"
                "  timeline_status                    - Get timeline and recording status (JSON)\n"
                "  recording_status                   - Get current recording status (JSON)\n"
                "  list_recordings                    - List saved timeline files (JSON)\n"
                "  list                               - Alias for list_recordings\n"
                "  delete_recording <filename>        - Delete a saved timeline file\n"
                "  rename_recording <old> <new>       - Rename a saved timeline file\n"
                "  download_timeline <filename>       - Download timeline file as JSON content\n"
                "  upload_timeline <filename>         - Upload a timeline file (enters upload mode)\n"
                "  upload_audio <filename>            - Upload an audio file (enters upload mode)\n"
                "  export_recordings                  - Export all recordings and audio files as a zip (base64)\n"
                "  import_recordings                  - Import recordings zip (enters upload mode)\n"
                "  neutral                            - Set expression to neutral\n"
                "  happy                              - Set expression to happy\n"
                "  sad                                - Set expression to sad\n"
                "  angry                              - Set expression to angry\n"
                "  surprised                          - Set expression to surprised\n"
                "  scared                             - Set expression to scared\n"
                "  sleeping                           - Set expression to sleeping\n"
                "  help                               - Show this help message"
            )
            return help_text

        # Status query commands
        if data == "timeline_status":
            status = self.pumpkin.timeline_playback.get_status()
            status["recording"] = self.pumpkin.recording_session.is_recording
            response = json.dumps(status)
            return response
        
        if data == "recording_status":
            status = {
                "is_recording": self.pumpkin.recording_session.is_recording,
                "command_count": len(self.pumpkin.recording_session.commands),
                "duration_ms": 0
            }
            if self.pumpkin.recording_session.is_recording and self.pumpkin.recording_session.start_time:
                current_time_ms = time.time() * 1000
                status["duration_ms"] = int(current_time_ms - self.pumpkin.recording_session.start_time)
            response = json.dumps(status)
            return response
        
        # File management commands
        if data == "list_recordings" or data == "list":
            recordings = self.pumpkin.timeline_playback.list_recordings()
            response = json.dumps(recordings)
            return response
        
        if data.startswith("delete_recording "):
            try:
                parts = data.split(maxsplit=1)
                if len(parts) < 2:
                    response = "ERROR Missing filename"
                    print(response)
                    return response
                
                filename = parts[1]
                
                # Validate filename (no path separators)
                if '/' in filename or '\\' in filename:
                    response = "ERROR Invalid filename: path separators not allowed"
                    print(response)
                    return response
                
                # Check if currently playing
                if self.pumpkin.timeline_playback.filename == filename or \
                   self.pumpkin.timeline_playback.filename == f"{filename}.json":
                    response = "ERROR Cannot delete file currently in playback"
                else:
                    self.pumpkin.timeline_playback.delete_recording(filename)
                    if not filename.endswith('.json'):
                        filename = f"{filename}.json"
                    response = f"OK Deleted {filename}"
            except FileNotFoundError:
                response = f"ERROR File not found: {filename}"
            except Exception as e:
                response = f"ERROR {e}"
            
            print(response)
            return response
        
        if data.startswith("rename_recording "):
            try:
                parts = data.split()
                if len(parts) < 3:
                    response = "ERROR Missing filename arguments (old_name new_name)"
                    print(response)
                    return response
                
                old_name = parts[1]
                new_name = parts[2]
                
                # Validate filenames (no path separators)
                if '/' in old_name or '\\' in old_name or '/' in new_name or '\\' in new_name:
                    response = "ERROR Invalid filename: path separators not allowed"
                    print(response)
                    return response
                
                # Check if currently playing old file
                if self.pumpkin.timeline_playback.filename == old_name or \
                   self.pumpkin.timeline_playback.filename == f"{old_name}.json":
                    response = "ERROR Cannot rename file currently in playback"
                else:
                    self.pumpkin.timeline_playback.rename_recording(old_name, new_name)
                    old_json = old_name if old_name.endswith('.json') else f"{old_name}.json"
                    new_json = new_name if new_name.endswith('.json') else f"{new_name}.json"
                    response = f"OK Renamed {old_json} to {new_json}"
            except FileNotFoundError:
                response = f"ERROR File not found: {old_name}"
            except FileExistsError:
                response = f"ERROR File already exists: {new_name}"
            except Exception as e:
                response = f"ERROR {e}"
            
            print(response)
            return response
        
        if data.startswith("download_timeline "):
            try:
                parts = data.split(maxsplit=1)
                if len(parts) < 2:
                    response = "ERROR Missing filename"
                    print(response)
                    return response
                
                filename = parts[1]
                
                # Validate filename (no path separators)
                if '/' in filename or '\\' in filename:
                    response = "ERROR Invalid filename: path separators not allowed"
                    print(response)
                    return response
                
                # Download the timeline JSON
                json_content = self.pumpkin.file_manager.download_timeline(filename)
                if not filename.endswith('.json'):
                    filename = f"{filename}.json"
                response = json_content
                print(f"Downloaded {filename}")
            except FileNotFoundError:
                response = f"ERROR File not found: {filename}"
                print(response)
            except ValueError as e:
                response = f"ERROR Invalid timeline: {e}"
                print(response)
            except Exception as e:
                response = f"ERROR {e}"
                print(response)
            return response
        
        if data.startswith("upload_timeline "):
            # Note: upload_timeline requires socket-specific multi-step protocol
            # Return special marker to signal socket handler to enter upload mode
            return "UPLOAD_MODE"

        if data == "export_recordings":
            try:
                zip_bytes = self.pumpkin.file_manager.export_recordings()
                zip_b64 = base64.b64encode(zip_bytes).decode('ascii')
                response = f"RECORDINGS_ZIP:{zip_b64}"
                print(f"Exported recordings ({len(zip_bytes)} bytes)")
            except Exception as e:
                response = f"ERROR {e}"
                print(response)
            return response

        if data == "import_recordings":
            # TCP import requires a multi-step protocol handled in pumpkin_face.py.
            # This path is reached only for WebSocket (inline base64) — the TCP
            # socket handler intercepts "import_recordings" before CommandRouter.
            return "IMPORT_RECORDINGS_MODE"

        # ===== END TIMELINE COMMANDS =====
        
        # Check for manual override during playback
        # Timeline commands don't trigger pause, but animation/expression commands do
        is_timeline_command = data in ["record_start", "record start", "record_cancel", "record cancel", 
                                       "pause", "resume", "stop", "timeline_status", 
                                       "recording_status", "list_recordings", "list",
                                       "export_recordings", "import_recordings"] or \
                             data.startswith(("record_stop", "record stop", "play ", "seek ", 
                                             "delete_recording ", "rename_recording ", "upload_timeline ", "download_timeline "))
        
        if not is_timeline_command and self.pumpkin.timeline_playback.state.value == "playing":
            self.pumpkin.timeline_playback.pause()
            print("Playback paused for manual override")
        
        # Capture command if recording (for expression commands that reach this point)
        if self.pumpkin.recording_session.is_recording and not is_timeline_command:
            self.pumpkin._capture_command_for_recording(data)
        
        # Handle expression changes
        try:
            expression = self.Expression(data)
            self.pumpkin.set_expression(expression)
            response = f"OK Expression changed to {data}"
            print(f"Expression changed to: {data}")
            return response
        except ValueError:
            response = f"ERROR Unknown expression: {data}"
            print(f"Unknown expression: {data}")
            return response
