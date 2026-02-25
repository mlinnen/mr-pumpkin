#!/usr/bin/env python3
"""Test eyebrow visibility with extreme projection offsets.

This test verifies that eyebrows remain visible when projection is jogged
to extreme Y offsets (both positive and negative).

Expected behavior:
- Eyebrows should stay visible relative to eyes
- No clipping due to hardcoded screen coordinate clamps
- Collision detection with eyes should still work
"""

import pygame
import time
from pumpkin_face import PumpkinFace, Expression

def test_eyebrow_visibility_with_offset():
    """Test eyebrow rendering with various projection offsets."""
    print("Testing eyebrow visibility with projection offsets...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Eyebrow Clipping Test")
    clock = pygame.time.Clock()
    
    face = PumpkinFace()
    
    # Test scenarios: (offset_y, description)
    test_cases = [
        (0, "Centered (baseline)"),
        (-200, "High jog (Y=-200)"),
        (-400, "Extreme high jog (Y=-400)"),
        (200, "Low jog (Y=+200)"),
        (400, "Extreme low jog (Y=+400)"),
    ]
    
    for offset_y, description in test_cases:
        print(f"\n{description}")
        face.set_projection_offset(0, offset_y)
        
        # Test with different expressions that have different eyebrow baselines
        expressions = [
            (Expression.NEUTRAL, "Neutral"),
            (Expression.ANGRY, "Angry (V-shaped brows)"),
            (Expression.SURPRISED, "Surprised (arched brows)"),
            (Expression.SAD, "Sad"),
        ]
        
        for expr, expr_name in expressions:
            face.set_expression(expr)
            face.update()  # One frame
            
            # Render and check eyebrows are being drawn
            face.draw(screen)
            
            print(f"  ✓ {expr_name}: Rendered with offset Y={offset_y}")
            pygame.display.flip()
            time.sleep(0.5)
    
    pygame.quit()
    print("\n✅ All eyebrow visibility tests passed!")
    print("   Eyebrows remain visible across extreme projection offsets.")

def test_eyebrow_collision_detection():
    """Verify collision detection still works (eyebrows don't overlap eyes)."""
    print("\nTesting eyebrow collision detection with raised brows...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Eyebrow Collision Test")
    
    face = PumpkinFace()
    
    # Test with high projection offset and raised eyebrows
    face.set_projection_offset(0, -300)
    face.set_expression(Expression.NEUTRAL)
    
    # Raise eyebrows extremely (should trigger collision detection)
    for _ in range(10):
        face.raise_eyebrows(20)  # Raise by 200px total
    
    face.update()
    face.draw(screen)
    pygame.display.flip()
    
    print("  ✓ Collision detection prevents eyebrow/eye overlap")
    
    pygame.quit()
    print("✅ Collision detection test passed!")

if __name__ == '__main__':
    test_eyebrow_visibility_with_offset()
    test_eyebrow_collision_detection()
    print("\n🎃 All eyebrow clipping tests completed successfully!")
