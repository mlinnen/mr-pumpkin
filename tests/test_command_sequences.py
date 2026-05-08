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

def test_rapid_command_sequence_does_not_crash(pumpkin):
    # Send a burst of commands quickly and verify system remains responsive
    commands = ['happy', 'blink', 'angry', 'neutral', 'surprised', 'sleep']
    for cmd in commands * 3:  # repeat sequence
        pumpkin.handle_command(cmd)
    # allow processing
    time.sleep(0.2)
    # Expect the face to have processed commands and be in a valid state
    assert pumpkin.current_expression is not None

def test_command_queue_ordering(pumpkin):
    # If the implementation uses a queue, ensure FIFO ordering behavior
    pumpkin.handle_command('happy')
    pumpkin.handle_command('angry')
    time.sleep(0.05)
    # Depending on implementation, either final expression is 'angry' or in transition
    assert pumpkin.current_expression in ('angry', 'transition_to_angry')

