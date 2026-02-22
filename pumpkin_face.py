import pygame
import math
import socket
import threading
import sys
from enum import Enum
from typing import Tuple

class Expression(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    SCARED = "scared"
    SLEEPING = "sleeping"

class PumpkinFace:
    def __init__(self, width: int = 1920, height: int = 1080, monitor: int = 0, fullscreen: bool = True):
        self.width = width
        self.height = height
        self.monitor = monitor
        self.fullscreen = fullscreen
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_expression = Expression.NEUTRAL
        self.target_expression = Expression.NEUTRAL
        self.transition_progress = 1.0
        self.transition_speed = 0.05
        
        # Blink animation state
        self.is_blinking = False
        self.blink_progress = 0.0
        self.blink_speed = 0.03  # Slower than transition_speed (0.05)
        self.pre_blink_expression = None  # Expression to return to after blink
        
        # Wink animation state
        self.is_winking = False
        self.winking_eye = None  # 'left' or 'right'
        self.wink_progress = 0.0
        self.wink_speed = 0.03
        self.pre_wink_expression = None
        self.left_eye_scale = 1.0
        self.right_eye_scale = 1.0
        
        # Rolling eyes animation state
        self.is_rolling = False
        self.rolling_progress = 0.0
        self.rolling_direction = 'clockwise'  # 'clockwise' or 'counterclockwise'
        self.rolling_duration = 1.0  # 360° rotation in 1 second
        self.rolling_speed = 0.01  # Speed of rolling progress per frame
        self.rolling_start_angle = None  # Angle where rolling started
        self.pupil_angle = 225.0  # Current pupil angle in degrees (225° = upper-left)
        
        # Gaze control state (per-eye X/Y angles)
        # Default (-45°, 45°) matches original 225° position (upper-left) for backward compatibility
        self.pupil_angle_left = (-45.0, 45.0)   # (x_angle, y_angle) where 0,0 = straight ahead
        self.pupil_angle_right = (-45.0, 45.0)  # +X = right, +Y = up, range ±90°
        
        # Eyebrow control state (orthogonal to expression state machine)
        # Sign convention: NEGATIVE = raise (up), POSITIVE = lower (down) — screen Y coords
        self.eyebrow_left_offset = 0.0   # pixels, clamped [-50, +50]
        self.eyebrow_right_offset = 0.0  # pixels, clamped [-50, +50]
        
        # Colors - optimized for projection mapping
        self.BACKGROUND_COLOR = (0, 0, 0)  # Black background for projection
        self.FEATURE_COLOR = (255, 255, 255)  # White features (eyes, nose, mouth)
    
    @property
    def left_eye_gaze_x(self):
        """X angle for left eye (-90 to +90 degrees)."""
        return self.pupil_angle_left[0]
    
    @property
    def left_eye_gaze_y(self):
        """Y angle for left eye (-90 to +90 degrees)."""
        return self.pupil_angle_left[1]
    
    @property
    def right_eye_gaze_x(self):
        """X angle for right eye (-90 to +90 degrees)."""
        return self.pupil_angle_right[0]
    
    @property
    def right_eye_gaze_y(self):
        """Y angle for right eye (-90 to +90 degrees)."""
        return self.pupil_angle_right[1]
        
    def draw(self, surface: pygame.Surface):
        # Black background for projection
        surface.fill(self.BACKGROUND_COLOR)
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Calculate eye and mouth positions based on expression
        left_eye_pos, right_eye_pos = self._get_eye_positions(center_x, center_y)
        mouth_points = self._get_mouth_points(center_x, center_y)
        
        # Draw eyes
        self._draw_eyes(surface, left_eye_pos, right_eye_pos)
        
        # Draw mouth
        self._draw_mouth(surface, mouth_points)
    
    def _get_eye_positions(self, cx: int, cy: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        eye_y_offset = -50
        left_x = cx - 100
        right_x = cx + 100
        
        if self.current_expression == Expression.HAPPY:
            eye_y_offset = -30
        elif self.current_expression == Expression.SAD:
            eye_y_offset = -70
        elif self.current_expression == Expression.SURPRISED:
            eye_y_offset = -20
        elif self.current_expression == Expression.SCARED:
            eye_y_offset = -40
        
        return (int(left_x), int(cy + eye_y_offset)), (int(right_x), int(cy + eye_y_offset))
    
    def _get_mouth_points(self, cx: int, cy: int) -> list:
        mouth_y = cy + 80
        mouth_width = 150
        
        if self.current_expression == Expression.HAPPY:
            # Smile
            points = []
            for i in range(0, 101):
                x = cx - mouth_width + (i / 100) * (mouth_width * 2)
                y = mouth_y - math.sin(i / 100 * math.pi) * 60
                points.append((int(x), int(y)))
            return points
        elif self.current_expression == Expression.SAD:
            # Frown
            points = []
            for i in range(0, 101):
                x = cx - mouth_width + (i / 100) * (mouth_width * 2)
                y = mouth_y + math.sin(i / 100 * math.pi) * 40
                points.append((int(x), int(y)))
            return points
        elif self.current_expression == Expression.ANGRY:
            # Angry mouth
            return [(int(cx - mouth_width), int(mouth_y + 20)), (int(cx + mouth_width), int(mouth_y - 20))]
        elif self.current_expression == Expression.SURPRISED:
            # Open mouth (O shape)
            return []
        elif self.current_expression == Expression.SCARED:
            # Scared open mouth
            return []
        
        # Neutral
        return [(int(cx - mouth_width), int(mouth_y)), (int(cx + mouth_width), int(mouth_y))]
    
    def _draw_eyes(self, surface: pygame.Surface, left_pos: Tuple[int, int], right_pos: Tuple[int, int]):
        eye_radius = 40
        
        if self.current_expression == Expression.SURPRISED:
            eye_radius = 50
        elif self.current_expression == Expression.SCARED:
            eye_radius = 45
        
        # Calculate blink state
        eye_scale = 1.0
        if self.is_blinking:
            if self.blink_progress <= 0.5:
                # Closing phase (0.0 to 0.5)
                eye_scale = 1.0 - (self.blink_progress * 2.0)
            elif self.blink_progress <= 0.55:
                # Hold closed (0.5 to 0.55)
                eye_scale = 0.0
            else:
                # Opening phase (0.55 to 1.0)
                eye_scale = (self.blink_progress - 0.55) / 0.45
        
        # Sleeping expression or fully closed blink - closed eyes as horizontal white lines
        if self.current_expression == Expression.SLEEPING or (self.is_blinking and eye_scale == 0.0):
            line_width = 60
            line_thickness = 8
            # Left closed eye
            pygame.draw.line(surface, self.FEATURE_COLOR, 
                           (left_pos[0] - line_width // 2, left_pos[1]), 
                           (left_pos[0] + line_width // 2, left_pos[1]), 
                           line_thickness)
            # Right closed eye
            pygame.draw.line(surface, self.FEATURE_COLOR, 
                           (right_pos[0] - line_width // 2, right_pos[1]), 
                           (right_pos[0] + line_width // 2, right_pos[1]), 
                           line_thickness)
            return
        
        # Scale eye height for blink animation
        scaled_radius_vertical = int(eye_radius * eye_scale)
        if scaled_radius_vertical == 0:
            scaled_radius_vertical = 1  # Minimum for rendering
        
        # Left eye - white filled ellipse for projection (scaled vertically during blink)
        if eye_scale < 1.0:
            pygame.draw.ellipse(surface, self.FEATURE_COLOR, 
                              (left_pos[0] - eye_radius, left_pos[1] - scaled_radius_vertical,
                               eye_radius * 2, scaled_radius_vertical * 2))
        else:
            pygame.draw.circle(surface, self.FEATURE_COLOR, left_pos, eye_radius)
        
        # Right eye - white filled ellipse for projection (scaled vertically during blink)
        if eye_scale < 1.0:
            pygame.draw.ellipse(surface, self.FEATURE_COLOR, 
                              (right_pos[0] - eye_radius, right_pos[1] - scaled_radius_vertical,
                               eye_radius * 2, scaled_radius_vertical * 2))
        else:
            pygame.draw.circle(surface, self.FEATURE_COLOR, right_pos, eye_radius)
        
        # Draw pupils as black circles (scale with eye, position based on gaze angles or rolling)
        pupil_radius = int(15 * eye_scale)
        # Orbit radius with safety margin: eye_radius(40) - pupil_radius(15) - safety(10.86) ≈ 14.14
        pupil_orbit_radius = int(math.sqrt(200) * eye_scale)
        
        if pupil_radius > 0:
            # Determine pupil position: use rolling animation if active, otherwise use gaze angles
            if self.is_rolling:
                # Rolling eyes: both pupils follow pupil_angle (circular motion)
                angle_rad = math.radians(self.pupil_angle)
                left_pupil_x = int(left_pos[0] + pupil_orbit_radius * math.cos(angle_rad))
                left_pupil_y = int(left_pos[1] + pupil_orbit_radius * math.sin(angle_rad))
                right_pupil_x = int(right_pos[0] + pupil_orbit_radius * math.cos(angle_rad))
                right_pupil_y = int(right_pos[1] + pupil_orbit_radius * math.sin(angle_rad))
            else:
                # Gaze control: convert X/Y angles to pixel offsets independently per eye
                left_pupil_x, left_pupil_y = self._angle_to_pixel(left_pos, self.pupil_angle_left, pupil_orbit_radius)
                right_pupil_x, right_pupil_y = self._angle_to_pixel(right_pos, self.pupil_angle_right, pupil_orbit_radius)
            
            pygame.draw.circle(surface, self.BACKGROUND_COLOR, (left_pupil_x, left_pupil_y), pupil_radius)
            pygame.draw.circle(surface, self.BACKGROUND_COLOR, (right_pupil_x, right_pupil_y), pupil_radius)
    
    def _angle_to_pixel(self, eye_center: Tuple[int, int], angles: Tuple[float, float], orbit_radius: int) -> Tuple[int, int]:
        """Convert gaze X/Y angles to pupil pixel position.
        
        Args:
            eye_center: (x, y) position of eye center
            angles: (x_angle, y_angle) where 0,0 = straight ahead, +X = right, +Y = up
            orbit_radius: maximum radius pupils can move from center
            
        Returns:
            (x, y) pixel position for pupil
        """
        x_angle, y_angle = angles
        
        # Clamp angles to ±90° to prevent pupils from going outside eyes
        x_angle = max(-90.0, min(90.0, x_angle))
        y_angle = max(-90.0, min(90.0, y_angle))
        
        # Convert angles to radians
        x_angle_rad = math.radians(x_angle)
        y_angle_rad = math.radians(y_angle)
        
        # Calculate pixel offsets: +X angle = right (+cos), +Y angle = up (-sin for screen coords)
        # Use sin for angle mapping: at 0° no offset, at ±90° max offset
        offset_x = orbit_radius * math.sin(x_angle_rad)
        offset_y = -orbit_radius * math.sin(y_angle_rad)  # Negative because screen Y increases downward
        
        pupil_x = int(eye_center[0] + offset_x)
        pupil_y = int(eye_center[1] + offset_y)
        
        return (pupil_x, pupil_y)
    
    def _gaze_to_angle(self, gaze: Tuple[float, float]) -> float:
        """Convert gaze X/Y angles to circular angle for rolling animation.
        
        Args:
            gaze: (x_angle, y_angle) where 0,0 = straight ahead, +X = right, +Y = up
            
        Returns:
            Circular angle in degrees (0° = right, 90° = down, 180° = left, 270° = up)
        """
        x_angle, y_angle = gaze
        
        # Convert angles to radians
        x_rad = math.radians(x_angle)
        y_rad = math.radians(y_angle)
        
        # Calculate unit vector from gaze angles
        # X: positive = right, Y: positive = up (but screen coords are inverted)
        offset_x = math.sin(x_rad)
        offset_y = -math.sin(y_rad)  # Invert Y for screen coordinates
        
        # Convert to circular angle using atan2
        # atan2(y, x) gives angle in radians, convert to degrees
        angle_rad = math.atan2(offset_y, offset_x)
        angle_deg = math.degrees(angle_rad)
        
        # Normalize to 0-360 range
        return angle_deg % 360
    
    def _draw_mouth(self, surface: pygame.Surface, points: list):
        if not points or len(points) < 2:
            if self.current_expression == Expression.SURPRISED:
                # O-shaped mouth - white filled circle
                pygame.draw.circle(surface, self.FEATURE_COLOR, (self.width // 2, self.height // 2 + 80), 30)
            elif self.current_expression == Expression.SCARED:
                # Scared mouth - white filled ellipse
                pygame.draw.ellipse(surface, self.FEATURE_COLOR, 
                                   (self.width // 2 - 40, self.height // 2 + 70, 80, 50))
            return
        
        # Draw thick white lines for mouth curves
        for i in range(len(points) - 1):
            p1 = (int(points[i][0]), int(points[i][1]))
            p2 = (int(points[i+1][0]), int(points[i+1][1]))
            pygame.draw.line(surface, self.FEATURE_COLOR, p1, p2, 8)
    
    def set_eyebrow(self, left: float, right: float = None):
        """Set eyebrow offsets. Negative = raise, positive = lower. Clamped to [-50, +50].
        
        Args:
            left: Offset for left eyebrow (if right not provided, applies to both)
            right: Offset for right eyebrow (optional)
        """
        def clamp(v): return max(-50.0, min(50.0, float(v)))
        self.eyebrow_left_offset = clamp(left)
        self.eyebrow_right_offset = clamp(right if right is not None else left)

    def raise_eyebrows(self, step: float = 10.0):
        """Raise both eyebrows by step pixels."""
        self.eyebrow_left_offset = max(-50.0, self.eyebrow_left_offset - step)
        self.eyebrow_right_offset = max(-50.0, self.eyebrow_right_offset - step)

    def lower_eyebrows(self, step: float = 10.0):
        """Lower both eyebrows by step pixels."""
        self.eyebrow_left_offset = min(50.0, self.eyebrow_left_offset + step)
        self.eyebrow_right_offset = min(50.0, self.eyebrow_right_offset + step)

    def raise_eyebrow_left(self, step: float = 10.0):
        """Raise left eyebrow by step pixels."""
        self.eyebrow_left_offset = max(-50.0, self.eyebrow_left_offset - step)

    def lower_eyebrow_left(self, step: float = 10.0):
        """Lower left eyebrow by step pixels."""
        self.eyebrow_left_offset = min(50.0, self.eyebrow_left_offset + step)

    def raise_eyebrow_right(self, step: float = 10.0):
        """Raise right eyebrow by step pixels."""
        self.eyebrow_right_offset = max(-50.0, self.eyebrow_right_offset - step)

    def lower_eyebrow_right(self, step: float = 10.0):
        """Lower right eyebrow by step pixels."""
        self.eyebrow_right_offset = min(50.0, self.eyebrow_right_offset + step)

    def reset_eyebrows(self):
        """Reset both eyebrows to neutral position."""
        self.eyebrow_left_offset = 0.0
        self.eyebrow_right_offset = 0.0

    def set_expression(self, expression: Expression):
        if expression != self.current_expression:
            self.target_expression = expression
            self.transition_progress = 0.0
    
    def blink(self):
        if not self.is_blinking:  # Don't interrupt an ongoing blink
            self.is_blinking = True
            self.blink_progress = 0.0
            self.pre_blink_expression = self.current_expression
    
    def wink_left(self):
        if not self.is_winking:
            self.is_winking = True
            self.winking_eye = 'left'
            self.wink_progress = 0.0
            self.pre_wink_expression = self.current_expression
    
    def wink_right(self):
        if not self.is_winking:
            self.is_winking = True
            self.winking_eye = 'right'
            self.wink_progress = 0.0
            self.pre_wink_expression = self.current_expression
    
    def gaze(self, *args):
        """Set gaze direction for one or both eyes.
        
        Supports two calling modes:
        - gaze(x, y): Both eyes look at (x, y) angles
        - gaze(x1, y1, x2, y2): Left eye at (x1, y1), right eye at (x2, y2)
        
        Args:
            x, y: Angles for both eyes (if 2 args)
            x1, y1, x2, y2: Left eye (x1, y1), right eye (x2, y2) angles (if 4 args)
            
        Angles: 0° = straight ahead, +X = right, +Y = up, range ±90° (auto-clamped)
        """
        if len(args) == 2:
            # Both eyes look same direction
            try:
                x, y = float(args[0]), float(args[1])
            except (ValueError, TypeError):
                raise TypeError(f"gaze() arguments must be numeric")
            x = max(-90.0, min(90.0, x))
            y = max(-90.0, min(90.0, y))
            self.pupil_angle_left = (x, y)
            self.pupil_angle_right = (x, y)
        elif len(args) == 4:
            # Independent eye control
            try:
                x1, y1, x2, y2 = float(args[0]), float(args[1]), float(args[2]), float(args[3])
            except (ValueError, TypeError):
                raise TypeError(f"gaze() arguments must be numeric")
            x1 = max(-90.0, min(90.0, x1))
            y1 = max(-90.0, min(90.0, y1))
            x2 = max(-90.0, min(90.0, x2))
            y2 = max(-90.0, min(90.0, y2))
            self.pupil_angle_left = (x1, y1)
            self.pupil_angle_right = (x2, y2)
        else:
            raise TypeError(f"gaze() takes 2 or 4 arguments ({len(args)} given)")
    
    def get_left_eye_gaze(self):
        """Get current gaze angles for left eye."""
        return self.pupil_angle_left
    
    def get_right_eye_gaze(self):
        """Get current gaze angles for right eye."""
        return self.pupil_angle_right
    
    def roll_clockwise(self):
        if not self.is_rolling:  # Don't interrupt an ongoing roll
            self.is_rolling = True
            self.rolling_progress = 0.0
            self.rolling_direction = 'clockwise'
            # Capture current gaze state before rolling
            self.pre_rolling_gaze_left = self.pupil_angle_left
            self.pre_rolling_gaze_right = self.pupil_angle_right
            # Convert current gaze to circular angle for rolling start position
            self.rolling_start_angle = self._gaze_to_angle(self.pupil_angle_left)
            self.pupil_angle = self.rolling_start_angle

    def roll_counterclockwise(self):
        if not self.is_rolling:  # Don't interrupt an ongoing roll
            self.is_rolling = True
            self.rolling_progress = 0.0
            self.rolling_direction = 'counterclockwise'
            # Capture current gaze state before rolling
            self.pre_rolling_gaze_left = self.pupil_angle_left
            self.pre_rolling_gaze_right = self.pupil_angle_right
            # Convert current gaze to circular angle for rolling start position
            self.rolling_start_angle = self._gaze_to_angle(self.pupil_angle_left)
            self.pupil_angle = self.rolling_start_angle

    def roll_eyes_clockwise(self):
        if not self.is_rolling:  # Don't interrupt an ongoing roll
            self.is_rolling = True
            self.rolling_progress = 0.0
            self.rolling_direction = 'clockwise'
            # Capture current gaze state before rolling
            self.pre_rolling_gaze_left = self.pupil_angle_left
            self.pre_rolling_gaze_right = self.pupil_angle_right
            # Convert current gaze to circular angle for rolling start position
            self.rolling_start_angle = self._gaze_to_angle(self.pupil_angle_left)
            self.pupil_angle = self.rolling_start_angle

    def roll_eyes_counterclockwise(self):
        if not self.is_rolling:  # Don't interrupt an ongoing roll
            self.is_rolling = True
            self.rolling_progress = 0.0
            self.rolling_direction = 'counterclockwise'
            # Capture current gaze state before rolling
            self.pre_rolling_gaze_left = self.pupil_angle_left
            self.pre_rolling_gaze_right = self.pupil_angle_right
            # Convert current gaze to circular angle for rolling start position
            self.rolling_start_angle = self._gaze_to_angle(self.pupil_angle_left)
            self.pupil_angle = self.rolling_start_angle
    
    def set_gaze(self, x1: float, y1: float, x2: float = None, y2: float = None):
        """Set gaze angles for one or both eyes.
        
        Args:
            x1: X angle for both eyes (if x2/y2 not provided) or left eye X
            y1: Y angle for both eyes (if x2/y2 not provided) or left eye Y
            x2: Right eye X angle (optional)
            y2: Right eye Y angle (optional)
        
        Angles are clamped to [-90, 90] range.
        0 degrees = straight ahead, +X = right, +Y = up
        """
        # Clamp values to ±90°
        def clamp(value: float) -> float:
            return max(-90.0, min(90.0, value))
        
        if x2 is None or y2 is None:
            # Two args: apply same angles to both eyes
            self.pupil_angle_left = (clamp(x1), clamp(y1))
            self.pupil_angle_right = (clamp(x1), clamp(y1))
        else:
            # Four args: independent eye control
            self.pupil_angle_left = (clamp(x1), clamp(y1))
            self.pupil_angle_right = (clamp(x2), clamp(y2))
    
    def get_gaze(self) -> tuple:
        """Get current gaze angles for both eyes.
        
        Returns:
            Tuple of (left_x, left_y, right_x, right_y)
        """
        return (self.left_gaze_x, self.left_gaze_y, self.right_gaze_x, self.right_gaze_y)
    
    def update(self):
        # Handle blink animation
        if self.is_blinking:
            self.blink_progress += self.blink_speed
            if self.blink_progress >= 1.0:
                self.is_blinking = False
                self.blink_progress = 0.0
                # Restore original expression after blink
                self.current_expression = self.pre_blink_expression
        
        # Handle wink animation
        if self.is_winking:
            self.wink_progress += self.wink_speed
            
            # Closing phase (0.0 to 0.5)
            # Hold closed (0.5 to 0.55)
            # Opening phase (0.55 to 1.0)
            
            if self.wink_progress < 0.5:
                scale = 1.0 - (self.wink_progress * 2)
            elif self.wink_progress < 0.55:
                scale = 0.0  # Hold closed
            else:
                scale = (self.wink_progress - 0.55) / 0.45
            
            if self.winking_eye == 'left':
                self.left_eye_scale = scale
                self.right_eye_scale = 1.0
            else:
                self.right_eye_scale = scale
                self.left_eye_scale = 1.0
            
            if self.wink_progress >= 1.0:
                self.is_winking = False
                self.winking_eye = None
                self.left_eye_scale = 1.0
                self.right_eye_scale = 1.0
        
        # Handle rolling eyes animation (pauses during blink or wink)
        if self.is_rolling and not (self.is_blinking or self.is_winking):
            delta_time = 1.0 / 60.0  # Assume 60 FPS
            self.rolling_progress += delta_time / self.rolling_duration
            if self.rolling_progress >= 1.0:
                # Complete: return to exact starting angle
                self.pupil_angle = self.rolling_start_angle
                self.rolling_progress = 0.0
                self.is_rolling = False
                self.rolling_start_angle = None
                # Restore gaze state
                self.pupil_angle_left = self.pre_rolling_gaze_left
                self.pupil_angle_right = self.pre_rolling_gaze_right
            else:
                # Rotate 360° from starting position
                direction_multiplier = 1 if self.rolling_direction == 'clockwise' else -1
                self.pupil_angle = (self.rolling_start_angle + self.rolling_progress * 360 * direction_multiplier) % 360
        elif self.is_blinking or self.is_winking:
            # Rolling animation paused during blink or wink
            pass
        
        # Handle expression transitions
        if self.transition_progress < 1.0:
            self.transition_progress += self.transition_speed
            if self.transition_progress >= 1.0:
                self.current_expression = self.target_expression
                self.transition_progress = 1.0
    
    def run(self):
        pygame.init()
        
        # Get monitor information
        monitors = pygame.display.get_desktop_sizes()
        print(f"Available monitors: {len(monitors)}")
        for i, monitor_size in enumerate(monitors):
            print(f"  Monitor {i}: {monitor_size[0]}x{monitor_size[1]}")
        
        if self.monitor >= len(monitors):
            print(f"Error: Monitor {self.monitor} not found. Using monitor 0.")
            self.monitor = 0
        
        # Get monitor info and position
        monitor_size = monitors[self.monitor]
        
        if self.fullscreen:
            self.width, self.height = monitor_size
            
            # Calculate monitor position based on index
            monitor_x = 0
            for i in range(self.monitor):
                monitor_x += monitors[i][0]
            
            # Set position for fullscreen
            import os
            os.environ['SDL_VIDEO_WINDOW_POS'] = f'{monitor_x},0'
            
            # Create fullscreen window
            screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
            print(f"Running FULLSCREEN on monitor {self.monitor} - {self.width}x{self.height}")
        else:
            # Windowed mode - use default size or smaller if monitor is smaller
            self.width = min(self.width, monitor_size[0])
            self.height = min(self.height, monitor_size[1])
            
            # Calculate position to center window on selected monitor
            monitor_x = 0
            for i in range(self.monitor):
                monitor_x += monitors[i][0]
            
            window_x = monitor_x + (monitor_size[0] - self.width) // 2
            window_y = (monitor_size[1] - self.height) // 2
            
            import os
            os.environ['SDL_VIDEO_WINDOW_POS'] = f'{window_x},{window_y}'
            
            # Create windowed window
            screen = pygame.display.set_mode((self.width, self.height))
            print(f"Running WINDOWED on monitor {self.monitor} - {self.width}x{self.height}")
        
        pygame.display.set_caption("Mr. Pumpkin")
        
        # Start network server
        server_thread = threading.Thread(target=self._run_socket_server, daemon=True)
        server_thread.start()
        
        print("Press ESC to exit or send socket commands to port 5000")
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    self._handle_keyboard_input(event.key)
            
            self.update()
            self.draw(screen)
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
    
    def _handle_keyboard_input(self, key):
        mapping = {
            pygame.K_1: Expression.NEUTRAL,
            pygame.K_2: Expression.HAPPY,
            pygame.K_3: Expression.SAD,
            pygame.K_4: Expression.ANGRY,
            pygame.K_5: Expression.SURPRISED,
            pygame.K_6: Expression.SCARED,
            pygame.K_7: Expression.SLEEPING,
        }
        if key in mapping:
            self.set_expression(mapping[key])
        elif key == pygame.K_b:
            self.blink()
        elif key == pygame.K_l:
            self.wink_left()
        elif key == pygame.K_r:
            self.wink_right()
        elif key == pygame.K_c:
            self.roll_clockwise()
        elif key == pygame.K_x:
            self.roll_counterclockwise()
        elif key == pygame.K_u:
            self.raise_eyebrows()
        elif key == pygame.K_j:
            self.lower_eyebrows()
        elif key == pygame.K_LEFTBRACKET:
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_SHIFT:
                self.lower_eyebrow_left()
            else:
                self.raise_eyebrow_left()
        elif key == pygame.K_RIGHTBRACKET:
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_SHIFT:
                self.lower_eyebrow_right()
            else:
                self.raise_eyebrow_right()
    
    def _run_socket_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', 5000))
        server_socket.listen(1)
        print("Socket server listening on port 5000")
        
        try:
            while self.running:
                try:
                    client_socket, addr = server_socket.accept()
                    print(f"Connected by {addr}")
                    
                    while True:
                        data = client_socket.recv(1024).decode('utf-8').strip().lower()
                        if not data:
                            break
                        
                        # Handle blink command
                        if data == "blink":
                            self.blink()
                            print("Blink animation triggered")
                            continue
                        
                        # Handle wink commands
                        if data == "wink_left":
                            self.wink_left()
                            print("Left wink animation triggered")
                            continue
                        elif data == "wink_right":
                            self.wink_right()
                            print("Right wink animation triggered")
                            continue
                        
                        # Handle rolling eyes commands
                        if data == "roll_clockwise":
                            self.roll_clockwise()
                            print("Rolling eyes clockwise")
                            continue
                        
                        if data == "roll_counterclockwise":
                            self.roll_counterclockwise()
                            print("Rolling eyes counter-clockwise")
                            continue
                        
                        # Handle gaze command
                        if data.startswith("gaze "):
                            try:
                                parts = data.split()
                                args = [float(x) for x in parts[1:]]
                                
                                if len(args) == 2:
                                    # Two args: apply same angles to both eyes
                                    self.set_gaze(args[0], args[1])
                                    print(f"Gaze set to: both eyes ({args[0]}°, {args[1]}°)")
                                elif len(args) == 4:
                                    # Four args: independent eye control
                                    self.set_gaze(args[0], args[1], args[2], args[3])
                                    print(f"Gaze set to: left ({args[0]}°, {args[1]}°), right ({args[2]}°, {args[3]}°)")
                                else:
                                    print(f"Error: gaze command requires 2 or 4 numeric arguments, got {len(args)}")
                            except (ValueError, IndexError) as e:
                                print(f"Error parsing gaze command: {e}")
                            continue
                        
                        # Handle eyebrow commands
                        if data == "eyebrow_raise":
                            self.raise_eyebrows()
                            print("Eyebrows raised")
                            continue
                        
                        if data == "eyebrow_lower":
                            self.lower_eyebrows()
                            print("Eyebrows lowered")
                            continue
                        
                        if data == "eyebrow_raise_left":
                            self.raise_eyebrow_left()
                            print("Left eyebrow raised")
                            continue
                        
                        if data == "eyebrow_lower_left":
                            self.lower_eyebrow_left()
                            print("Left eyebrow lowered")
                            continue
                        
                        if data == "eyebrow_raise_right":
                            self.raise_eyebrow_right()
                            print("Right eyebrow raised")
                            continue
                        
                        if data == "eyebrow_lower_right":
                            self.lower_eyebrow_right()
                            print("Right eyebrow lowered")
                            continue
                        
                        if data == "eyebrow_reset":
                            self.reset_eyebrows()
                            print("Eyebrows reset to neutral")
                            continue
                        
                        if data.startswith("eyebrow "):
                            try:
                                parts = data.split()
                                val = float(parts[1])
                                self.set_eyebrow(val)
                                print(f"Both eyebrows set to: {val}")
                            except (ValueError, IndexError) as e:
                                print(f"Error parsing eyebrow command: {e}")
                            continue
                        
                        if data.startswith("eyebrow_left "):
                            try:
                                parts = data.split()
                                val = float(parts[1])
                                self.set_eyebrow(val, self.eyebrow_right_offset)
                                print(f"Left eyebrow set to: {val}")
                            except (ValueError, IndexError) as e:
                                print(f"Error parsing eyebrow_left command: {e}")
                            continue
                        
                        if data.startswith("eyebrow_right "):
                            try:
                                parts = data.split()
                                val = float(parts[1])
                                self.set_eyebrow(self.eyebrow_left_offset, val)
                                print(f"Right eyebrow set to: {val}")
                            except (ValueError, IndexError) as e:
                                print(f"Error parsing eyebrow_right command: {e}")
                            continue
                        
                        try:
                            expression = Expression(data)
                            self.set_expression(expression)
                            print(f"Expression changed to: {data}")
                        except ValueError:
                            print(f"Unknown expression: {data}")
                    
                    client_socket.close()
                except Exception as e:
                    print(f"Connection error: {e}")
        finally:
            server_socket.close()

if __name__ == "__main__":
    monitor = 0
    fullscreen = True
    
    # Parse command-line arguments
    for arg in sys.argv[1:]:
        if arg == '--window':
            fullscreen = False
        elif arg == '--fullscreen':
            fullscreen = True
        else:
            try:
                monitor = int(arg)
            except ValueError:
                print(f"Usage: python pumpkin_face.py [monitor_number] [--window|--fullscreen]")
                print(f"")
                print(f"Examples:")
                print(f"  python pumpkin_face.py              # Fullscreen on monitor 0 (default)")
                print(f"  python pumpkin_face.py 0            # Fullscreen on monitor 0")
                print(f"  python pumpkin_face.py 1            # Fullscreen on monitor 1")
                print(f"  python pumpkin_face.py --window     # Windowed on monitor 0")
                print(f"  python pumpkin_face.py 1 --window   # Windowed on monitor 1")
                sys.exit(1)
    
    pumpkin = PumpkinFace(monitor=monitor, fullscreen=fullscreen)
    pumpkin.run()
