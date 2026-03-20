"""
Test suite for position persistence feature (Issue #86).

When the projector is positioned and the face is jogged into alignment with the
physical pumpkin, that alignment should survive a restart. These tests validate:

  - Save on jog: jog_projection() writes position file with correct values
  - Save on set: set_projection_offset() writes position file with correct values
  - Load on startup: position file is read at __init__ time and applied
  - Default on missing: no position file -> projection_offset_x/y default to 0
  - File format: JSON with "x" and "y" integer keys
  - Roundtrip: save then load restores exact values, including negatives
  - Edge case: invalid JSON in position file -> silently falls back to (0, 0)

Author: Mylo (Tester)
Issue: #86
"""

import json
import os
import pygame
import pytest
from unittest.mock import mock_open, patch, MagicMock, call

from pumpkin_face import PumpkinFace, Expression

# ---------------------------------------------------------------------------
# Expected file name — matches the constant Vi will define in pumpkin_face.py
# ---------------------------------------------------------------------------
EXPECTED_POSITION_FILE = "pumpkin_position.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pumpkin_no_load():
    """Create PumpkinFace while suppressing position file load.

    Since the load happens inside __init__, patch the load method before
    instantiation so tests that don't care about startup loading start with
    a clean (0, 0) state regardless of any real file on disk.
    """
    with patch.object(PumpkinFace, "_load_position", return_value=None):
        face = PumpkinFace(width=800, height=600)
    return face


# ---------------------------------------------------------------------------
# 1. API Surface
# ---------------------------------------------------------------------------

class TestPositionPersistenceAPIExists:
    """Verify that the public API introduced by Issue #86 is present."""

    def test_save_position_method_exists(self):
        """PumpkinFace must expose a _save_position() method."""
        pygame.init()
        face = _make_pumpkin_no_load()
        assert hasattr(face, "_save_position"), \
            "PumpkinFace must have a _save_position() method for Issue #86"
        assert callable(getattr(face, "_save_position")), \
            "_save_position must be callable"
        pygame.quit()

    def test_load_position_method_exists(self):
        """PumpkinFace must expose a _load_position() method."""
        pygame.init()
        face = _make_pumpkin_no_load()
        assert hasattr(face, "_load_position"), \
            "PumpkinFace must have a _load_position() method for Issue #86"
        assert callable(getattr(face, "_load_position")), \
            "_load_position must be callable"
        pygame.quit()

    def test_position_file_constant_exists(self):
        """pumpkin_face module must export POSITION_FILE constant."""
        import pumpkin_face as pf
        assert hasattr(pf, "POSITION_FILE"), \
            "pumpkin_face module must define a POSITION_FILE constant"
        assert isinstance(pf.POSITION_FILE, str), \
            "POSITION_FILE must be a string path"

    def teardown_method(self, method):
        try:
            pygame.quit()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 2. Save on Jog
# ---------------------------------------------------------------------------

class TestPositionSaveOnJog:
    """Position file is written when jog_projection() is called."""

    @pytest.fixture
    def pumpkin(self):
        pygame.init()
        face = _make_pumpkin_no_load()
        yield face
        pygame.quit()

    def test_jog_projection_calls_save_position(self, pumpkin):
        """jog_projection() must call _save_position() to persist the new offset."""
        with patch.object(pumpkin, "_save_position") as mock_save:
            pumpkin.jog_projection(10, 5)
            mock_save.assert_called_once()

    def test_jog_projection_saves_correct_x(self, pumpkin, tmp_path):
        """After jog_projection(10, 0), saved file contains x=10."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.jog_projection(10, 0)
        assert pos_file.exists(), "Position file must be created after jog"
        data = json.loads(pos_file.read_text())
        assert data["x"] == 10, f"Expected x=10, got {data['x']}"

    def test_jog_projection_saves_correct_y(self, pumpkin, tmp_path):
        """After jog_projection(0, 20), saved file contains y=20."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.jog_projection(0, 20)
        data = json.loads(pos_file.read_text())
        assert data["y"] == 20, f"Expected y=20, got {data['y']}"

    def test_jog_projection_saves_cumulative_offset(self, pumpkin, tmp_path):
        """Multiple jog calls accumulate; last save reflects final offset."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.jog_projection(10, 5)
            pumpkin.jog_projection(-3, 15)
        data = json.loads(pos_file.read_text())
        assert data["x"] == 7, f"Expected x=7 (10-3), got {data['x']}"
        assert data["y"] == 20, f"Expected y=20 (5+15), got {data['y']}"

    def test_jog_projection_saves_negative_values(self, pumpkin, tmp_path):
        """Negative projection offsets are persisted correctly."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.jog_projection(-50, -30)
        data = json.loads(pos_file.read_text())
        assert data["x"] == -50
        assert data["y"] == -30


# ---------------------------------------------------------------------------
# 3. Save on set_projection_offset
# ---------------------------------------------------------------------------

class TestPositionSaveOnSet:
    """Position file is written when set_projection_offset() is called."""

    @pytest.fixture
    def pumpkin(self):
        pygame.init()
        face = _make_pumpkin_no_load()
        yield face
        pygame.quit()

    def test_set_projection_offset_calls_save_position(self, pumpkin):
        """set_projection_offset() must call _save_position()."""
        with patch.object(pumpkin, "_save_position") as mock_save:
            pumpkin.set_projection_offset(100, -50)
            mock_save.assert_called_once()

    def test_set_projection_offset_saves_correct_values(self, pumpkin, tmp_path):
        """set_projection_offset(75, -25) writes x=75, y=-25 to file."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.set_projection_offset(75, -25)
        data = json.loads(pos_file.read_text())
        assert data["x"] == 75
        assert data["y"] == -25


# ---------------------------------------------------------------------------
# 4. Load on Startup
# ---------------------------------------------------------------------------

class TestPositionLoadOnStartup:
    """Saved position is applied during PumpkinFace.__init__()."""

    def test_startup_loads_saved_x(self, tmp_path):
        """If position file contains x=42, projection_offset_x starts at 42."""
        pos_file = tmp_path / "pumpkin_position.json"
        pos_file.write_text(json.dumps({"x": 42, "y": 0}))
        pygame.init()
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            face = PumpkinFace(width=800, height=600)
        assert face.projection_offset_x == 42, \
            f"Expected projection_offset_x=42, got {face.projection_offset_x}"
        pygame.quit()

    def test_startup_loads_saved_y(self, tmp_path):
        """If position file contains y=-17, projection_offset_y starts at -17."""
        pos_file = tmp_path / "pumpkin_position.json"
        pos_file.write_text(json.dumps({"x": 0, "y": -17}))
        pygame.init()
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            face = PumpkinFace(width=800, height=600)
        assert face.projection_offset_y == -17, \
            f"Expected projection_offset_y=-17, got {face.projection_offset_y}"
        pygame.quit()

    def test_startup_loads_both_axes(self, tmp_path):
        """Both x and y are restored correctly on startup."""
        pos_file = tmp_path / "pumpkin_position.json"
        pos_file.write_text(json.dumps({"x": 123, "y": -456}))
        pygame.init()
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            face = PumpkinFace(width=800, height=600)
        assert face.projection_offset_x == 123
        assert face.projection_offset_y == -456
        pygame.quit()

    def teardown_method(self, method):
        try:
            pygame.quit()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 5. Default on Missing File
# ---------------------------------------------------------------------------

class TestPositionDefaultOnMissingFile:
    """No position file -> offset defaults to (0, 0) without error."""

    def test_missing_file_defaults_x_to_zero(self, tmp_path):
        """When position file does not exist, projection_offset_x defaults to 0."""
        pos_file = tmp_path / "pumpkin_position.json"
        # Intentionally NOT creating the file
        pygame.init()
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            face = PumpkinFace(width=800, height=600)
        assert face.projection_offset_x == 0, \
            f"Expected 0, got {face.projection_offset_x}"
        pygame.quit()

    def test_missing_file_defaults_y_to_zero(self, tmp_path):
        """When position file does not exist, projection_offset_y defaults to 0."""
        pos_file = tmp_path / "pumpkin_position.json"
        pygame.init()
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            face = PumpkinFace(width=800, height=600)
        assert face.projection_offset_y == 0, \
            f"Expected 0, got {face.projection_offset_y}"
        pygame.quit()

    def test_missing_file_does_not_raise(self, tmp_path):
        """Loading with no position file must not raise an exception."""
        pos_file = tmp_path / "pumpkin_position.json"
        pygame.init()
        try:
            with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
                face = PumpkinFace(width=800, height=600)
        except Exception as e:
            pytest.fail(f"PumpkinFace() raised {type(e).__name__} with missing position file: {e}")
        finally:
            pygame.quit()

    def teardown_method(self, method):
        try:
            pygame.quit()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 6. File Format
# ---------------------------------------------------------------------------

class TestPositionFileFormat:
    """Position file uses JSON format with numeric 'x' and 'y' keys."""

    @pytest.fixture
    def pumpkin(self):
        pygame.init()
        face = _make_pumpkin_no_load()
        yield face
        pygame.quit()

    def test_file_is_valid_json(self, pumpkin, tmp_path):
        """_save_position() writes a file that can be parsed as JSON."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.jog_projection(5, 10)
        content = pos_file.read_text()
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            pytest.fail(f"Position file is not valid JSON: {e}\nContent: {content!r}")

    def test_file_has_x_key(self, pumpkin, tmp_path):
        """Saved JSON must have an 'x' key."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.jog_projection(5, 10)
        data = json.loads(pos_file.read_text())
        assert "x" in data, f"Position file must have 'x' key, got: {list(data.keys())}"

    def test_file_has_y_key(self, pumpkin, tmp_path):
        """Saved JSON must have a 'y' key."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.jog_projection(5, 10)
        data = json.loads(pos_file.read_text())
        assert "y" in data, f"Position file must have 'y' key, got: {list(data.keys())}"

    def test_x_value_is_numeric(self, pumpkin, tmp_path):
        """The 'x' key must hold a numeric (int or float) value."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.jog_projection(5, 10)
        data = json.loads(pos_file.read_text())
        assert isinstance(data["x"], (int, float)), \
            f"'x' must be numeric, got {type(data['x'])}"

    def test_y_value_is_numeric(self, pumpkin, tmp_path):
        """The 'y' key must hold a numeric (int or float) value."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.jog_projection(5, 10)
        data = json.loads(pos_file.read_text())
        assert isinstance(data["y"], (int, float)), \
            f"'y' must be numeric, got {type(data['y'])}"

    def test_x_value_matches_offset(self, pumpkin, tmp_path):
        """The saved 'x' value matches pumpkin.projection_offset_x after jog."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.jog_projection(33, 0)
        data = json.loads(pos_file.read_text())
        assert data["x"] == pumpkin.projection_offset_x

    def test_y_value_matches_offset(self, pumpkin, tmp_path):
        """The saved 'y' value matches pumpkin.projection_offset_y after jog."""
        pos_file = tmp_path / "pumpkin_position.json"
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.jog_projection(0, -77)
        data = json.loads(pos_file.read_text())
        assert data["y"] == pumpkin.projection_offset_y


# ---------------------------------------------------------------------------
# 7. Roundtrip
# ---------------------------------------------------------------------------

class TestPositionRoundtrip:
    """Save then load must return exactly the same offset values."""

    @pytest.fixture
    def pumpkin(self):
        pygame.init()
        face = _make_pumpkin_no_load()
        yield face
        pygame.quit()

    def test_roundtrip_positive_values(self, tmp_path):
        """Positive offset survives save-then-load."""
        pos_file = tmp_path / "pumpkin_position.json"
        pygame.init()

        # Save phase
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            with patch.object(PumpkinFace, "_load_position", return_value=None):
                writer = PumpkinFace(width=800, height=600)
            writer.set_projection_offset(200, 150)
            writer.jog_projection(0, 0)  # ensure last save has correct state

        # Load phase
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            reader = PumpkinFace(width=800, height=600)

        assert reader.projection_offset_x == 200
        assert reader.projection_offset_y == 150
        pygame.quit()

    def test_roundtrip_negative_values(self, tmp_path):
        """Negative offsets (typical when projector is off-center) survive roundtrip."""
        pos_file = tmp_path / "pumpkin_position.json"
        pygame.init()

        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            with patch.object(PumpkinFace, "_load_position", return_value=None):
                writer = PumpkinFace(width=800, height=600)
            writer.set_projection_offset(-300, -200)

        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            reader = PumpkinFace(width=800, height=600)

        assert reader.projection_offset_x == -300
        assert reader.projection_offset_y == -200
        pygame.quit()

    def test_roundtrip_zero_values(self, tmp_path):
        """Zero offset (centered projection) roundtrips to (0, 0)."""
        pos_file = tmp_path / "pumpkin_position.json"
        pygame.init()

        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            with patch.object(PumpkinFace, "_load_position", return_value=None):
                writer = PumpkinFace(width=800, height=600)
            writer.set_projection_offset(0, 0)

        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            reader = PumpkinFace(width=800, height=600)

        assert reader.projection_offset_x == 0
        assert reader.projection_offset_y == 0
        pygame.quit()

    def test_roundtrip_mixed_sign_values(self, tmp_path):
        """Mixed sign offsets (e.g. x positive, y negative) roundtrip exactly."""
        pos_file = tmp_path / "pumpkin_position.json"
        pygame.init()

        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            with patch.object(PumpkinFace, "_load_position", return_value=None):
                writer = PumpkinFace(width=800, height=600)
            writer.set_projection_offset(120, -80)

        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            reader = PumpkinFace(width=800, height=600)

        assert reader.projection_offset_x == 120
        assert reader.projection_offset_y == -80
        pygame.quit()

    def teardown_method(self, method):
        try:
            pygame.quit()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 8. Invalid JSON Edge Case
# ---------------------------------------------------------------------------

class TestPositionInvalidJSONFallback:
    """Corrupted position file must not crash startup; fallback to (0, 0)."""

    @pytest.mark.parametrize("bad_content", [
        "not json at all",
        "{x: 10, y: 20}",          # Keys without quotes
        '{"x": 10',                 # Truncated
        "",                         # Empty file
        "null",                     # Valid JSON but not an object
        '{"x": "ten", "y": 5}',    # String value instead of number
    ])
    def test_invalid_json_defaults_x_to_zero(self, bad_content, tmp_path):
        """Corrupt position file -> projection_offset_x defaults to 0, no crash."""
        pos_file = tmp_path / "pumpkin_position.json"
        pos_file.write_text(bad_content)
        pygame.init()
        try:
            with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
                face = PumpkinFace(width=800, height=600)
            assert face.projection_offset_x == 0, \
                f"Expected 0 after bad JSON, got {face.projection_offset_x} (content: {bad_content!r})"
        except Exception as e:
            pytest.fail(
                f"PumpkinFace() crashed on invalid position file "
                f"({bad_content!r}): {type(e).__name__}: {e}"
            )
        finally:
            pygame.quit()

    @pytest.mark.parametrize("bad_content", [
        "not json at all",
        "{x: 10, y: 20}",
        '{"x": 10',
        "",
        "null",
    ])
    def test_invalid_json_defaults_y_to_zero(self, bad_content, tmp_path):
        """Corrupt position file -> projection_offset_y defaults to 0, no crash."""
        pos_file = tmp_path / "pumpkin_position.json"
        pos_file.write_text(bad_content)
        pygame.init()
        try:
            with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
                face = PumpkinFace(width=800, height=600)
            assert face.projection_offset_y == 0, \
                f"Expected 0 after bad JSON, got {face.projection_offset_y} (content: {bad_content!r})"
        except Exception as e:
            pytest.fail(
                f"PumpkinFace() crashed on invalid position file "
                f"({bad_content!r}): {type(e).__name__}: {e}"
            )
        finally:
            pygame.quit()

    def teardown_method(self, method):
        try:
            pygame.quit()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 9. No Side Effects on Non-Persistence Operations
# ---------------------------------------------------------------------------

class TestPositionNoSideEffectsOnReset:
    """Verify projection_reset does NOT persist (resets are transient by design)."""

    @pytest.fixture
    def pumpkin(self):
        pygame.init()
        face = _make_pumpkin_no_load()
        yield face
        pygame.quit()

    def test_reset_projection_offset_does_not_save(self, pumpkin, tmp_path):
        """projection_reset should NOT write a position file.

        The user's physical alignment is preserved across resets so they can
        recover it with a restart. Only explicit jog/set operations persist.
        """
        pos_file = tmp_path / "pumpkin_position.json"
        # First save a real position
        with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
            pumpkin.set_projection_offset(100, 50)

        saved_before = json.loads(pos_file.read_text())

        # Reset should zero the in-memory offset but not overwrite the file
        with patch.object(pumpkin, "_save_position") as mock_save:
            pumpkin.reset_projection_offset()
            mock_save.assert_not_called(), \
                "reset_projection_offset() must NOT call _save_position()"

        # File on disk should still contain the pre-reset position
        saved_after = json.loads(pos_file.read_text())
        assert saved_after == saved_before, \
            "Position file must not be overwritten by reset"
