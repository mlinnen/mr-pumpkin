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
        
        # Colors
        self.PUMPKIN_COLOR = (255, 140, 0)
        self.EYE_COLOR = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.DARK_BROWN = (101, 67, 33)
        
    def draw(self, surface: pygame.Surface):
        surface.fill((240, 240, 240))
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Draw pumpkin body (circle)
        pumpkin_radius = 300
        pygame.draw.circle(surface, self.PUMPKIN_COLOR, (center_x, center_y), pumpkin_radius)
        
        # Draw pumpkin ridges
        ridge_count = 8
        for i in range(ridge_count):
            angle = (i / ridge_count) * 2 * math.pi
            ridge_x = int(center_x + pumpkin_radius * 0.9 * math.cos(angle))
            ridge_y = int(center_y + pumpkin_radius * 0.9 * math.sin(angle))
            pygame.draw.circle(surface, self.DARK_BROWN, (ridge_x, ridge_y), 20, 2)
        
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
        
        # Left eye
        pygame.draw.circle(surface, self.EYE_COLOR, left_pos, eye_radius)
        pygame.draw.circle(surface, self.WHITE, left_pos, eye_radius, 3)
        
        # Right eye
        pygame.draw.circle(surface, self.EYE_COLOR, right_pos, eye_radius)
        pygame.draw.circle(surface, self.WHITE, right_pos, eye_radius, 3)
        
        # Draw pupils
        pupil_radius = 15
        pygame.draw.circle(surface, self.WHITE, (left_pos[0] - 10, left_pos[1] - 10), pupil_radius)
        pygame.draw.circle(surface, self.WHITE, (right_pos[0] - 10, right_pos[1] - 10), pupil_radius)
    
    def _draw_mouth(self, surface: pygame.Surface, points: list):
        if not points or len(points) < 2:
            if self.current_expression == Expression.SURPRISED:
                # O-shaped mouth
                pygame.draw.circle(surface, self.EYE_COLOR, (self.width // 2, self.height // 2 + 80), 30)
            elif self.current_expression == Expression.SCARED:
                # Scared mouth
                pygame.draw.ellipse(surface, self.EYE_COLOR, 
                                   (self.width // 2 - 40, self.height // 2 + 70, 80, 50))
            return
        
        # Draw lines between consecutive points
        for i in range(len(points) - 1):
            p1 = (int(points[i][0]), int(points[i][1]))
            p2 = (int(points[i+1][0]), int(points[i+1][1]))
            pygame.draw.line(surface, self.DARK_BROWN, p1, p2, 4)
    
    def set_expression(self, expression: Expression):
        if expression != self.current_expression:
            self.target_expression = expression
            self.transition_progress = 0.0
    
    def update(self):
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
        }
        if key in mapping:
            self.set_expression(mapping[key])
    
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
