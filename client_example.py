"""
Example client to send commands to the pumpkin face server.

Usage:
    python client_example.py
    Then type an expression: neutral, happy, sad, angry, surprised, scared
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
    print("Valid expressions: neutral, happy, sad, angry, surprised, scared")
    print("Type 'quit' to exit\n")
    
    while True:
        expression = input("Enter expression: ").strip()
        if expression.lower() == 'quit':
            break
        if expression:
            send_expression(expression)
