"""
Interactive test script for animated head movement (Issue #17).
Tests the smooth 3D head movement illusion created by animating projection offset.
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
        time.sleep(0.6)  # Wait for 0.5s animation + buffer
    except Exception as e:
        print(f"✗ Error sending '{command}': {e}")

def test_animated_head_movement():
    """Test smooth animated head movements."""
    print("\n=== Testing Animated 3D Head Movement ===\n")
    
    print("1. Testing basic head turns (default 50px):")
    send_command("turn_left")
    send_command("center_head")
    send_command("turn_right")
    send_command("center_head")
    send_command("turn_up")
    send_command("center_head")
    send_command("turn_down")
    send_command("center_head")
    
    print("\n2. Testing custom amounts:")
    send_command("turn_left 100")
    send_command("center_head")
    send_command("turn_right 75")
    send_command("center_head")
    
    print("\n3. Testing smooth movement sequence:")
    send_command("turn_left 60")
    send_command("turn_right 120")  # Should move from -60 to +60
    send_command("center_head")
    
    print("\n4. Testing with expressions:")
    send_command("happy")
    time.sleep(0.3)
    send_command("turn_left 50")
    send_command("turn_right 100")
    send_command("center_head")
    
    send_command("neutral")
    
    print("\n✓ All animated head movement tests completed!")
    print("The head should move smoothly with ease-in-out animation.\n")

if __name__ == "__main__":
    print("\nNOTE: This test requires pumpkin_face.py to be running.")
    print("Start it with: python pumpkin_face.py --window\n")
    
    response = input("Is the pumpkin face server running? (y/n): ")
    if response.lower() == 'y':
        test_animated_head_movement()
    else:
        print("\nPlease start the server first, then run this test again.")
