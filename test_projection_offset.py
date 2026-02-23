"""
Test script for projection offset functionality.
Tests the backend command interface for projection alignment/jog.
"""
import socket
import time

def send_command(command):
    """Send a command to the pumpkin face server."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5000))
        client.send(command.encode('utf-8'))
        client.close()
        print(f"✓ Sent: {command}")
        time.sleep(0.2)  # Small delay between commands
    except Exception as e:
        print(f"✗ Error sending '{command}': {e}")

def test_projection_offset_commands():
    """Test all projection offset commands."""
    print("\n=== Testing Projection Offset Backend ===\n")
    
    print("1. Testing jog_offset command (relative positioning):")
    send_command("jog_offset 10 5")  # Move right 10, down 5
    send_command("jog_offset -5 10")  # Move left 5, down 10
    send_command("jog_offset 0 -15")  # Move up 15
    
    print("\n2. Testing set_offset command (absolute positioning):")
    send_command("set_offset 50 -30")  # Set to x=50, y=-30
    send_command("set_offset 0 0")  # Return to center
    
    print("\n3. Testing boundary clamping (should clamp at ±500):")
    send_command("set_offset 600 -700")  # Should clamp to (500, -500)
    send_command("jog_offset 100 100")  # Should stay at limits
    
    print("\n4. Testing reset command:")
    send_command("projection_reset")  # Should return to (0, 0)
    
    print("\n5. Testing edge case - invalid arguments:")
    send_command("jog_offset abc def")  # Should error gracefully
    send_command("set_offset 100")  # Missing Y argument
    
    print("\n✓ All test commands sent successfully!")
    print("Check the server console for actual offset values and error messages.\n")

if __name__ == "__main__":
    print("\nNOTE: This test requires pumpkin_face.py to be running.")
    print("Start it with: python pumpkin_face.py --window\n")
    
    response = input("Is the pumpkin face server running? (y/n): ")
    if response.lower() == 'y':
        test_projection_offset_commands()
    else:
        print("\nPlease start the server first, then run this test again.")
