---
name: "multiline-socket-protocol"
description: "Pattern for reliably transmitting multi-line data (JSON, text blocks) over line-based socket protocols"
domain: "networking, protocols, socket communication"
confidence: "low"
source: "earned"
---

## Context

Line-based socket protocols (where data is framed by newline characters) work well for simple commands, but become problematic when transmitting data that contains embedded newlines (JSON, multi-line text, binary data). This pattern enables reliable multi-line transmission using explicit handshake signals.

Applicable to:
- Uploading/downloading configuration files in JSON format
- Transmitting multi-line text data (logs, documents, etc.)
- Sending structured data blocks over TCP
- Any scenario where data size/structure is unknown at protocol design time

## Patterns

### 1. Handshake-Based Protocol

Instead of trying to frame JSON on a single line, use explicit signals to bracket the data:

```
Client → Server: COMMAND <args>
Server → Client: READY
Client → Server: <data line 1>
Client → Server: <data line 2>
Client → Server: ...
Client → Server: <data line N>
Client → Server: END_MARKER
Server → Client: OK <response>
```

**Why this works:**
- Each line is still properly delimited by newlines (socket.recv() works correctly)
- Data can contain any characters, including newlines
- Server knows when to stop reading (END_MARKER signal)
- Explicit READY signal allows server preparation before data arrives
- Clear flow for error handling at each stage

### 2. Server-Side Implementation

```python
def handle_upload(self, client_socket, data):
    """Handle multi-line data upload with handshake protocol."""
    try:
        # Parse command and extract filename
        parts = data.split(maxsplit=1)
        if len(parts) < 2:
            client_socket.sendall(b"ERROR Missing filename\n")
            return
        
        filename = parts[1]
        
        # Signal readiness
        client_socket.sendall(b"READY\n")
        
        # Read lines until END_MARKER
        lines = []
        while True:
            line = client_socket.recv(4096).decode('utf-8').strip()
            
            if not line:
                # Empty recv = connection closed
                client_socket.sendall(b"ERROR Connection lost\n")
                break
            
            if line == "END_MARKER":
                # Process complete data
                content = '\n'.join(lines)
                try:
                    # Validate and save
                    self.process_data(filename, content)
                    response = f"OK Saved {filename}"
                except ValidationError as e:
                    response = f"ERROR {e}"
                finally:
                    client_socket.sendall((response + '\n').encode('utf-8'))
                break
            
            lines.append(line)
    
    except Exception as e:
        client_socket.sendall(f"ERROR {e}\n".encode('utf-8'))
```

### 3. Client-Side Implementation

```python
def upload_data(self, filename, file_path):
    """Upload multi-line data to server."""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Connect to server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5000))
        
        # Send command with filename
        client.send(f"upload_data {filename}\n".encode('utf-8'))
        
        # Wait for READY signal
        response = client.recv(1024).decode('utf-8').strip()
        if response != "READY":
            print(f"Error: Server not ready. Got: {response}")
            client.close()
            return
        
        # Send data content
        client.send(content.encode('utf-8'))
        client.send(b"\n")  # Ensure newline before marker
        
        # Send end marker
        client.send(b"END_MARKER\n")
        
        # Get response
        response = client.recv(1024).decode('utf-8').strip()
        client.close()
        
        print(f"Response: {response}")
    
    except Exception as e:
        print(f"Error uploading data: {e}")
```

### 4. Choosing Marker Strings

**Good markers:**
- `END_UPLOAD` — Explicit and descriptive
- `END_MARKER` — Generic but clear
- `__END__` — Unlikely to appear in normal data
- Use uppercase to distinguish from data content

**Avoid:**
- ❌ `END` — Too generic, likely in data
- ❌ `DONE` — Common word, data collision risk
- ❌ Empty line — Some data may legitimately have empty lines

### 5. Handling Incomplete Transmission

Always validate data completeness:

```python
def validate_transmission(self, lines, expected_format):
    """Verify we got all expected data before processing."""
    if not lines:
        raise ValueError("No data received (connection closed?)")
    
    try:
        data = '\n'.join(lines)
        # Validate structure (JSON syntax, file format, etc.)
        parsed = json.loads(data)
        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
```

## Examples

### Example 1: Recording File Upload (Issue #44)

```python
# Server
if data.startswith("upload_timeline "):
    parts = data.split(maxsplit=1)
    filename = parts[1]
    client_socket.sendall(b"READY\n")
    
    json_lines = []
    while True:
        line = client_socket.recv(4096).decode('utf-8').strip()
        if not line:
            client_socket.sendall(b"ERROR Connection lost\n")
            break
        if line == "END_UPLOAD":
            json_content = '\n'.join(json_lines)
            self.file_manager.upload_timeline(filename, json_content)
            client_socket.sendall(b"OK Uploaded\n")
            break
        json_lines.append(line)

# Client
def upload_timeline(filename, json_file_path):
    with open(json_file_path, 'r') as f:
        json_content = f.read()
    
    client = socket.socket()
    client.connect(('localhost', 5000))
    client.send(f"upload_timeline {filename}\n".encode())
    assert client.recv(1024).decode().strip() == "READY"
    
    client.send(json_content.encode())
    client.send(b"\nEND_UPLOAD\n")
    response = client.recv(1024).decode().strip()
    print(response)
    client.close()
```

## Anti-Patterns

### ❌ Don't try to frame multi-line data on a single line
```python
# BAD: Breaks if JSON contains newlines
client.send(json_string.encode())  # Line is incomplete if JSON multi-line
```

```python
# GOOD: Use explicit end marker
client.send(json_string.encode())
client.send(b"\nEND_UPLOAD\n")
```

### ❌ Don't assume READY arrival means data can be sent immediately
```python
# BAD: Race condition if server hasn't allocated buffer
client.send(command)
time.sleep(0.1)  # Brittle timing dependency
client.send(data)
```

```python
# GOOD: Wait for READY response before sending data
client.send(command)
response = client.recv(1024)  # Blocking wait for READY
assert response.strip() == b"READY"
client.send(data)
```

### ❌ Don't use end markers that could appear in data
```python
# BAD: "\n" could legitimately appear in JSON
if line == "\n":
    break
```

```python
# GOOD: Use unlikely-to-collide marker
if line == "END_UPLOAD":
    break
```

### ❌ Don't forget to handle connection loss
```python
# BAD: Infinite loop if client disconnects
while True:
    line = client_socket.recv(4096).decode('utf-8').strip()
    if line == "END_MARKER":
        break
    lines.append(line)
    # What if recv() returns empty? Infinite loop!
```

```python
# GOOD: Detect and handle disconnection
while True:
    line = client_socket.recv(4096).decode('utf-8').strip()
    if not line:
        raise ConnectionError("Client disconnected")
    if line == "END_MARKER":
        break
    lines.append(line)
```

### ❌ Don't accumulate unbounded data in memory
```python
# BAD: Large files cause memory overflow
lines = []
while True:
    line = client_socket.recv(4096)
    if line == b"END_MARKER\n":
        break
    lines.append(line)  # Could be gigabytes in memory
```

```python
# GOOD: Stream or limit accumulation
lines = []
max_lines = 100000
while True:
    if len(lines) > max_lines:
        raise ValueError("Data too large")
    line = client_socket.recv(4096)
    if line == b"END_MARKER\n":
        break
    lines.append(line)
```

## Security Considerations

- **Buffer overflow:** Implement max data limits to prevent DoS
- **Path traversal:** Validate filenames don't contain `../` or `..\\`
- **Validation:** Always validate received data structure before processing
- **Timeouts:** Consider socket timeouts to prevent hanging on incomplete data
- **Authentication:** This pattern assumes socket is already authenticated

## Related Patterns

- **Socket command parsing:** Prerequisite for implementing protocol handlers
- **Data validation:** Critical for processing received multi-line data
- **Error handling:** Each handshake stage should have clear error paths
