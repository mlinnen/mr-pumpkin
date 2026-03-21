"""
Export/Import Recordings Tests — Issue #88

Tests for FileManager.export_recordings() and FileManager.import_recordings(),
covering:
  1. Export — produces a valid zip containing all .json and audio files
  2. Export — returns an empty (but valid) zip when the recordings dir is absent
  3. Import — extracts files and overwrites existing ones
  4. Import — ignores files with unsupported extensions
  5. Import — strips directory components from zip entry names
  6. Import — raises ValueError on bad zip data
  7. Import — raises ValueError when zip has no valid files
  8. CommandRouter.execute("export_recordings") — returns RECORDINGS_ZIP: prefix
  9. CommandRouter.execute("import_recordings") — returns IMPORT_RECORDINGS_MODE
 10. client_example.export_recordings / import_recordings — happy paths

Author: Mylo (Tester)
Date: 2026-03-20
"""

import base64
import io
import json
import os
import sys
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from timeline import FileManager, Timeline


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_minimal_timeline_json() -> str:
    """Return a minimal valid Timeline JSON string."""
    tl = Timeline()
    return json.dumps(tl.to_dict())


def _zip_containing(files: dict) -> bytes:
    """Build a zip in memory from a {name: bytes} dict and return raw bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# FileManager.export_recordings()
# ---------------------------------------------------------------------------

class TestExportRecordings:
    def test_export_empty_dir_returns_valid_empty_zip(self, tmp_path):
        fm = FileManager(recordings_dir=tmp_path)
        raw = fm.export_recordings()
        buf = io.BytesIO(raw)
        with zipfile.ZipFile(buf, 'r') as zf:
            assert zf.namelist() == []

    def test_export_nonexistent_dir_returns_valid_empty_zip(self, tmp_path):
        fm = FileManager(recordings_dir=tmp_path / "missing")
        raw = fm.export_recordings()
        buf = io.BytesIO(raw)
        with zipfile.ZipFile(buf, 'r') as zf:
            assert zf.namelist() == []

    def test_export_includes_json_files(self, tmp_path):
        (tmp_path / "session1.json").write_text(_make_minimal_timeline_json())
        (tmp_path / "session2.json").write_text(_make_minimal_timeline_json())
        fm = FileManager(recordings_dir=tmp_path)
        raw = fm.export_recordings()
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            names = zf.namelist()
        assert "session1.json" in names
        assert "session2.json" in names

    def test_export_includes_audio_files(self, tmp_path):
        audio_exts = ('.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac')
        for ext in audio_exts:
            (tmp_path / f"track{ext}").write_bytes(b"fake audio")
        fm = FileManager(recordings_dir=tmp_path)
        raw = fm.export_recordings()
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            names = zf.namelist()
        for ext in audio_exts:
            assert f"track{ext}" in names

    def test_export_excludes_unsupported_files(self, tmp_path):
        (tmp_path / "readme.txt").write_text("notes")
        (tmp_path / "session1.json").write_text(_make_minimal_timeline_json())
        fm = FileManager(recordings_dir=tmp_path)
        raw = fm.export_recordings()
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            names = zf.namelist()
        assert "readme.txt" not in names
        assert "session1.json" in names

    def test_export_returns_bytes(self, tmp_path):
        fm = FileManager(recordings_dir=tmp_path)
        raw = fm.export_recordings()
        assert isinstance(raw, bytes)

    def test_export_zip_entries_use_basenames_only(self, tmp_path):
        (tmp_path / "my_session.json").write_text(_make_minimal_timeline_json())
        fm = FileManager(recordings_dir=tmp_path)
        raw = fm.export_recordings()
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            for name in zf.namelist():
                assert '/' not in name, f"Entry should not contain path separator: {name}"


# ---------------------------------------------------------------------------
# FileManager.import_recordings()
# ---------------------------------------------------------------------------

class TestImportRecordings:
    def test_import_json_files(self, tmp_path):
        content = _make_minimal_timeline_json()
        raw_zip = _zip_containing({"session1.json": content.encode()})
        fm = FileManager(recordings_dir=tmp_path)
        count = fm.import_recordings(raw_zip)
        assert count == 1
        assert (tmp_path / "session1.json").read_text() == content

    def test_import_audio_files(self, tmp_path):
        raw_zip = _zip_containing({"track.mp3": b"fake mp3 data"})
        fm = FileManager(recordings_dir=tmp_path)
        count = fm.import_recordings(raw_zip)
        assert count == 1
        assert (tmp_path / "track.mp3").read_bytes() == b"fake mp3 data"

    def test_import_overwrites_existing_files(self, tmp_path):
        (tmp_path / "session1.json").write_text("old content")
        new_content = _make_minimal_timeline_json().encode()
        raw_zip = _zip_containing({"session1.json": new_content})
        fm = FileManager(recordings_dir=tmp_path)
        fm.import_recordings(raw_zip)
        assert (tmp_path / "session1.json").read_bytes() == new_content

    def test_import_creates_recordings_dir_if_missing(self, tmp_path):
        dest = tmp_path / "recordings"
        raw_zip = _zip_containing({"session1.json": _make_minimal_timeline_json().encode()})
        fm = FileManager(recordings_dir=dest)
        fm.import_recordings(raw_zip)
        assert dest.exists()

    def test_import_ignores_unsupported_extensions(self, tmp_path):
        raw_zip = _zip_containing({
            "session1.json": _make_minimal_timeline_json().encode(),
            "readme.txt": b"notes",
        })
        fm = FileManager(recordings_dir=tmp_path)
        count = fm.import_recordings(raw_zip)
        assert count == 1
        assert not (tmp_path / "readme.txt").exists()

    def test_import_strips_directory_components(self, tmp_path):
        raw_zip = _zip_containing({"subdir/session1.json": _make_minimal_timeline_json().encode()})
        fm = FileManager(recordings_dir=tmp_path)
        count = fm.import_recordings(raw_zip)
        assert count == 1
        assert (tmp_path / "session1.json").exists()

    def test_import_returns_count_of_extracted_files(self, tmp_path):
        raw_zip = _zip_containing({
            "a.json": _make_minimal_timeline_json().encode(),
            "b.json": _make_minimal_timeline_json().encode(),
            "c.mp3": b"audio",
        })
        fm = FileManager(recordings_dir=tmp_path)
        count = fm.import_recordings(raw_zip)
        assert count == 3

    def test_import_raises_on_invalid_zip(self, tmp_path):
        fm = FileManager(recordings_dir=tmp_path)
        with pytest.raises(ValueError, match="Invalid zip file"):
            fm.import_recordings(b"this is not a zip")

    def test_import_raises_when_no_valid_files_in_zip(self, tmp_path):
        raw_zip = _zip_containing({"readme.txt": b"nothing here"})
        fm = FileManager(recordings_dir=tmp_path)
        with pytest.raises(ValueError, match="no valid recording or audio files"):
            fm.import_recordings(raw_zip)

    def test_import_all_audio_extensions(self, tmp_path):
        audio_exts = ('.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac')
        files = {f"track{ext}": b"fake" for ext in audio_exts}
        raw_zip = _zip_containing(files)
        fm = FileManager(recordings_dir=tmp_path)
        count = fm.import_recordings(raw_zip)
        assert count == len(audio_exts)


# ---------------------------------------------------------------------------
# CommandRouter — export_recordings and import_recordings commands
# ---------------------------------------------------------------------------

class TestCommandRouterExportImport:
    def _make_router(self, tmp_path):
        """Build a minimal CommandRouter with mocked pumpkin and real FileManager."""
        from command_handler import CommandRouter

        pumpkin = MagicMock()
        # Wire recording_session and timeline_playback so the router doesn't crash
        pumpkin.recording_session.is_recording = False
        pumpkin.timeline_playback.state.value = "stopped"
        pumpkin.timeline_playback.filename = None
        # Use a real FileManager pointing at tmp_path
        from timeline import FileManager
        fm = FileManager(recordings_dir=tmp_path)
        pumpkin.file_manager = fm

        # expression class that always raises (so expression commands fail cleanly)
        class FakeExpr:
            def __init__(self, val):
                raise ValueError(f"unknown: {val}")

        return CommandRouter(pumpkin, FakeExpr)

    def test_export_recordings_returns_recordings_zip_prefix(self, tmp_path):
        router = self._make_router(tmp_path)
        response = router.execute("export_recordings")
        assert response.startswith("RECORDINGS_ZIP:")

    def test_export_recordings_base64_decodes_to_valid_zip(self, tmp_path):
        (tmp_path / "session1.json").write_text(_make_minimal_timeline_json())
        router = self._make_router(tmp_path)
        response = router.execute("export_recordings")
        b64 = response[len("RECORDINGS_ZIP:"):]
        raw = base64.b64decode(b64)
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            assert "session1.json" in zf.namelist()

    def test_export_recordings_empty_dir_returns_empty_zip(self, tmp_path):
        router = self._make_router(tmp_path)
        response = router.execute("export_recordings")
        assert response.startswith("RECORDINGS_ZIP:")
        raw = base64.b64decode(response[len("RECORDINGS_ZIP:"):])
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            assert zf.namelist() == []

    def test_import_recordings_returns_import_mode_marker(self, tmp_path):
        router = self._make_router(tmp_path)
        response = router.execute("import_recordings")
        assert response == "IMPORT_RECORDINGS_MODE"


# ---------------------------------------------------------------------------
# client_example — export_recordings / import_recordings
# ---------------------------------------------------------------------------

import client_example


class TestClientExportRecordings:
    def _make_socket(self, response_bytes: bytes):
        mock_sock = MagicMock()
        # Simulate server sending response then closing connection
        mock_sock.recv.side_effect = [response_bytes, b'']
        return mock_sock

    def test_export_recordings_saves_zip_to_disk(self, tmp_path):
        content = _make_minimal_timeline_json().encode()
        raw_zip = _zip_containing({"session1.json": content})
        b64 = base64.b64encode(raw_zip).decode('ascii')
        server_response = (f"RECORDINGS_ZIP:{b64}\n").encode('utf-8')

        output_path = str(tmp_path / "out.zip")
        with patch('socket.socket') as mock_sock_cls:
            mock_instance = self._make_socket(server_response)
            mock_sock_cls.return_value = mock_instance
            client_example.export_recordings(output_path)

        assert os.path.exists(output_path)
        with zipfile.ZipFile(output_path) as zf:
            assert "session1.json" in zf.namelist()

    def test_export_recordings_handles_server_error(self, tmp_path, capsys):
        server_response = b"ERROR No recordings found\n"
        output_path = str(tmp_path / "out.zip")
        with patch('socket.socket') as mock_sock_cls:
            mock_instance = self._make_socket(server_response)
            mock_sock_cls.return_value = mock_instance
            client_example.export_recordings(output_path)

        captured = capsys.readouterr()
        assert "Error" in captured.out
        assert not os.path.exists(output_path)

    def test_export_recordings_handles_connection_error(self, tmp_path, capsys):
        output_path = str(tmp_path / "out.zip")
        with patch('socket.socket') as mock_sock_cls:
            mock_instance = MagicMock()
            mock_instance.connect.side_effect = ConnectionRefusedError("refused")
            mock_sock_cls.return_value = mock_instance
            client_example.export_recordings(output_path)

        captured = capsys.readouterr()
        assert "Error" in captured.out


class TestClientImportRecordings:
    def test_import_recordings_sends_zip_to_server(self, tmp_path):
        content = _make_minimal_timeline_json().encode()
        raw_zip = _zip_containing({"session1.json": content})
        zip_path = str(tmp_path / "bundle.zip")
        with open(zip_path, 'wb') as f:
            f.write(raw_zip)

        with patch('socket.socket') as mock_sock_cls:
            mock_instance = MagicMock()
            mock_instance.recv.return_value = b'READY'
            mock_sock_cls.return_value = mock_instance
            # Second recv (final response)
            mock_instance.recv.side_effect = [b'READY', b'OK Imported 1 files']
            client_example.import_recordings(zip_path)

        mock_instance.connect.assert_called_once_with(('localhost', 5000))
        # Verify END_UPLOAD was sent
        sent_calls = [c[0][0] for c in mock_instance.send.call_args_list]
        assert b"END_UPLOAD\n" in sent_calls

    def test_import_recordings_file_not_found(self, tmp_path, capsys):
        client_example.import_recordings(str(tmp_path / "nonexistent.zip"))
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_import_recordings_handles_connection_error(self, tmp_path, capsys):
        zip_path = str(tmp_path / "bundle.zip")
        with open(zip_path, 'wb') as f:
            f.write(_zip_containing({"a.json": b"{}"}))

        with patch('socket.socket') as mock_sock_cls:
            mock_instance = MagicMock()
            mock_instance.connect.side_effect = ConnectionRefusedError("refused")
            mock_sock_cls.return_value = mock_instance
            client_example.import_recordings(zip_path)

        captured = capsys.readouterr()
        assert "Error" in captured.out
