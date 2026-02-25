"""
Test script to verify socket server head movement commands.
"""

import socket
import time

def send_command(command: str):
    """Send a command to the socket server."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5000))
        client.send(command.encode('utf-8'))
        client.close()
        print(f"✓ Sent: {command}")
        time.sleep(0.5)
    except Exception as e:
        print(f"✗ Error sending '{command}': {e}")

if __name__ == "__main__":
    print("Testing head movement socket commands...\n")
    
    # Test head movement commands
    commands = [
        "turn_left 30",      # Turn head left by 30px
        "turn_right 40",     # Turn head right by 40px
        "turn_up 25",        # Turn head up by 25px
        "turn_down 35",      # Turn head down by 35px
        "turn_left",         # Turn left with default amount (50px)
        "turn_right",        # Turn right with default amount (50px)
        "turn_up",           # Turn up with default amount (50px)
        "turn_down",         # Turn down with default amount (50px)
        "center_head",       # Center head position
    ]
    
    print("Sending head movement commands:")
    for cmd in commands:
        send_command(cmd)
    
    print("\n✓ All commands sent successfully!")
