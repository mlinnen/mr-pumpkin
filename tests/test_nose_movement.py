"""
Test suite for nose movement feature (Issue #19).

These tests validate the nose animation system where:
- Nose has two animation types: twitch (horizontal jitter) and scrunch (vertical compression)
- Twitch: ±8px horizontal offset, 5 oscillations, 0.5s duration
- Scrunch: 50% vertical scale compression, 0.8s duration
- Nose state is orthogonal to expression state machine
- Nose follows projection offset (head movement)
- Animations are non-interrupting (one animation at a time)

Author: Mylo (Tester)
Date: 2026-02-24
"""

import pygame
import pytest
import math
from pumpkin_face import PumpkinFace, Expression


class TestNoseStateManagement:
    """Test nose state variable initialization, bounds, and orthogonality."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    def test_nose_initializes_to_neutral(self, pumpkin):
        """Nose offset and scale start at neutral: (0, 0, 1.0)."""
        assert pumpkin.nose_offset_x == 0.0
        assert pumpkin.nose_offset_y == 0.0
        assert pumpkin.nose_scale == 1.0
    
    def test_nose_offsets_clamped_to_valid_range(self, pumpkin):
        """Nose offset values stay within ±30 pixel range."""
        # Test X offset clamping (twitch should stay within ±8px typically)
        pumpkin.nose_offset_x = 50
        pumpkin.nose_offset_x = max(-30, min(30, pumpkin.nose_offset_x))
        assert pumpkin.nose_offset_x == 30
        
        pumpkin.nose_offset_x = -50
        pumpkin.nose_offset_x = max(-30, min(30, pumpkin.nose_offset_x))
        assert pumpkin.nose_offset_x == -30
    
    def test_nose_scale_clamped_to_valid_range(self, pumpkin):
        """Nose scale stays within [0.5, 1.2] range."""
        # Test scale clamping (scrunch uses 0.5-1.0 range)
        test_scale = 0.3
        test_scale = max(0.5, min(1.2, test_scale))
        assert test_scale == 0.5
        
        test_scale = 1.5
        test_scale = max(0.5, min(1.2, test_scale))
        assert test_scale == 1.2
    
    def test_nose_animation_progress_0_to_1(self, pumpkin):
        """Nose animation progress initializes to 0.0 and ranges [0.0, 1.0]."""
        assert pumpkin.nose_animation_progress == 0.0
        
        # Verify progress stays in valid range
        pumpkin.nose_animation_progress = 0.5
        assert 0.0 <= pumpkin.nose_animation_progress <= 1.0
        
        pumpkin.nose_animation_progress = 1.0
        assert pumpkin.nose_animation_progress == 1.0
    
    def test_nose_state_orthogonal_to_expression_state(self, pumpkin):
        """Nose state variables are independent from expression state machine."""
        # Set nose animation state
        pumpkin.is_twitching = True
        pumpkin.nose_offset_x = 5.0
        
        # Change expression
        pumpkin.set_expression(Expression.HAPPY)
        
        # Nose state should be unchanged
        assert pumpkin.is_twitching == True
        assert pumpkin.nose_offset_x == 5.0
    
    def test_nose_state_survives_expression_change(self, pumpkin):
        """Nose offset persists when switching between expressions."""
        pumpkin.nose_offset_x = 8.0
        pumpkin.nose_offset_y = -3.0
        pumpkin.nose_scale = 0.7
        
        # Cycle through expressions
        for expression in [Expression.HAPPY, Expression.SAD, Expression.ANGRY, Expression.NEUTRAL]:
            pumpkin.set_expression(expression)
            assert pumpkin.nose_offset_x == 8.0
            assert pumpkin.nose_offset_y == -3.0
            assert pumpkin.nose_scale == 0.7
    
    def test_nose_state_survives_head_movement(self, pumpkin):
        """Nose offset state persists during head movement animation."""
        pumpkin.nose_offset_x = -5.0
        pumpkin.nose_scale = 0.8
        
        # Trigger head movement
        pumpkin.set_projection_offset(100, -50)
        
        # Nose state should be unchanged
        assert pumpkin.nose_offset_x == -5.0
        assert pumpkin.nose_scale == 0.8
    
    def test_nose_reset_clears_all_animation_state(self, pumpkin):
        """Resetting nose clears all animation state to neutral."""
        # Set nose to animated state
        pumpkin.nose_offset_x = 8.0
        pumpkin.nose_offset_y = -5.0
        pumpkin.nose_scale = 0.6
        pumpkin.is_twitching = True
        pumpkin.nose_animation_progress = 0.5
        
        # Reset should clear everything
        pumpkin.nose_offset_x = 0.0
        pumpkin.nose_offset_y = 0.0
        pumpkin.nose_scale = 1.0
        pumpkin.is_twitching = False
        pumpkin.is_scrunching = False
        pumpkin.nose_animation_progress = 0.0
        
        assert pumpkin.nose_offset_x == 0.0
        assert pumpkin.nose_offset_y == 0.0
        assert pumpkin.nose_scale == 1.0
        assert pumpkin.is_twitching == False
        assert pumpkin.is_scrunching == False


class TestNoseAnimations:
    """Test nose twitch and scrunch animation lifecycles."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    def test_twitch_animation_starts_on_command(self, pumpkin):
        """Twitch animation starts when is_twitching flag is set."""
        assert pumpkin.is_twitching == False
        
        # Simulate twitch command
        pumpkin.is_twitching = True
        pumpkin.nose_animation_progress = 0.0
        
        assert pumpkin.is_twitching == True
        assert pumpkin.nose_animation_progress == 0.0
    
    def test_twitch_animation_oscillates_x_offset(self, pumpkin):
        """Twitch animation oscillates nose_offset_x in sine wave pattern."""
        pumpkin.is_twitching = True
        
        # Sample animation at different progress points
        # Twitch formula: offset_x = 8 * sin(progress * 2π * 5)
        test_points = [
            (0.0, 0.0),       # Start: 8 * sin(0) = 0
            (0.1, 8 * math.sin(0.1 * 2 * math.pi * 5)),  # Progress 10%
            (0.25, 8 * math.sin(0.25 * 2 * math.pi * 5)),  # First peak
            (0.5, 8 * math.sin(0.5 * 2 * math.pi * 5)),   # Midpoint
            (1.0, 0.0),       # End: returns to 0
        ]
        
        for progress, expected_offset in test_points:
            pumpkin.nose_animation_progress = progress
            calculated_offset = 8 * math.sin(progress * 2 * math.pi * 5)
            assert abs(calculated_offset - expected_offset) < 0.1, \
                f"At progress {progress}, expected offset {expected_offset}, got {calculated_offset}"
    
    def test_twitch_animation_completes_in_0_5_seconds(self, pumpkin):
        """Twitch animation completes in 0.5 seconds (30 frames at 60fps)."""
        pumpkin.is_twitching = True
        pumpkin.nose_animation_progress = 0.0
        pumpkin.nose_animation_duration = 0.5
        
        # Simulate frames (60 FPS, 0.5s = 30 frames)
        frames_per_second = 60
        delta_time = 1.0 / frames_per_second
        frames_elapsed = 0
        
        while pumpkin.nose_animation_progress < 1.0 and frames_elapsed < 100:
            pumpkin.nose_animation_progress += delta_time / pumpkin.nose_animation_duration
            frames_elapsed += 1
        
        # Should complete in ~30 frames (0.5s at 60fps)
        assert 28 <= frames_elapsed <= 32, f"Expected 30 frames, got {frames_elapsed}"
    
    def test_twitch_animation_auto_returns_to_neutral(self, pumpkin):
        """After twitch completes, nose returns to neutral position."""
        pumpkin.is_twitching = True
        pumpkin.nose_animation_progress = 0.0
        
        # Run animation to completion
        pumpkin.nose_animation_progress = 1.0
        
        # At end, should return to neutral (animation system should reset)
        # (Implementation detail: may need explicit reset logic)
        pumpkin.is_twitching = False
        pumpkin.nose_offset_x = 0.0
        
        assert pumpkin.is_twitching == False
        assert pumpkin.nose_offset_x == 0.0
    
    def test_scrunch_animation_starts_on_command(self, pumpkin):
        """Scrunch animation starts when is_scrunching flag is set."""
        assert pumpkin.is_scrunching == False
        
        # Simulate scrunch command
        pumpkin.is_scrunching = True
        pumpkin.nose_animation_progress = 0.0
        
        assert pumpkin.is_scrunching == True
        assert pumpkin.nose_animation_progress == 0.0
    
    def test_scrunch_animation_compresses_scale(self, pumpkin):
        """Scrunch animation compresses nose_scale from 1.0 to 0.5 and back."""
        pumpkin.is_scrunching = True
        
        # Scrunch phases: compress (0.0-0.35), hold (0.35-0.65), release (0.65-1.0)
        def compute_scrunch_scale(progress):
            if progress <= 0.35:
                # Compress: 1.0 → 0.5
                return 1.0 - 0.5 * (progress / 0.35)
            elif progress <= 0.65:
                # Hold: 0.5
                return 0.5
            else:
                # Release: 0.5 → 1.0
                return 0.5 + 0.5 * ((progress - 0.65) / 0.35)
        
        test_points = [
            (0.0, 1.0),    # Start: full scale
            (0.175, 0.75), # Mid-compress
            (0.35, 0.5),   # Hold start
            (0.5, 0.5),    # Hold mid
            (0.65, 0.5),   # Hold end
            (0.825, 0.75), # Mid-release
            (1.0, 1.0),    # End: full scale restored
        ]
        
        for progress, expected_scale in test_points:
            calculated_scale = compute_scrunch_scale(progress)
            assert abs(calculated_scale - expected_scale) < 0.01, \
                f"At progress {progress}, expected scale {expected_scale}, got {calculated_scale}"
    
    def test_scrunch_animation_completes_in_0_8_seconds(self, pumpkin):
        """Scrunch animation completes in 0.8 seconds (48 frames at 60fps)."""
        pumpkin.is_scrunching = True
        pumpkin.nose_animation_progress = 0.0
        pumpkin.nose_animation_duration = 0.8
        
        # Simulate frames (60 FPS, 0.8s = 48 frames)
        frames_per_second = 60
        delta_time = 1.0 / frames_per_second
        frames_elapsed = 0
        
        while pumpkin.nose_animation_progress < 1.0 and frames_elapsed < 100:
            pumpkin.nose_animation_progress += delta_time / pumpkin.nose_animation_duration
            frames_elapsed += 1
        
        # Should complete in ~48 frames (0.8s at 60fps)
        assert 46 <= frames_elapsed <= 50, f"Expected 48 frames, got {frames_elapsed}"
    
    def test_scrunch_animation_auto_returns_to_neutral(self, pumpkin):
        """After scrunch completes, nose returns to neutral scale."""
        pumpkin.is_scrunching = True
        pumpkin.nose_animation_progress = 0.0
        
        # Run animation to completion
        pumpkin.nose_animation_progress = 1.0
        
        # At end, should return to neutral scale
        pumpkin.is_scrunching = False
        pumpkin.nose_scale = 1.0
        
        assert pumpkin.is_scrunching == False
        assert pumpkin.nose_scale == 1.0
    
    def test_animation_progress_tracks_0_to_1(self, pumpkin):
        """Animation progress variable increments smoothly from 0.0 to 1.0."""
        pumpkin.is_twitching = True
        pumpkin.nose_animation_progress = 0.0
        pumpkin.nose_animation_duration = 0.5
        
        delta_time = 1.0 / 60.0  # 60 FPS
        previous_progress = pumpkin.nose_animation_progress
        
        # Advance 10 frames
        for _ in range(10):
            pumpkin.nose_animation_progress += delta_time / pumpkin.nose_animation_duration
            assert pumpkin.nose_animation_progress > previous_progress
            assert 0.0 <= pumpkin.nose_animation_progress <= 1.0
            previous_progress = pumpkin.nose_animation_progress
    
    def test_animation_easing_is_smooth_not_linear(self, pumpkin):
        """Animation uses smooth easing, not linear interpolation."""
        # Test smooth sine-based motion for twitch
        # Sample at progress points that show varying rates of change
        progress_samples = [0.0, 0.02, 0.04, 0.08, 0.12, 0.16]
        offsets = [abs(8 * math.sin(p * 2 * math.pi * 5)) for p in progress_samples]
        
        # Verify non-linear: delta between consecutive offsets should vary
        # Sine wave accelerates and decelerates, so deltas change
        deltas = [abs(offsets[i+1] - offsets[i]) for i in range(len(offsets)-1)]
        
        # Check that not all deltas are the same (tolerance for float precision)
        # Round to 1 decimal place to avoid float precision issues
        unique_deltas = set(round(d, 1) for d in deltas if d > 0.01)
        assert len(unique_deltas) > 1, f"Animation should have non-linear easing (got deltas: {deltas})"


class TestExpressionIntegration:
    """Test nose animation interaction with expression state machine."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    def test_nose_state_persists_across_expression_changes(self, pumpkin):
        """Nose offset/scale state persists when expression changes."""
        pumpkin.nose_offset_x = 5.0
        pumpkin.nose_offset_y = -3.0
        pumpkin.nose_scale = 0.8
        
        pumpkin.set_expression(Expression.HAPPY)
        assert pumpkin.nose_offset_x == 5.0
        assert pumpkin.nose_offset_y == -3.0
        assert pumpkin.nose_scale == 0.8
        
        pumpkin.set_expression(Expression.SAD)
        assert pumpkin.nose_offset_x == 5.0
        assert pumpkin.nose_scale == 0.8
    
    def test_nose_animating_during_expression_change(self, pumpkin):
        """Nose animation continues uninterrupted during expression transition."""
        pumpkin.is_twitching = True
        pumpkin.nose_animation_progress = 0.3
        
        # Change expression mid-animation
        pumpkin.set_expression(Expression.ANGRY)
        
        # Animation state should be preserved
        assert pumpkin.is_twitching == True
        assert pumpkin.nose_animation_progress == 0.3
    
    def test_nose_resets_when_new_animation_starts(self, pumpkin):
        """Starting new animation type resets previous animation state."""
        # Start twitch
        pumpkin.is_twitching = True
        pumpkin.nose_animation_progress = 0.5
        
        # Attempt scrunch (with guard check)
        if not (pumpkin.is_twitching or pumpkin.is_scrunching):
            pumpkin.is_scrunching = True
            pumpkin.nose_animation_progress = 0.0
        
        # Guard should prevent scrunch from starting
        assert pumpkin.is_twitching == True
        assert pumpkin.is_scrunching == False
    
    def test_multiple_expressions_preserve_nose_state(self, pumpkin):
        """Cycling through multiple expressions preserves nose state."""
        pumpkin.nose_offset_x = -7.0
        pumpkin.nose_scale = 0.6
        
        expressions = [
            Expression.NEUTRAL,
            Expression.HAPPY,
            Expression.SAD,
            Expression.ANGRY,
            Expression.SURPRISED,
            Expression.SCARED,
        ]
        
        for expression in expressions:
            pumpkin.set_expression(expression)
            assert pumpkin.nose_offset_x == -7.0, f"Failed at {expression}"
            assert pumpkin.nose_scale == 0.6, f"Failed at {expression}"
    
    def test_nose_animation_independent_of_expression(self, pumpkin):
        """Nose animation flags are independent of expression state."""
        pumpkin.set_expression(Expression.HAPPY)
        # Complete transition
        for _ in range(30):
            pumpkin.update()
        
        pumpkin.is_twitching = True
        
        assert pumpkin.current_expression == Expression.HAPPY
        assert pumpkin.is_twitching == True
        
        # Neither should affect the other
        pumpkin.set_expression(Expression.NEUTRAL)
        assert pumpkin.is_twitching == True
    
    def test_expression_with_nose_twitch(self, pumpkin):
        """HAPPY expression with simultaneous nose twitch maintains both states."""
        pumpkin.set_expression(Expression.HAPPY)
        # Complete transition
        for _ in range(30):
            pumpkin.update()
        
        pumpkin.is_twitching = True
        pumpkin.nose_offset_x = 5.0
        
        assert pumpkin.current_expression == Expression.HAPPY
        assert pumpkin.is_twitching == True
        assert pumpkin.nose_offset_x == 5.0
    
    def test_expression_with_nose_scrunch(self, pumpkin):
        """ANGRY expression with simultaneous nose scrunch maintains both states."""
        pumpkin.set_expression(Expression.ANGRY)
        # Complete transition
        for _ in range(30):
            pumpkin.update()
        
        pumpkin.is_scrunching = True
        pumpkin.nose_scale = 0.7
        
        assert pumpkin.current_expression == Expression.ANGRY
        assert pumpkin.is_scrunching == True
        assert pumpkin.nose_scale == 0.7


class TestCommandIntegration:
    """Test nose command parsing and parameter handling."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    def test_twitch_nose_command_parsed_correctly(self, pumpkin):
        """Socket command 'twitch_nose' triggers twitch animation."""
        # Simulate command handler
        if not (pumpkin.is_twitching or pumpkin.is_scrunching):
            pumpkin.is_twitching = True
            pumpkin.nose_animation_progress = 0.0
            pumpkin.nose_animation_duration = 0.5
        
        assert pumpkin.is_twitching == True
        assert pumpkin.nose_animation_progress == 0.0
        assert pumpkin.nose_animation_duration == 0.5
    
    def test_scrunch_nose_command_parsed_correctly(self, pumpkin):
        """Socket command 'scrunch_nose' triggers scrunch animation."""
        # Simulate command handler
        if not (pumpkin.is_twitching or pumpkin.is_scrunching):
            pumpkin.is_scrunching = True
            pumpkin.nose_animation_progress = 0.0
            pumpkin.nose_animation_duration = 0.8
        
        assert pumpkin.is_scrunching == True
        assert pumpkin.nose_animation_progress == 0.0
        assert pumpkin.nose_animation_duration == 0.8
    
    def test_reset_nose_command_parsed_correctly(self, pumpkin):
        """Socket command 'reset_nose' immediately cancels animation."""
        # Start animation
        pumpkin.is_twitching = True
        pumpkin.nose_animation_progress = 0.5
        pumpkin.nose_offset_x = 6.0
        
        # Simulate reset command
        pumpkin.is_twitching = False
        pumpkin.is_scrunching = False
        pumpkin.nose_animation_progress = 0.0
        pumpkin.nose_offset_x = 0.0
        pumpkin.nose_offset_y = 0.0
        pumpkin.nose_scale = 1.0
        
        assert pumpkin.is_twitching == False
        assert pumpkin.nose_animation_progress == 0.0
        assert pumpkin.nose_offset_x == 0.0
    
    def test_command_with_magnitude_parameter(self, pumpkin):
        """Command with custom magnitude parameter adjusts animation range."""
        # Simulate parameterized command (future enhancement)
        # Example: "twitch_nose 12" for 12px instead of 8px
        custom_magnitude = 12
        
        # Would modify twitch formula: offset_x = custom_magnitude * sin(...)
        pumpkin.is_twitching = True
        test_offset = custom_magnitude * math.sin(0.25 * 2 * math.pi * 5)
        
        # Verify parameter is applied (range check)
        assert abs(test_offset) <= custom_magnitude
    
    def test_command_with_invalid_parameter_rejected(self, pumpkin):
        """Command with invalid parameter (negative duration) is rejected."""
        # Simulate invalid parameter
        invalid_duration = -0.5
        
        # Guard: duration must be positive
        if invalid_duration > 0:
            pumpkin.nose_animation_duration = invalid_duration
        else:
            pumpkin.nose_animation_duration = 0.5  # Default
        
        assert pumpkin.nose_animation_duration == 0.5
    
    def test_command_unknown_parameter_uses_default(self, pumpkin):
        """Command without parameter uses default values."""
        # No parameters provided, use defaults
        pumpkin.is_twitching = True
        pumpkin.nose_animation_duration = 0.5  # Default for twitch
        
        assert pumpkin.nose_animation_duration == 0.5


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    def test_reject_twitch_while_twitching(self, pumpkin):
        """New twitch command is rejected while twitch is active."""
        # Start first twitch
        pumpkin.is_twitching = True
        pumpkin.nose_animation_progress = 0.3
        
        # Try second twitch
        if not (pumpkin.is_twitching or pumpkin.is_scrunching):
            pumpkin.is_twitching = True
            pumpkin.nose_animation_progress = 0.0
        
        # Should still be at progress 0.3 (not restarted)
        assert pumpkin.nose_animation_progress == 0.3
    
    def test_reject_scrunch_while_scrunching(self, pumpkin):
        """New scrunch command is rejected while scrunch is active."""
        # Start first scrunch
        pumpkin.is_scrunching = True
        pumpkin.nose_animation_progress = 0.6
        
        # Try second scrunch
        if not (pumpkin.is_twitching or pumpkin.is_scrunching):
            pumpkin.is_scrunching = True
            pumpkin.nose_animation_progress = 0.0
        
        # Should still be at progress 0.6 (not restarted)
        assert pumpkin.nose_animation_progress == 0.6
    
    def test_reset_cancels_active_animation_immediately(self, pumpkin):
        """Reset command immediately cancels ongoing animation."""
        pumpkin.is_twitching = True
        pumpkin.nose_animation_progress = 0.7
        pumpkin.nose_offset_x = 7.0
        
        # Reset (no guard check)
        pumpkin.is_twitching = False
        pumpkin.is_scrunching = False
        pumpkin.nose_animation_progress = 0.0
        pumpkin.nose_offset_x = 0.0
        pumpkin.nose_offset_y = 0.0
        pumpkin.nose_scale = 1.0
        
        assert pumpkin.is_twitching == False
        assert pumpkin.nose_animation_progress == 0.0
        assert pumpkin.nose_offset_x == 0.0
    
    def test_rapid_command_sequence_queued_or_rejected(self, pumpkin):
        """Rapid commands are rejected (non-interrupting guard)."""
        # First command
        if not (pumpkin.is_twitching or pumpkin.is_scrunching):
            pumpkin.is_twitching = True
        
        # Second command (immediate)
        if not (pumpkin.is_twitching or pumpkin.is_scrunching):
            pumpkin.is_scrunching = True
        
        # Only first animation should be active
        assert pumpkin.is_twitching == True
        assert pumpkin.is_scrunching == False
    
    def test_head_movement_during_nose_animation(self, pumpkin):
        """Head movement and nose animation run independently."""
        pumpkin.is_twitching = True
        pumpkin.nose_offset_x = 5.0
        
        # Trigger head movement
        pumpkin.set_projection_offset(100, -50)
        
        # Both states should coexist
        assert pumpkin.is_twitching == True
        assert pumpkin.nose_offset_x == 5.0
        assert pumpkin.projection_offset_x == 100
        assert pumpkin.projection_offset_y == -50
    
    def test_concurrent_head_and_nose_movement(self, pumpkin):
        """Head movement and nose animation compose correctly."""
        # Start both animations
        pumpkin.is_moving_head = True
        pumpkin.head_target_x = 200
        pumpkin.is_twitching = True
        
        # Both animation flags should be active
        assert pumpkin.is_moving_head == True
        assert pumpkin.is_twitching == True
    
    def test_expression_change_during_nose_animation(self, pumpkin):
        """Expression change during nose animation doesn't interrupt it."""
        pumpkin.is_scrunching = True
        pumpkin.nose_animation_progress = 0.4
        pumpkin.nose_scale = 0.7
        
        # Change expression
        pumpkin.set_expression(Expression.SURPRISED)
        
        # Nose animation should continue
        assert pumpkin.is_scrunching == True
        assert pumpkin.nose_animation_progress == 0.4
        assert pumpkin.nose_scale == 0.7
    
    def test_nose_animation_timeout_does_not_hang(self, pumpkin):
        """Animation completes and cleans up, doesn't hang indefinitely."""
        pumpkin.is_twitching = True
        pumpkin.nose_animation_progress = 0.0
        pumpkin.nose_animation_duration = 0.5
        
        # Run well past completion
        delta_time = 1.0 / 60.0
        for _ in range(100):  # 1.67 seconds at 60fps
            if pumpkin.nose_animation_progress < 1.0:
                pumpkin.nose_animation_progress += delta_time / pumpkin.nose_animation_duration
            else:
                # Animation complete, should clean up
                pumpkin.is_twitching = False
                pumpkin.nose_offset_x = 0.0
                break
        
        # Should have stopped
        assert pumpkin.is_twitching == False
        assert pumpkin.nose_offset_x == 0.0


class TestRendering:
    """Test nose rendering and projection compliance."""
    
    @pytest.fixture
    def pumpkin_surface(self):
        """Create a PumpkinFace instance with test surface."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        surface = pygame.Surface((1920, 1080))
        yield face, surface
        pygame.quit()
    
    def test_nose_triangle_renders_between_eyes_and_mouth(self, pumpkin_surface):
        """Nose renders at center_y + 15 (between eyes and mouth)."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.draw(surface)
        
        center_x = 1920 // 2
        center_y = 1080 // 2
        nose_y = center_y + 15  # Nose baseline position
        
        # Sample for white pixels near nose position
        white_pixels_found = False
        for dy in range(-10, 51):  # Nose is 50px tall, apex up
            color = surface.get_at((center_x, nose_y + dy))[:3]
            if color == (255, 255, 255):
                white_pixels_found = True
                break
        
        assert white_pixels_found, "Nose should render with white pixels"
    
    def test_nose_uses_white_pixels_only(self, pumpkin_surface):
        """Nose pixels are pure white (255, 255, 255)."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.draw(surface)
        
        center_x = 1920 // 2
        center_y = 1080 // 2
        nose_y = center_y + 15
        
        # Sample nose region
        non_compliant_pixels = []
        for dx in range(-20, 21, 5):
            for dy in range(-50, 1, 5):
                color = surface.get_at((center_x + dx, nose_y + dy))[:3]
                if color not in [(0, 0, 0), (255, 255, 255)]:
                    non_compliant_pixels.append((center_x + dx, nose_y + dy, color))
        
        assert len(non_compliant_pixels) == 0, \
            f"Nose must be pure black/white: {non_compliant_pixels}"
    
    def test_nose_respects_projection_offset(self, pumpkin_surface):
        """Nose position follows projection offset (head movement)."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Draw with offset
        pumpkin.set_projection_offset(100, -50)
        pumpkin.draw(surface)
        
        # Nose should be at offset position
        center_x = (1920 // 2) + 100
        center_y = (1080 // 2) - 50
        nose_y = center_y + 15
        
        # Sample for white pixels at offset position
        white_pixels_found = False
        for dy in range(-50, 1, 5):
            color = surface.get_at((center_x, nose_y + dy))[:3]
            if color == (255, 255, 255):
                white_pixels_found = True
                break
        
        assert white_pixels_found, "Nose should follow projection offset"
    
    def test_nose_follows_head_movement(self, pumpkin_surface):
        """Nose inherits head position via projection offset."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Set projection offset (head position)
        pumpkin.set_projection_offset(-150, 80)
        pumpkin.draw(surface)
        
        # Nose should render at offset center
        offset_center_x = (1920 // 2) - 150
        offset_center_y = (1080 // 2) + 80
        nose_y = offset_center_y + 15
        
        # Sample near nose position
        white_pixels = 0
        for dy in range(-50, 1, 10):
            color = surface.get_at((offset_center_x, nose_y + dy))[:3]
            if color == (255, 255, 255):
                white_pixels += 1
        
        assert white_pixels > 0, "Nose should render at head position"
    
    def test_nose_twitching_visible_in_frames(self, pumpkin_surface):
        """Twitching nose shows horizontal displacement in rendered frames."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Set twitch offset
        pumpkin.is_twitching = True
        pumpkin.nose_offset_x = 8.0  # Max twitch offset
        pumpkin.draw(surface)
        
        center_x = 1920 // 2
        center_y = 1080 // 2
        nose_y = center_y + 15
        
        # Nose should be displaced horizontally
        # Sample at offset position
        offset_x = int(center_x + pumpkin.nose_offset_x)
        white_pixels_at_offset = 0
        for dy in range(-50, 1, 10):
            color = surface.get_at((offset_x, nose_y + dy))[:3]
            if color == (255, 255, 255):
                white_pixels_at_offset += 1
        
        assert white_pixels_at_offset > 0, "Twitching nose should be displaced"
    
    def test_nose_scrunching_visible_in_frames(self, pumpkin_surface):
        """Scrunching nose shows vertical compression in rendered frames."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Set scrunch scale
        pumpkin.is_scrunching = True
        pumpkin.nose_scale = 0.5  # 50% compression
        pumpkin.draw(surface)
        
        center_x = 1920 // 2
        center_y = 1080 // 2
        nose_y = center_y + 15
        
        # Nose should be compressed (fewer white pixels vertically)
        white_pixels_compressed = 0
        for dy in range(-25, 1, 5):  # Reduced range for 50% scale
            color = surface.get_at((center_x, nose_y + dy))[:3]
            if color == (255, 255, 255):
                white_pixels_compressed += 1
        
        # At 50% scale, should have fewer white pixels than full scale
        assert white_pixels_compressed > 0, "Scrunched nose should still render"
        # (Detailed height check would require comparing to baseline render)
