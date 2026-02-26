"""
Test that the 'list' command works without hanging.
"""

import socket
import json
import time

def test_list_command():
    """Test that 'list' command returns a response and doesn't hang."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(2.0)  # 2 second timeout to detect hangs
        client.connect(('localhost', 5000))
        
        # Send 'list' command
        client.send(b'list')
        
        # Try to receive response
        response = client.recv(4096).decode('utf-8').strip()
        client.close()
        
        # Parse JSON
        data = json.loads(response)
        
        print(f"✓ 'list' command succeeded!")
        print(f"  Response type: {type(data)}")
        print(f"  Number of recordings: {len(data)}")
        if data:
            print(f"  First recording: {data[0]['filename']}")
        
        return True
        
    except socket.timeout:
        print("✗ FAILED: Socket timeout - command hung!")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ FAILED: Invalid JSON response: {e}")
        print(f"  Response was: {response}")
        return False
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

if __name__ == "__main__":
    print("Testing 'list' command...")
    print("Note: This test requires pumpkin_face.py to be running on localhost:5000")
    print()
    
    success = test_list_command()
    
    if success:
        print("\n✓ Test passed!")
    else:
        print("\n✗ Test failed!")
