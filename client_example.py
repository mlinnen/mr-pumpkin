"""
Example client to send commands to the pumpkin face server.

Usage:
    python client_example.py
    Then type an expression: neutral, happy, sad, angry, surprised, scared, sleeping
    Or animation commands: blink, roll_clockwise, roll_counterclockwise
    Or gaze command: gaze <x> <y> [<x2> <y2>]
      - 2 args: both eyes look at same angle
      - 4 args: left eye (x1,y1), right eye (x2,y2)
      - Angles: -90 to +90 degrees (0=straight, +X=right, +Y=up)
    Or recording commands:
      - record start: Begin recording commands
      - record stop <filename>: Save recording with given filename
      - record cancel: Discard current recording
      - record status: Show recording state (is_recording, command_count, duration_ms)
      - list: Show available recordings
    Or playback commands:
      - play <filename>: Start playing a recording
      - pause: Pause current playback
      - resume: Resume from paused state
      - stop: Stop playback
      - seek <position_ms>: Jump to position in recording
      - timeline_status: Show playback state (state, filename, position, duration)
    Or file upload:
      - upload_timeline <filename> <json_file>: Upload a recording file
"""

import socket
import json
import os

def send_command(command: str):
    """Send command and handle response (for recording/status/playback commands)"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5000))
        client.send(command.encode('utf-8'))
        
        # For commands that return JSON responses, read the response
        if command in ["recording_status", "list_recordings", "timeline_status"] or command == "list":
            response = client.recv(4096).decode('utf-8').strip()
            client.close()
            
            # Handle 'list' as alias for 'list_recordings'
            actual_command = "list_recordings" if command == "list" else command
            
            try:
                data = json.loads(response)
                if actual_command == "recording_status":
                    print(f"Recording Status:")
                    print(f"  Is Recording: {data['is_recording']}")
                    print(f"  Commands Captured: {data['command_count']}")
                    print(f"  Duration: {data['duration_ms']} ms")
                elif actual_command == "list_recordings":
                    print(f"Available Recordings:")
                    if not data:
                        print("  (none)")
                    else:
                        for rec in data:
                            print(f"  - {rec['filename']}: {rec['command_count']} commands, {rec['duration_ms']} ms")
                elif actual_command == "timeline_status":
                    print(f"Playback Status:")
                    print(f"  State: {data['state']}")
                    print(f"  Filename: {data.get('filename', '(none)')}")
                    print(f"  Position: {data['position_ms']} ms")
                    print(f"  Duration: {data['duration_ms']} ms")
                    print(f"  Is Playing: {data['is_playing']}")
                    if data.get('is_recording'):
                        print(f"  Recording: Active")
            except json.JSONDecodeError:
                print(f"Response: {response}")
        else:
            response = client.recv(1024).decode('utf-8').strip()
            client.close()
            if response:
                print(f"Response: {response}")
            else:
                print(f"Sent: {command}")
    except Exception as e:
        print(f"Error: {e}")

def send_expression(expression: str):
    """Legacy wrapper for backward compatibility"""
    send_command(expression)

def upload_timeline(filename: str, json_file_path: str):
    """Upload a recording file to the server.
    
    Args:
        filename: Name to save the recording as on the server
        json_file_path: Local path to JSON file to upload
    """
    if not os.path.exists(json_file_path):
        print(f"Error: File not found: {json_file_path}")
        return
    
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_content = f.read()
        
        # Connect to server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5000))
        
        # Send upload request
        upload_cmd = f"upload_timeline {filename}\n"
        client.send(upload_cmd.encode('utf-8'))
        
        # Wait for READY signal
        response = client.recv(1024).decode('utf-8').strip()
        if response != "READY":
            print(f"Error: Server did not send READY signal. Got: {response}")
            client.close()
            return
        
        # Send JSON content
        client.send(json_content.encode('utf-8'))
        client.send(b"\n")
        
        # Send end marker
        client.send(b"END_UPLOAD\n")
        
        # Get response
        response = client.recv(1024).decode('utf-8').strip()
        client.close()
        
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error uploading timeline: {e}")

if __name__ == "__main__":
    print("Pumpkin Face Client")
    print("Valid expressions: neutral, happy, sad, angry, surprised, scared, sleeping")
    print("Animation commands: blink, roll_clockwise, roll_counterclockwise")
    print("Gaze command: gaze <x> <y> [<x2> <y2>]")
    print("  Examples: 'gaze 45 30' (both eyes), 'gaze -90 0 90 45' (independent)")
    print("Recording commands:")
    print("  record start - Begin recording")
    print("  record stop <filename> - Save recording")
    print("  record cancel - Discard recording")
    print("  record status - Show recording state")
    print("  list - Show available recordings")
    print("Playback commands:")
    print("  play <filename> - Start playing a recording")
    print("  pause - Pause playback")
    print("  resume - Resume from paused state")
    print("  stop - Stop playback")
    print("  seek <position_ms> - Jump to position in recording")
    print("  timeline_status - Show playback state")
    print("File upload:")
    print("  upload_timeline <server_filename> <local_json_file> - Upload a recording file")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("Enter command: ").strip()
        if user_input.lower() == 'quit':
            break
        if user_input:
            # Handle special case: 'record status' → 'recording_status'
            if user_input == "record status":
                send_command("recording_status")
            # Handle upload_timeline with two arguments
            elif user_input.startswith("upload_timeline "):
                parts = user_input.split(maxsplit=2)
                if len(parts) < 3:
                    print("Error: upload_timeline requires two arguments: server_filename local_json_file")
                else:
                    upload_timeline(parts[1], parts[2])
            else:
                send_command(user_input)
