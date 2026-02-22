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
"""

import socket

def send_expression(expression: str):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5000))
        client.send(expression.encode('utf-8'))
        client.close()
        print(f"Sent: {expression}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Pumpkin Face Client")
    print("Valid expressions: neutral, happy, sad, angry, surprised, scared, sleeping")
    print("Animation commands: blink, roll_clockwise, roll_counterclockwise")
    print("Gaze command: gaze <x> <y> [<x2> <y2>]")
    print("  Examples: 'gaze 45 30' (both eyes), 'gaze -90 0 90 45' (independent)")
    print("Type 'quit' to exit\n")
    
    while True:
        expression = input("Enter expression: ").strip()
        if expression.lower() == 'quit':
            break
        if expression:
            send_expression(expression)
