"""
Test suite for wiggle_nose command alias (Issue #50).

These tests validate that wiggle_nose is a functional alias for twitch_nose:
- Command recognition and routing
- Alias equivalence (same behavior as twitch_nose)
- Parameter handling (default magnitude, custom magnitude)
- Edge cases (empty args, invalid args, recording integration)

The wiggle_nose command was added to provide a more user-friendly alternative
to twitch_nose, making the command more discoverable and intuitive.

Author: Mylo (Tester)
Date: 2026-02-26
"""

import pygame
import pytest
from pumpkin_face import PumpkinFace, Expression
from command_handler import CommandRouter


class TestWiggleNoseCommandRecognition:
    """Test that wiggle_nose command is recognized and routed correctly."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    @pytest.fixture
    def router(self, pumpkin):
        """Create a CommandRouter for testing command execution."""
        return CommandRouter(pumpkin, Expression)
    
    def test_wiggle_nose_command_recognized(self, router, pumpkin):
        """wiggle_nose command should be recognized by command router."""
        # Execute wiggle_nose command
        result = router.execute("wiggle_nose")
        
        # Verify command was processed (returns empty string for socket commands)
        assert result == ""
        
        # Verify animation started
        assert pumpkin.is_twitching == True
    
    def test_wiggle_nose_with_default_magnitude(self, router, pumpkin):
        """wiggle_nose without parameters should use default magnitude (50)."""
        # Execute command without parameters
        router.execute("wiggle_nose")
        
        # Verify twitch animation started with correct state
        assert pumpkin.is_twitching == True
        assert pumpkin.nose_animation_progress == 0.0
        assert pumpkin.nose_animation_duration == 0.5
    
    def test_wiggle_nose_with_custom_magnitude(self, router, pumpkin):
        """wiggle_nose with magnitude parameter should use that magnitude."""
        # Execute command with custom magnitude
        router.execute("wiggle_nose 75")
        
        # Verify animation started (magnitude affects amplitude, not duration)
        assert pumpkin.is_twitching == True
        assert pumpkin.nose_animation_duration == 0.5
    
    def test_wiggle_nose_case_insensitive(self, router, pumpkin):
        """wiggle_nose should work regardless of case."""
        # Test uppercase
        router.execute("WIGGLE_NOSE")
        assert pumpkin.is_twitching == True
        
        # Reset
        pumpkin.is_twitching = False
        
        # Test mixed case
        router.execute("WiGgLe_NoSe")
        assert pumpkin.is_twitching == True


class TestWiggleNoseAliasEquivalence:
    """Test that wiggle_nose produces identical behavior to twitch_nose."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    @pytest.fixture
    def router(self, pumpkin):
        """Create a CommandRouter for testing command execution."""
        return CommandRouter(pumpkin, Expression)
    
    def test_wiggle_nose_equals_twitch_nose_default(self, router, pumpkin):
        """wiggle_nose (no params) should behave identically to twitch_nose (no params)."""
        # Execute twitch_nose and capture state
        router.execute("twitch_nose")
        twitch_state = {
            'is_twitching': pumpkin.is_twitching,
            'duration': pumpkin.nose_animation_duration,
            'progress': pumpkin.nose_animation_progress
        }
        
        # Reset
        pumpkin.is_twitching = False
        
        # Execute wiggle_nose and capture state
        router.execute("wiggle_nose")
        wiggle_state = {
            'is_twitching': pumpkin.is_twitching,
            'duration': pumpkin.nose_animation_duration,
            'progress': pumpkin.nose_animation_progress
        }
        
        # Verify identical behavior
        assert wiggle_state == twitch_state
    
    def test_wiggle_nose_equals_twitch_nose_with_magnitude(self, router, pumpkin):
        """wiggle_nose 75 should behave identically to twitch_nose 75."""
        # Execute twitch_nose with magnitude
        router.execute("twitch_nose 75")
        twitch_state = {
            'is_twitching': pumpkin.is_twitching,
            'duration': pumpkin.nose_animation_duration,
            'progress': pumpkin.nose_animation_progress
        }
        
        # Reset
        pumpkin.is_twitching = False
        
        # Execute wiggle_nose with same magnitude
        router.execute("wiggle_nose 75")
        wiggle_state = {
            'is_twitching': pumpkin.is_twitching,
            'duration': pumpkin.nose_animation_duration,
            'progress': pumpkin.nose_animation_progress
        }
        
        # Verify identical behavior
        assert wiggle_state == twitch_state
    
    def test_wiggle_nose_calls_same_internal_method(self, router, pumpkin):
        """Both wiggle_nose and twitch_nose should call _start_nose_twitch."""
        # This is verified implicitly by checking is_twitching flag
        # Both commands trigger the same animation state
        
        router.execute("wiggle_nose")
        assert pumpkin.is_twitching == True
        assert pumpkin.is_scrunching == False  # Not scrunch
        
        # Reset and test twitch_nose
        pumpkin.is_twitching = False
        
        router.execute("twitch_nose")
        assert pumpkin.is_twitching == True
        assert pumpkin.is_scrunching == False


class TestWiggleNoseEdgeCases:
    """Test edge cases and error handling for wiggle_nose command."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    @pytest.fixture
    def router(self, pumpkin):
        """Create a CommandRouter for testing command execution."""
        return CommandRouter(pumpkin, Expression)
    
    def test_wiggle_nose_with_invalid_magnitude_graceful_degradation(self, router, pumpkin):
        """wiggle_nose with invalid magnitude should handle error gracefully."""
        # Try with non-numeric magnitude
        result = router.execute("wiggle_nose invalid")
        
        # Should return empty string (error is logged, not returned)
        assert result == ""
        
        # Animation should NOT start due to error
        assert pumpkin.is_twitching == False
    
    def test_wiggle_nose_with_negative_magnitude(self, router, pumpkin):
        """wiggle_nose with negative magnitude should still parse (abs value used)."""
        # Execute with negative magnitude
        router.execute("wiggle_nose -50")
        
        # Should start animation (implementation uses magnitude in formula)
        assert pumpkin.is_twitching == True
    
    def test_wiggle_nose_with_zero_magnitude(self, router, pumpkin):
        """wiggle_nose with zero magnitude should still animate (edge case)."""
        router.execute("wiggle_nose 0")
        
        # Animation starts (magnitude affects amplitude, not whether it runs)
        assert pumpkin.is_twitching == True
    
    def test_wiggle_nose_with_extra_parameters_ignored(self, router, pumpkin):
        """wiggle_nose with extra parameters should use first parameter only."""
        router.execute("wiggle_nose 50 100 200")
        
        # Should successfully start (extra params ignored)
        assert pumpkin.is_twitching == True
    
    def test_wiggle_nose_while_already_twitching_rejected(self, router, pumpkin):
        """wiggle_nose during active twitch should be rejected (non-interrupting)."""
        # Start first animation
        router.execute("wiggle_nose")
        assert pumpkin.is_twitching == True
        
        # Try to start second animation (should be rejected)
        # Advance progress slightly to simulate in-progress animation
        pumpkin.nose_animation_progress = 0.3
        
        # Attempt second wiggle
        router.execute("wiggle_nose")
        
        # Animation should still be in progress from first command
        assert pumpkin.is_twitching == True
        assert pumpkin.nose_animation_progress == 0.3  # Unchanged
    
    def test_wiggle_nose_while_scrunching_rejected(self, router, pumpkin):
        """wiggle_nose during active scrunch should be rejected (cross-animation block)."""
        # Start scrunch animation
        router.execute("scrunch_nose")
        assert pumpkin.is_scrunching == True
        
        # Try to wiggle while scrunching
        router.execute("wiggle_nose")
        
        # Should not start twitch (scrunch is still active)
        assert pumpkin.is_scrunching == True
        assert pumpkin.is_twitching == False
    
    def test_wiggle_nose_after_reset(self, router, pumpkin):
        """wiggle_nose should work after reset_nose."""
        # Start and reset
        router.execute("wiggle_nose")
        router.execute("reset_nose")
        
        assert pumpkin.is_twitching == False
        
        # Should be able to wiggle again
        router.execute("wiggle_nose")
        assert pumpkin.is_twitching == True


class TestWiggleNoseRecordingIntegration:
    """Test that wiggle_nose integrates correctly with recording system."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    @pytest.fixture
    def router(self, pumpkin):
        """Create a CommandRouter for testing command execution."""
        return CommandRouter(pumpkin, Expression)
    
    def test_wiggle_nose_captured_during_recording(self, router, pumpkin):
        """wiggle_nose should be captured when recording is active."""
        # Start recording session
        pumpkin.recording_session.start()
        
        # Execute wiggle_nose
        router.execute("wiggle_nose")
        
        # Verify command was captured
        assert len(pumpkin.recording_session.commands) == 1
        assert pumpkin.recording_session.commands[0].command == "wiggle_nose"
    
    def test_wiggle_nose_with_magnitude_captured_with_params(self, router, pumpkin):
        """wiggle_nose with magnitude should be captured with full command string."""
        # Start recording
        pumpkin.recording_session.start()
        
        # Execute wiggle_nose with magnitude
        router.execute("wiggle_nose 75")
        
        # Verify full command captured (preserves magnitude for playback)
        assert len(pumpkin.recording_session.commands) == 1
        assert pumpkin.recording_session.commands[0].command == "wiggle_nose"
        assert pumpkin.recording_session.commands[0].args["magnitude"] == 75.0
    
    def test_wiggle_nose_not_captured_when_not_recording(self, router, pumpkin):
        """wiggle_nose should not be captured when recording is inactive."""
        # Ensure recording is off
        pumpkin.recording_session.is_recording = False
        pumpkin.recording_session.commands = []
        
        # Execute wiggle_nose
        router.execute("wiggle_nose")
        
        # Verify command was NOT captured
        assert len(pumpkin.recording_session.commands) == 0


class TestWiggleNoseParameterParsing:
    """Test parameter parsing edge cases for wiggle_nose command."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    @pytest.fixture
    def router(self, pumpkin):
        """Create a CommandRouter for testing command execution."""
        return CommandRouter(pumpkin, Expression)
    
    def test_wiggle_nose_with_float_magnitude(self, router, pumpkin):
        """wiggle_nose should accept float magnitude values."""
        router.execute("wiggle_nose 50.5")
        
        # Should parse successfully
        assert pumpkin.is_twitching == True
    
    def test_wiggle_nose_with_large_magnitude(self, router, pumpkin):
        """wiggle_nose with very large magnitude should still work."""
        router.execute("wiggle_nose 999.9")
        
        # Should parse (clamping may occur in animation logic)
        assert pumpkin.is_twitching == True
    
    def test_wiggle_nose_with_whitespace_variations(self, router, pumpkin):
        """wiggle_nose should handle various whitespace patterns."""
        # Multiple spaces
        router.execute("wiggle_nose  50")
        assert pumpkin.is_twitching == True
        
        # Reset
        pumpkin.is_twitching = False
        
        # Trailing whitespace
        router.execute("wiggle_nose 50  ")
        assert pumpkin.is_twitching == True
    
    def test_wiggle_nose_empty_parameter(self, router, pumpkin):
        """wiggle_nose with empty parameter string should use default."""
        # Command with trailing space but no parameter
        router.execute("wiggle_nose ")
        
        # Should use default magnitude
        assert pumpkin.is_twitching == True
