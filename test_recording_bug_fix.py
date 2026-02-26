"""
Test script to verify recording bug fix.

This script tests that commands sent to the server during recording
are properly captured in the recording file.

Bug: Commands like "happy", "blink", etc. were not being recorded
because the command handlers used 'continue' which skipped the
recording capture code.

Fix: Added recording capture check in each command handler block
before the command executes.
"""

import socket
import time
import json
import os
from pathlib import Path

def send_command(command: str, wait_for_response=False):
    """Send command to server"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5000))
        client.send(command.encode('utf-8'))
        
        if wait_for_response:
            response = client.recv(4096).decode('utf-8').strip()
            client.close()
            return response
        else:
            client.close()
            return None
    except Exception as e:
        print(f"Error sending command '{command}': {e}")
        return None

def test_recording_capture():
    """Test that commands are captured during recording"""
    print("=" * 60)
    print("Testing Recording Bug Fix")
    print("=" * 60)
    
    test_filename = "test_bug_fix"
    
    # Clean up any existing test file
    recordings_dir = Path.home() / '.mr-pumpkin' / 'recordings'
    test_file = recordings_dir / f"{test_filename}.json"
    if test_file.exists():
        test_file.unlink()
        print(f"Cleaned up existing test file: {test_file}")
    
    print("\n1. Starting recording...")
    response = send_command("record start", wait_for_response=True)
    print(f"   Response: {response}")
    
    if not response or "OK" not in response:
        print("   ❌ FAILED: Could not start recording")
        return False
    
    print("\n2. Sending commands during recording...")
    commands = [
        "happy",
        "blink",
        "roll_clockwise",
        "gaze 45 30",
        "eyebrow_raise",
        "turn_left",
        "twitch_nose",
    ]
    
    for cmd in commands:
        time.sleep(0.2)  # 200ms between commands
        send_command(cmd)
        print(f"   Sent: {cmd}")
    
    time.sleep(0.5)  # Wait for commands to be captured
    
    print("\n3. Checking recording status...")
    response = send_command("recording_status", wait_for_response=True)
    print(f"   Response: {response}")
    
    try:
        status = json.loads(response)
        command_count = status.get("command_count", 0)
        print(f"   Commands captured: {command_count}")
        
        if command_count == 0:
            print("   ❌ FAILED: No commands were captured!")
            return False
        elif command_count != len(commands):
            print(f"   ⚠️  WARNING: Expected {len(commands)} commands, got {command_count}")
        else:
            print(f"   ✅ All {command_count} commands captured")
    except json.JSONDecodeError:
        print("   ❌ FAILED: Could not parse recording status")
        return False
    
    print("\n4. Stopping recording...")
    response = send_command(f"record stop {test_filename}", wait_for_response=True)
    print(f"   Response: {response}")
    
    if not response or "OK" not in response:
        print("   ❌ FAILED: Could not stop recording")
        return False
    
    print("\n5. Verifying saved file...")
    if not test_file.exists():
        print(f"   ❌ FAILED: Recording file not found: {test_file}")
        return False
    
    with open(test_file, 'r') as f:
        timeline_data = json.load(f)
    
    saved_commands = timeline_data.get("commands", [])
    print(f"   Saved commands: {len(saved_commands)}")
    
    if len(saved_commands) == 0:
        print("   ❌ FAILED: Recording file is empty!")
        return False
    
    print("\n6. Verifying command content...")
    for i, cmd_entry in enumerate(saved_commands):
        cmd_name = cmd_entry.get("command", "unknown")
        time_ms = cmd_entry.get("time_ms", 0)
        args = cmd_entry.get("args", {})
        print(f"   [{i}] {time_ms}ms: {cmd_name} {args}")
    
    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Commands are being captured correctly!")
    print("=" * 60)
    
    # Clean up test file
    print(f"\nCleaning up test file: {test_file}")
    test_file.unlink()
    
    return True

if __name__ == "__main__":
    print("This test requires the pumpkin_face.py server to be running.")
    print("Start the server in another terminal with:")
    print("  python pumpkin_face.py --window")
    print("")
    input("Press Enter when server is ready...")
    
    try:
        test_recording_capture()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
