"""Test socket commands for rolling eyes."""

import socket
import time

def send_command(command: str):
    """Send command to pumpkin face server."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5000))
        client.send(command.encode('utf-8'))
        client.close()
        print(f"✓ Sent: {command}")
        return True
    except Exception as e:
        print(f"✗ Error sending {command}: {e}")
        return False

if __name__ == "__main__":
    print("Testing socket commands for rolling eyes")
    print("(Make sure pumpkin_face.py is running in another terminal)\n")
    
    time.sleep(1)
    
    # Test clockwise roll
    if send_command("roll_clockwise"):
        print("  Waiting for animation to complete...")
        time.sleep(1.5)
    
    # Test counter-clockwise roll
    if send_command("roll_counterclockwise"):
        print("  Waiting for animation to complete...")
        time.sleep(1.5)
    
    # Test roll + blink coordination
    print("\nTesting roll + blink coordination:")
    send_command("roll_clockwise")
    time.sleep(0.3)  # Let roll start
    send_command("blink")  # Blink should pause rolling
    print("  Blink triggered mid-roll - rolling should pause then resume")
    time.sleep(2.0)
    
    print("\n✅ Socket command tests complete!")
    print("Visual verification needed for actual animation behavior.")
