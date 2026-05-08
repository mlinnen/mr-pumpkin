import time
import pytest

from pumpkin_face import PumpkinFace

@pytest.fixture
def pumpkin():
    p = PumpkinFace(test_mode=True)
    yield p
    try:
        p.shutdown()
    except Exception:
        pass

def test_invalid_command_returns_error_or_ignored(pumpkin):
    # Some implementations raise, others return False/None — accept both behaviors
    try:
        result = pumpkin.handle_command('nonexistent_command')
    except Exception as e:
        assert isinstance(e, (ValueError, KeyError))
    else:
        assert result in (False, None)

def test_rendering_timeout(monkeypatch, pumpkin):
    # Simulate renderer blocking/hanging and verify timeout handling
    # Example: monkeypatch the render method to sleep longer than allowed timeout
    def slow_render(*a, **k):
        time.sleep(2.0)

    # assume PumpkinFace has an internal _render_frame method
    monkeypatch.setattr(pumpkin, '_render_frame', slow_render)

    # trigger a render and expect the public API to raise or return a timeout indicator
    with pytest.raises(TimeoutError):
        pumpkin.render_with_timeout(timeout=0.1)

