"""
Simple verification script to demonstrate the recording bug fix.

This script shows that all commands (blink, happy, gaze, etc.) are now
being captured during recording.

Run this after starting the server with: python pumpkin_face.py --window
"""

import socket
import time
import json
from pathlib import Path

def send_command(cmd):
    """Send a command to the server"""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('localhost', 5000))
        client.send(cmd.encode('utf-8'))
        client.settimeout(1.0)
        try:
            response = client.recv(4096).decode('utf-8').strip()
            return response
        except socket.timeout:
            return None
    finally:
        client.close()

def main():
    print("Testing Recording Bug Fix")
    print("=" * 60)
    
    # Start recording
    print("\n1. Starting recording...")
    response = send_command("record start")
    print(f"   Response: {response}")
    time.sleep(0.5)
    
    # Send various commands
    print("\n2. Sending commands...")
    commands = [
        ("happy", "expression command"),
        ("blink", "animation command"),
        ("roll_clockwise", "rolling eyes command"),
        ("gaze 45 30", "gaze command"),
        ("eyebrow_raise", "eyebrow command"),
    ]
    
    for cmd, desc in commands:
        send_command(cmd)
        print(f"   - Sent {cmd} ({desc})")
        time.sleep(0.2)
    
    # Check status
    print("\n3. Checking recording status...")
    response = send_command("recording_status")
    if response:
        status = json.loads(response)
        print(f"   Commands captured: {status['command_count']}")
        print(f"   Duration: {status['duration_ms']}ms")
        
        if status['command_count'] == len(commands):
            print("   ✅ All commands captured!")
        elif status['command_count'] == 0:
            print("   ❌ BUG: No commands were captured")
        else:
            print(f"   ⚠️  WARNING: Expected {len(commands)}, got {status['command_count']}")
    
    # Stop and save
    print("\n4. Stopping recording...")
    response = send_command("record stop demo_recording")
    print(f"   Response: {response}")
    
    # Verify file
    print("\n5. Verifying saved file...")
    recordings_dir = Path.home() / '.mr-pumpkin' / 'recordings'
    demo_file = recordings_dir / 'demo_recording.json'
    
    if demo_file.exists():
        with open(demo_file, 'r') as f:
            timeline = json.load(f)
        
        saved_commands = timeline.get('commands', [])
        print(f"   File created: {demo_file}")
        print(f"   Commands in file: {len(saved_commands)}")
        
        for i, cmd in enumerate(saved_commands):
            print(f"      [{i}] {cmd['time_ms']}ms: {cmd['command']} {cmd.get('args', {})}")
        
        if saved_commands:
            print("\n✅ BUG FIX VERIFIED: Commands are being recorded correctly!")
        else:
            print("\n❌ BUG STILL EXISTS: File is empty")
        
        # Clean up
        demo_file.unlink()
        print(f"\nCleaned up test file: {demo_file.name}")
    else:
        print(f"   ❌ File not found: {demo_file}")

if __name__ == "__main__":
    print("This test requires the server to be running.")
    print("Start with: python pumpkin_face.py --window\n")
    input("Press Enter when ready...")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
