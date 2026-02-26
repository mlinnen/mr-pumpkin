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
"""

import socket
import json

def send_command(command: str):
    """Send command and handle response (for recording/status commands)"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5000))
        client.send(command.encode('utf-8'))
        
        # For commands that return JSON responses, read the response
        if command in ["recording_status", "list_recordings"] or command == "list":
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
            except json.JSONDecodeError:
                print(f"Response: {response}")
        else:
            client.close()
            print(f"Sent: {command}")
    except Exception as e:
        print(f"Error: {e}")

def send_expression(expression: str):
    """Legacy wrapper for backward compatibility"""
    send_command(expression)

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
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("Enter command: ").strip()
        if user_input.lower() == 'quit':
            break
        if user_input:
            # Handle special case: 'record status' → 'recording_status'
            if user_input == "record status":
                send_command("recording_status")
            else:
                send_command(user_input)
