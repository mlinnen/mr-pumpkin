"""Quick validation of rolling eyes state machine logic."""

import sys
sys.path.insert(0, '.')

from pumpkin_face import PumpkinFace

def test_rolling_state_machine():
    """Test rolling eyes state machine without GUI."""
    print("Testing rolling eyes state machine...")
    
    # Create pumpkin face instance (won't run GUI)
    pumpkin = PumpkinFace(width=800, height=600)
    
    # Test initial state
    assert pumpkin.is_rolling == False
    assert pumpkin.rolling_progress == 0.0
    assert pumpkin.pupil_angle == 0.0 or hasattr(pumpkin, 'pupil_angle')
    print("✓ Initial state correct")
    
    # Test clockwise roll activation
    pumpkin.roll_clockwise()
    assert pumpkin.is_rolling == True
    assert pumpkin.rolling_progress == 0.0
    assert pumpkin.rolling_direction == 'clockwise'
    print("✓ Clockwise roll activated")
    
    # Test progress updates
    for _ in range(60):  # Simulate 1 second at 60 FPS
        pumpkin.update()
    
    # Should have completed and reset
    assert pumpkin.is_rolling == False
    assert pumpkin.rolling_progress == 0.0
    print("✓ Roll completed after 1 second")
    
    # Test counter-clockwise roll
    pumpkin.roll_counterclockwise()
    assert pumpkin.is_rolling == True
    assert pumpkin.rolling_direction == 'counterclockwise'
    print("✓ Counter-clockwise roll activated")
    
    # Reset
    pumpkin.is_rolling = False
    pumpkin.rolling_progress = 0.0
    
    # Test pause during blink
    pumpkin.roll_clockwise()
    assert pumpkin.is_rolling == True
    
    # Update a few frames
    for _ in range(10):
        pumpkin.update()
    
    progress_before_blink = pumpkin.rolling_progress
    assert progress_before_blink > 0.0
    print(f"✓ Roll progress before blink: {progress_before_blink:.3f}")
    
    # Trigger blink
    pumpkin.blink()
    assert pumpkin.is_blinking == True
    
    # Update during blink - rolling should pause
    for _ in range(10):
        pumpkin.update()
    
    # Rolling progress should stay constant during blink
    assert pumpkin.rolling_progress == progress_before_blink
    print("✓ Rolling paused during blink")
    
    # Complete blink
    while pumpkin.is_blinking:
        pumpkin.update()
    
    # Now rolling should resume
    pumpkin.update()
    assert pumpkin.rolling_progress > progress_before_blink
    print("✓ Rolling resumed after blink")
    
    # Test guard against interrupting roll
    pumpkin.is_rolling = True
    pumpkin.rolling_progress = 0.5
    pumpkin.rolling_direction = 'clockwise'
    
    pumpkin.roll_counterclockwise()  # Try to interrupt
    assert pumpkin.rolling_direction == 'clockwise'  # Should still be clockwise
    assert pumpkin.rolling_progress == 0.5  # Progress unchanged
    print("✓ Guard prevents interrupting ongoing roll")
    
    print("\n✅ All rolling eyes state machine tests passed!")

if __name__ == "__main__":
    test_rolling_state_machine()
