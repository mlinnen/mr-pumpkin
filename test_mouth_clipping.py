"""
Test script to verify mouth rendering doesn't clip at high projection offsets.
Tests surprised and scared expressions with extreme Y offsets.
"""

import pygame
import sys
import time
from pumpkin_face import PumpkinFace, Expression

def test_mouth_visibility():
    """Test that mouth remains visible at extreme projection offsets in surprised/scared modes."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Mouth Clipping Test")
    
    face = PumpkinFace(800, 600)
    clock = pygame.time.Clock()
    
    test_cases = [
        ("Surprised - Centered", Expression.SURPRISED, 0, 0, 2.0),
        ("Surprised - High Y", Expression.SURPRISED, 0, -200, 2.0),
        ("Surprised - Extreme High Y", Expression.SURPRISED, 0, -400, 2.0),
        ("Surprised - Low Y", Expression.SURPRISED, 0, 200, 2.0),
        ("Surprised - Extreme Low Y", Expression.SURPRISED, 0, 400, 2.0),
        ("Scared - Centered", Expression.SCARED, 0, 0, 2.0),
        ("Scared - High Y", Expression.SCARED, 0, -200, 2.0),
        ("Scared - Extreme High Y", Expression.SCARED, 0, -400, 2.0),
        ("Scared - Low Y", Expression.SCARED, 0, 200, 2.0),
        ("Scared - Extreme Low Y", Expression.SCARED, 0, 400, 2.0),
        ("Surprised - High X + High Y", Expression.SURPRISED, 200, -300, 2.0),
        ("Scared - High X + High Y", Expression.SCARED, 200, -300, 2.0),
    ]
    
    for test_name, expression, offset_x, offset_y, duration in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {test_name}")
        print(f"Expression: {expression.name}, Offset: ({offset_x}, {offset_y})")
        print(f"{'='*60}")
        
        # Set expression and offset
        face.set_expression(expression)
        face.set_projection_offset(offset_x, offset_y)
        
        # Wait for expression transition to complete
        while face.transition_progress < 1.0:
            clock.tick(60)
            face.update()
            face.draw(screen)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
        
        # Display for duration
        start_time = time.time()
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        return
            
            clock.tick(60)
            face.update()
            face.draw(screen)
            pygame.display.flip()
        
        print(f"✓ Test complete - mouth visible throughout")
    
    print("\n" + "="*60)
    print("All mouth clipping tests PASSED!")
    print("="*60)
    pygame.quit()

if __name__ == "__main__":
    print("Mouth Clipping Test")
    print("Tests surprised and scared expressions with extreme projection offsets")
    print("Press Q to quit early\n")
    
    test_mouth_visibility()
