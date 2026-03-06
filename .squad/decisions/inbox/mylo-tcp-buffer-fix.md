# Decision: TCP Upload Buffer Accumulation Pattern

**Date:** 2026-03-06  
**Author:** Mylo  
**Context:** PR #74 review bug fix — `upload_audio` TCP handler in `pumpkin_face.py`

---

## Decision

TCP upload loops that read until a marker (e.g., `\nEND_UPLOAD\n`) **must accumulate all received bytes in a single persistent buffer** across every `recv()` call. They must **never reset the buffer** after a non-matching chunk.

## Rationale

TCP is a stream protocol. A fixed marker string (like `\nEND_UPLOAD\n`) can be split arbitrarily across recv() boundaries. If the buffer is reset after each chunk that does not contain the marker, the tail of the previous chunk — which may be the start of the marker — is discarded. The marker is then never detected, causing the upload loop to hang indefinitely or corrupt the received file.

## Correct Pattern (binary upload)

```python
upload_buf = b""
upload_done = False
while True:
    chunk = client_socket.recv(4096)
    if not chunk:
        break  # connection lost
    upload_buf += chunk  # always accumulate, never reset
    if b"\nEND_UPLOAD\n" in upload_buf:
        audio_data, _ = upload_buf.split(b"\nEND_UPLOAD\n", 1)
        upload_done = True
        break
```

## Correct Pattern (line-oriented upload)

```python
upload_buf = b""
upload_done = False
while True:
    chunk = client_socket.recv(4096)
    if not chunk:
        break
    upload_buf += chunk
    while b"\n" in upload_buf:
        line_bytes, upload_buf = upload_buf.split(b"\n", 1)  # tail retained in upload_buf
        line = line_bytes.decode("utf-8").strip()
        if line == "END_UPLOAD":
            upload_done = True
            break
    if upload_done:
        break
```

The line-split pattern naturally retains the partial line tail in `upload_buf` after each split, so it is inherently split-safe.

## What Was Fixed

`upload_audio` TCP handler (`pumpkin_face.py`) — removed `upload_buf = b""` reset after non-matching chunks, and removed the redundant `audio_chunks` list. The buffer now accumulates correctly across all `recv()` calls.

`upload_timeline` TCP handler was already correct (uses the line-split pattern above).

## Applies To

Any TCP recv loop that reads until a delimiter or marker in `pumpkin_face.py` or any future server-side upload handler.
