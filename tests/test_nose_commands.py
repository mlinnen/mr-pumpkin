#!/usr/bin/env python3
"""
Test nose animation socket commands.

Tests:
1. twitch_nose (no parameters) - should use default magnitude 50
2. twitch_nose 75 - should use magnitude 75
3. scrunch_nose (no parameters) - should use default magnitude 50
4. scrunch_nose 100 - should use magnitude 100
5. reset_nose - should reset immediately
6. Non-interrupting: twitch during twitch should be rejected
7. Non-interrupting: scrunch during scrunch should be rejected
"""

import socket
import time

def send_command(command):
    """Send a command to the pumpkin face socket server."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 5555))
        sock.sendall(command.encode('utf-8'))
        sock.close()
        print(f"✓ Sent: {command}")
        return True
    except Exception as e:
        print(f"✗ Error sending '{command}': {e}")
        return False

def test_commands():
    """Test all nose animation commands."""
    print("=" * 60)
    print("NOSE COMMAND TESTS")
    print("=" * 60)
    print()
    
    # Test 1: twitch_nose with default magnitude
    print("Test 1: twitch_nose (default magnitude)")
    send_command("twitch_nose")
    time.sleep(0.6)  # Wait for animation to complete (0.5s duration + buffer)
    print()
    
    # Test 2: twitch_nose with custom magnitude
    print("Test 2: twitch_nose 75 (custom magnitude)")
    send_command("twitch_nose 75")
    time.sleep(0.6)
    print()
    
    # Test 3: scrunch_nose with default magnitude
    print("Test 3: scrunch_nose (default magnitude)")
    send_command("scrunch_nose")
    time.sleep(0.9)  # Wait for animation to complete (0.8s duration + buffer)
    print()
    
    # Test 4: scrunch_nose with custom magnitude
    print("Test 4: scrunch_nose 100 (custom magnitude)")
    send_command("scrunch_nose 100")
    time.sleep(0.9)
    print()
    
    # Test 5: reset_nose
    print("Test 5: reset_nose")
    send_command("scrunch_nose")
    time.sleep(0.2)  # Start animation then interrupt
    send_command("reset_nose")  # Should immediately cancel
    time.sleep(0.1)
    print()
    
    # Test 6: Non-interrupting - twitch during twitch
    print("Test 6: Non-interrupting - twitch during twitch")
    send_command("twitch_nose")
    time.sleep(0.1)  # Start animation
    send_command("twitch_nose")  # Should be rejected
    print("(Second command should show 'already in progress' message)")
    time.sleep(0.6)
    print()
    
    # Test 7: Non-interrupting - scrunch during scrunch
    print("Test 7: Non-interrupting - scrunch during scrunch")
    send_command("scrunch_nose")
    time.sleep(0.1)  # Start animation
    send_command("scrunch_nose")  # Should be rejected
    print("(Second command should show 'already in progress' message)")
    time.sleep(0.9)
    print()
    
    # Test 8: Cross-animation (twitch during scrunch)
    print("Test 8: Cross-animation - twitch during scrunch")
    send_command("scrunch_nose")
    time.sleep(0.1)
    send_command("twitch_nose")  # Should be rejected
    print("(Twitch should show 'already in progress' message)")
    time.sleep(0.9)
    print()
    
    print("=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)
    print()
    print("Check pumpkin_face.py output for:")
    print("  - 'Started nose twitch' messages")
    print("  - 'Started nose scrunch' messages")
    print("  - 'Nose reset to neutral' messages")
    print("  - 'Nose animation already in progress' messages")

if __name__ == "__main__":
    print()
    print("Make sure pumpkin_face.py is running before starting tests!")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    print()
    
    test_commands()
