import time
import pytest

# Tests for expression transitions of the pumpkin face
# Adjust imports/fixture names to match the real API in pumpkin_face.py
from pumpkin_face import PumpkinFace

@pytest.fixture
def pumpkin():
    # Create a PumpkinFace instance in test mode (if available)
    # If PumpkinFace requires init args, adapt here.
    p = PumpkinFace(test_mode=True)
    yield p
    # ensure cleanup
    try:
        p.shutdown()
    except Exception:
        pass

def test_basic_expression_sequence(pumpkin):
    # Verify transitions between a few named expressions result in correct state
    pumpkin.set_expression('neutral')
    assert pumpkin.current_expression == 'neutral'

    pumpkin.set_expression('happy')
    # allow animation step(s) to progress if animations are asynchronous
    time.sleep(0.05)
    assert pumpkin.current_expression in ('happy', 'transition_to_happy')

    pumpkin.set_expression('scared')
    time.sleep(0.05)
    assert pumpkin.current_expression in ('scared', 'transition_to_scared')

def test_expression_interrupt_preserves_stability(pumpkin):
    # Rapidly change expressions and assert no invalid state is reached
    pumpkin.set_expression('happy')
    pumpkin.set_expression('angry')
    pumpkin.set_expression('sad')
    time.sleep(0.1)
    # The final committed expression should be the last one requested
    assert pumpkin.current_expression in ('sad', 'transition_to_sad')

# Edge-case: request the same expression repeatedly
def test_idempotent_expression_requests(pumpkin):
    pumpkin.set_expression('neutral')
    pumpkin.set_expression('neutral')
    pumpkin.set_expression('neutral')
    assert pumpkin.current_expression == 'neutral'
