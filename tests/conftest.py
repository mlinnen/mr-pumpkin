import sys
import os
import pytest
from unittest.mock import patch

# Add parent directory to Python path so tests can import pumpkin_face module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(autouse=True)
def isolate_position_file(tmp_path):
    """Redirect pumpkin_face.POSITION_FILE to a per-test temp directory.

    Prevents any test from writing pumpkin_position.json to the real working
    directory. Methods like set_projection_offset(), jog_projection(save=True),
    and the animation update loop all call _save_position(), which uses
    POSITION_FILE. Without this fixture those writes contaminate subsequent
    tests that create fresh PumpkinFace() instances and load the stale file.

    Tests that patch POSITION_FILE themselves (e.g. test_position_persistence.py)
    continue to work unchanged: their inner patch overrides this outer one for
    the duration of their own context manager.
    """
    pos_file = tmp_path / "pumpkin_position.json"
    with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
        yield
