"""
Quick test to verify "record stop" command works.
This tests the fix for the bug where "record stop <filename>" wasn't being recognized.
"""

import time
import socket
import tempfile
import os
from pathlib import Path

def send_command(command: str) -> str:
    """Send command to server and get response."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(2.0)
        client.connect(('localhost', 5000))
        client.send(command.encode('utf-8'))
        
        # Read response
        response = client.recv(4096).decode('utf-8').strip()
        client.close()
        return response
    except Exception as e:
        return f"ERROR: {e}"

def test_record_stop_variants():
    """Test both 'record stop' and 'record_stop' command variants."""
    
    print("Testing recording commands with both space and underscore variants...")
    print()
    
    # Test 1: record_start (underscore variant)
    print("Test 1: Sending 'record_start'")
    response = send_command("record_start")
    print(f"  Response: {response}")
    assert "OK" in response, f"Expected OK, got: {response}"
    time.sleep(0.1)
    
    # Send a command to record
    print("Test 2: Sending 'happy' command")
    send_command("happy")
    time.sleep(0.1)
    
    # Test 3: record_stop with underscore
    test_filename = f"test_underscore_{int(time.time())}"
    print(f"Test 3: Sending 'record_stop {test_filename}'")
    response = send_command(f"record_stop {test_filename}")
    print(f"  Response: {response}")
    assert "OK" in response and test_filename in response, f"Expected OK with filename, got: {response}"
    
    # Verify file was created
    recordings_dir = Path.home() / '.mr-pumpkin' / 'recordings'
    saved_file = recordings_dir / f"{test_filename}.json"
    assert saved_file.exists(), f"File not created: {saved_file}"
    print(f"  ✓ File created: {saved_file}")
    saved_file.unlink()  # Clean up
    
    print()
    
    # Test 4: record start (space variant)
    print("Test 4: Sending 'record start' (with space)")
    response = send_command("record start")
    print(f"  Response: {response}")
    assert "OK" in response, f"Expected OK, got: {response}"
    time.sleep(0.1)
    
    # Send a command to record
    print("Test 5: Sending 'neutral' command")
    send_command("neutral")
    time.sleep(0.1)
    
    # Test 6: record stop with space
    test_filename2 = f"test_space_{int(time.time())}"
    print(f"Test 6: Sending 'record stop {test_filename2}' (with space)")
    response = send_command(f"record stop {test_filename2}")
    print(f"  Response: {response}")
    assert "OK" in response and test_filename2 in response, f"Expected OK with filename, got: {response}"
    
    # Verify file was created
    saved_file2 = recordings_dir / f"{test_filename2}.json"
    assert saved_file2.exists(), f"File not created: {saved_file2}"
    print(f"  ✓ File created: {saved_file2}")
    saved_file2.unlink()  # Clean up
    
    print()
    print("✓ All tests passed! Both 'record stop' and 'record_stop' work correctly.")

if __name__ == "__main__":
    print("=" * 70)
    print("Testing 'record stop' command fix")
    print("=" * 70)
    print()
    print("IMPORTANT: Make sure the pumpkin_face server is running!")
    print("  Run: python pumpkin_face.py")
    print()
    input("Press Enter when server is ready...")
    print()
    
    try:
        test_record_stop_variants()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Make sure the server is running: python pumpkin_face.py")
        exit(1)
