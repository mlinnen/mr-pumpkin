"""
Timeline upload client for Mr. Pumpkin.

Supports both TCP (multi-step handshake) and WebSocket (single-message) protocols.
WebSocket support is optional — falls back to TCP if the ``websockets`` package is
not installed.

Usage:
    from skill.uploader import upload_timeline
    upload_timeline("my_show", timeline_dict)
"""

import importlib.util
import json
import socket
import warnings

_TIMEOUT = 10  # seconds


def _upload_tcp(filename: str, json_string: str, host: str, port: int) -> None:
    """Upload a timeline via the TCP multi-step handshake protocol.

    Protocol:
        1. Connect
        2. Send ``upload_timeline <filename>\\n``
        3. Wait for ``READY``
        4. Send JSON string + ``\\n``
        5. Send ``END_UPLOAD\\n``
        6. Read final response
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(_TIMEOUT)
    try:
        client.connect((host, port))

        client.sendall(f"upload_timeline {filename}\n".encode("utf-8"))

        ready = _recv_line(client)
        if ready != "READY":
            raise ValueError(f"Expected READY from server, got: {ready!r}")

        client.sendall(json_string.encode("utf-8"))
        client.sendall(b"\n")
        client.sendall(b"END_UPLOAD\n")

        response = _recv_line(client)
    finally:
        client.close()

    if response.startswith("ERROR"):
        raise ValueError(response)


def _recv_line(sock: socket.socket) -> str:
    """Read bytes from ``sock`` until a newline and return the stripped line."""
    buf = b""
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        buf += chunk
        if b"\n" in buf:
            break
    return buf.decode("utf-8").strip()


async def _upload_ws_async(filename: str, json_string: str, host: str, port: int) -> None:
    """Async WebSocket upload (single-message format)."""
    import websockets  # type: ignore

    uri = f"ws://{host}:{port}"
    async with websockets.connect(uri, open_timeout=_TIMEOUT) as ws:
        message = f"upload_timeline {filename} {json_string}"
        await ws.send(message)
        response = await ws.recv()

    response = response.strip() if isinstance(response, str) else response.decode().strip()
    if response.startswith("ERROR"):
        raise ValueError(response)


def _upload_ws(filename: str, json_string: str, host: str, port: int) -> None:
    """Synchronous wrapper around the async WebSocket upload."""
    import asyncio
    asyncio.run(_upload_ws_async(filename, json_string, host, port))


def upload_timeline(
    filename: str,
    timeline_dict: dict,
    host: str = "localhost",
    tcp_port: int = 5000,
    ws_port: int = 5001,
    protocol: str = "tcp",
) -> None:
    """Upload a timeline dict to the Mr. Pumpkin server.

    Args:
        filename: Name to store the recording as on the server (without ``.json``
            extension — the server will add it).
        timeline_dict: Validated timeline dict (as returned by ``generate_timeline``).
        host: Hostname or IP address of the Mr. Pumpkin server.
        tcp_port: TCP server port (default 5000).
        ws_port: WebSocket server port (default 5001).
        protocol: ``"tcp"`` or ``"ws"`` / ``"websocket"``.  If ``"ws"`` is
            requested but the ``websockets`` package is not installed, falls
            back to TCP with a warning.

    Raises:
        ValueError: If the server returns an error response (including duplicate
            filename errors).
        ConnectionError: If the connection to the server cannot be established.
    """
    json_string = json.dumps(timeline_dict)

    use_ws = protocol.lower() in ("ws", "websocket")

    if use_ws and importlib.util.find_spec("websockets") is None:
        warnings.warn(
            "websockets package not installed; falling back to TCP protocol.",
            RuntimeWarning,
            stacklevel=2,
        )
        use_ws = False

    try:
        if use_ws:
            _upload_ws(filename, json_string, host, ws_port)
        else:
            _upload_tcp(filename, json_string, host, tcp_port)
    except ValueError:
        raise
    except OSError as exc:
        raise ConnectionError(
            f"Could not connect to Mr. Pumpkin at {host}:{ws_port if use_ws else tcp_port}: {exc}"
        ) from exc
