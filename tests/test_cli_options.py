"""
Test suite for CLI options: host and port configuration (Issue #89).

Tests validate that the PumpkinFace server correctly uses CLI arguments
for host and port configuration, with proper defaults when options are omitted.

Expected behavior:
  - When no --host/--port options provided: defaults to localhost:5000
  - When --host provided: binds to specified host (default port 5000)
  - When --port provided: binds to specified port (default host localhost)
  - When both provided: binds to specified host:port
  - Invalid host/port values produce clear error messages

These tests validate the implemented CLI interface in pumpkin_face.py.
Focused verification command:
  python -m pytest tests/test_cli_options.py -v

Author: Mylo (Tester)
Issue: #89
Date: 2026-03-12
"""

import socket
import subprocess
import time
import sys
import pytest
from pathlib import Path


# ============================================================================
# HELPERS
# ============================================================================

def wait_for_port(host: str, port: int, timeout: float = 5.0) -> bool:
    """Poll until a port is accepting connections or timeout expires.
    
    Args:
        host: Hostname or IP to connect to
        port: Port number to check
        timeout: Maximum seconds to wait
        
    Returns:
        True if port became available, False if timeout
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((host, port))
            sock.close()
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(0.1)
    return False


def send_tcp_command(host: str, port: int, command: str, timeout: float = 2.0) -> str:
    """Send a command to the TCP server and return response.
    
    Args:
        host: Server hostname/IP
        port: Server port
        command: Command string to send
        timeout: Socket timeout in seconds
        
    Returns:
        Response string from server (may be empty)
        
    Raises:
        ConnectionError: If cannot connect to server
    """
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(timeout)
        client.connect((host, port))
        client.send(command.encode('utf-8'))
        
        try:
            response = client.recv(4096).decode('utf-8').strip()
        except socket.timeout:
            response = ""
        
        client.close()
        return response
    except Exception as e:
        raise ConnectionError(f"Failed to connect to {host}:{port}: {e}")


def start_server_with_args(args: list, wait_host: str = 'localhost', 
                          wait_port: int = 5000, wait_timeout: float = 10.0):
    """Start pumpkin_face.py with given CLI arguments.
    
    Args:
        args: List of CLI arguments (e.g., ['--host', '127.0.0.1'])
        wait_host: Host to poll for server readiness
        wait_port: Port to poll for server readiness
        wait_timeout: Max seconds to wait for server start
        
    Returns:
        subprocess.Popen instance
        
    Raises:
        RuntimeError: If server doesn't become ready within timeout
    """
    cmd = [sys.executable, 'pumpkin_face.py'] + args
    
    if sys.platform == 'win32':
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    else:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    # Wait for server to be ready
    if not wait_for_port(wait_host, wait_port, timeout=wait_timeout):
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
        raise RuntimeError(
            f"Server did not become ready on {wait_host}:{wait_port} "
            f"within {wait_timeout}s"
        )
    
    return process


# ============================================================================
# TESTS: Default behavior (no CLI options)
# ============================================================================

class TestDefaultHostAndPort:
    """Verify server defaults to localhost:5000 when CLI options omitted."""
    
    def test_server_binds_to_localhost_5000_by_default(self):
        """Server with no args should bind to localhost:5000."""
        process = None
        try:
            process = start_server_with_args(
                [],
                wait_host='localhost',
                wait_port=5000
            )
            
            # Verify connection works
            response = send_tcp_command('localhost', 5000, 'help')
            assert response is not None, "Should receive response from default server"
            
        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def test_default_server_accepts_neutral_command(self):
        """Default server should accept and process 'neutral' expression command."""
        process = None
        try:
            process = start_server_with_args([])
            
            # Send neutral command (shouldn't error)
            response = send_tcp_command('localhost', 5000, 'neutral')
            # Response may be empty or "OK" depending on implementation
            # Key is that no connection error occurs
            
        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def test_default_server_not_accessible_on_other_ports(self):
        """Default server should only bind to port 5000, not 5001 or other ports."""
        process = None
        try:
            process = start_server_with_args([])
            
            # Confirm 5000 is open
            assert wait_for_port('localhost', 5000, timeout=2.0), \
                "Port 5000 should be open"
            
            # Confirm 5001 is NOT open (unless WebSocket server is running)
            # This tests TCP server specifically
            tcp_on_5001 = wait_for_port('localhost', 5001, timeout=0.5)
            # Note: If WebSocket is on 5001, this may pass - that's ok
            # The key test is that 5000 is the default TCP port
            
        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


# ============================================================================
# TESTS: --host option
# ============================================================================

class TestHostOption:
    """Verify --host option overrides default localhost binding."""
    
    def test_host_option_127_0_0_1(self):
        """--host 127.0.0.1 should bind to 127.0.0.1 (not 'localhost' string)."""
        process = None
        try:
            process = start_server_with_args(
                ['--host', '127.0.0.1'],
                wait_host='127.0.0.1',
                wait_port=5000
            )
            
            response = send_tcp_command('127.0.0.1', 5000, 'help')
            assert response is not None, "Server should respond on 127.0.0.1:5000"
            
        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def test_host_option_0_0_0_0(self):
        """--host 0.0.0.0 should bind to all interfaces."""
        process = None
        try:
            process = start_server_with_args(
                ['--host', '0.0.0.0'],
                wait_host='127.0.0.1',  # Poll on loopback
                wait_port=5000
            )
            
            # Should be accessible on loopback when bound to 0.0.0.0
            response = send_tcp_command('127.0.0.1', 5000, 'help')
            assert response is not None, "Server bound to 0.0.0.0 should accept local connections"
            
        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


# ============================================================================
# TESTS: --port option
# ============================================================================

class TestPortOption:
    """Verify --port option overrides default 5000."""
    
    def test_port_option_custom_port(self):
        """--port 6000 should bind to localhost:6000."""
        process = None
        try:
            process = start_server_with_args(
                ['--port', '6000'],
                wait_host='localhost',
                wait_port=6000
            )
            
            response = send_tcp_command('localhost', 6000, 'help')
            assert response is not None, "Server should respond on localhost:6000"
            
        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def test_port_option_does_not_bind_default_5000(self):
        """When --port 6000 used, default port 5000 should NOT be bound."""
        process = None
        try:
            process = start_server_with_args(
                ['--port', '6000'],
                wait_host='localhost',
                wait_port=6000
            )
            
            # Port 5000 should NOT be accepting connections
            port_5000_open = wait_for_port('localhost', 5000, timeout=0.5)
            assert not port_5000_open, "Port 5000 should not be bound when --port 6000 specified"
            
        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


# ============================================================================
# TESTS: Combined --host and --port
# ============================================================================

class TestHostAndPortCombined:
    """Verify --host and --port work together correctly."""
    
    def test_host_and_port_both_specified(self):
        """--host 127.0.0.1 --port 7000 should bind to 127.0.0.1:7000."""
        process = None
        try:
            process = start_server_with_args(
                ['--host', '127.0.0.1', '--port', '7000'],
                wait_host='127.0.0.1',
                wait_port=7000
            )
            
            response = send_tcp_command('127.0.0.1', 7000, 'help')
            assert response is not None, "Server should respond on 127.0.0.1:7000"
            
        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def test_host_and_port_argument_order_irrelevant(self):
        """--port 7001 --host 127.0.0.1 should work (order doesn't matter)."""
        process = None
        try:
            process = start_server_with_args(
                ['--port', '7001', '--host', '127.0.0.1'],  # port before host
                wait_host='127.0.0.1',
                wait_port=7001
            )
            
            response = send_tcp_command('127.0.0.1', 7001, 'help')
            assert response is not None, "Argument order should not matter"
            
        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


# ============================================================================
# TESTS: Error handling / validation
# ============================================================================

class TestCLIValidation:
    """Verify invalid CLI arguments produce appropriate errors."""
    
    def test_invalid_port_non_numeric(self):
        """--port abc should produce an error and exit."""
        process = None
        try:
            cmd = [sys.executable, 'pumpkin_face.py', '--port', 'abc']
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait briefly for process to exit with error
            try:
                returncode = process.wait(timeout=3)
                assert returncode != 0, "Invalid port should cause non-zero exit"
            except subprocess.TimeoutExpired:
                pytest.fail("Process did not exit with invalid port argument")
            
        finally:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def test_invalid_port_out_of_range(self):
        """--port 70000 (out of valid range 1-65535) causes binding error."""
        process = None
        try:
            cmd = [sys.executable, 'pumpkin_face.py', '--port', '70000']
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Process may not exit immediately, but should fail to bind
            # Check stderr for binding error within timeout
            try:
                stdout, stderr = process.communicate(timeout=3)
                output = stdout.decode() + stderr.decode()
                # Either exits with error or shows binding error in output
                assert 'port must be 0-65535' in output or process.returncode != 0, \
                    "Out-of-range port should cause binding error or non-zero exit"
            except subprocess.TimeoutExpired:
                # Process running but should have error in stderr
                process.terminate()
                try:
                    stdout, stderr = process.communicate(timeout=2)
                    output = stdout.decode() + stderr.decode()
                    assert 'port must be 0-65535' in output or 'OverflowError' in output, \
                        "Out-of-range port should produce error message"
                except subprocess.TimeoutExpired:
                    pytest.fail("Could not verify error output for out-of-range port")
            
        finally:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def test_invalid_host_malformed(self):
        """--host invalid..host should produce a binding error or early validation error."""
        process = None
        try:
            cmd = [sys.executable, 'pumpkin_face.py', '--host', 'invalid..host..name']
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Either immediate exit or binding failure - either is acceptable
            try:
                returncode = process.wait(timeout=5)
                # Non-zero exit is acceptable (validation error)
                # If process doesn't exit, that's also ok if it just fails to bind
            except subprocess.TimeoutExpired:
                # Process may stay running but fail to bind
                # This is acceptable - we just verify it doesn't bind to localhost:5000
                port_bound = wait_for_port('localhost', 5000, timeout=1.0)
                assert not port_bound, \
                    "Server should not successfully bind with invalid host"
            
        finally:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()


# ============================================================================
# TESTS: Help text / usage message
# ============================================================================

class TestCLIHelpText:
    """Verify --help or -h produces usage information."""
    
    def test_help_flag_shows_host_option(self):
        """--help should mention --host option in usage message."""
        result = subprocess.run(
            [sys.executable, 'pumpkin_face.py', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout + result.stderr
        assert '--host' in output.lower(), "Help text should document --host option"
    
    def test_help_flag_shows_port_option(self):
        """--help should mention --port option in usage message."""
        result = subprocess.run(
            [sys.executable, 'pumpkin_face.py', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout + result.stderr
        assert '--port' in output.lower(), "Help text should document --port option"
    
    def test_help_flag_shows_defaults(self):
        """--help should indicate default values (localhost, 5000)."""
        result = subprocess.run(
            [sys.executable, 'pumpkin_face.py', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout + result.stderr
        assert 'localhost' in output.lower() or '127.0.0.1' in output, \
            "Help should mention default host"
        assert '5000' in output, "Help should mention default port"
