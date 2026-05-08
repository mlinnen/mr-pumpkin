import pytest
from command_handler import CommandRouter

class DummyPumpkin:
    def __init__(self):
        self.recording_session = type('rs', (), {'is_recording': True})()
        self.timeline_playback = type('tp', (), {'state': type('s', (), {'value': 'stopped'})(), 'filename': None})()
        self.captured = None
    def _capture_command_for_recording(self, cmd):
        self.captured = cmd

class DummyExpression:
    def __init__(self, data):
        # Accept any expression so router.set_expression won't raise in tests
        pass

def test_preserve_argument_case_in_recording():
    p = DummyPumpkin()
    router = CommandRouter(p, DummyExpression)

    router.execute('play MyFile.JSON')
    assert p.captured == 'play MyFile.JSON'

    p.captured = None
    router.execute('record_stop SavedTimeline.JSON')
    # depending on branch logic, recorded value should preserve arg case
    assert p.captured is not None
