import sys
import os
import pytest

# Add parent directory to Python path so tests can import pumpkin_face module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ensure headless SDL drivers for CI (set before any pygame import)
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

# Lightweight mock surface used when pygame display is unavailable
class MockSurface:
    def __init__(self, size=(800, 600)):
        self._size = tuple(size)
    def blit(self, src, dest):
        return None
    def fill(self, color):
        return None
    def get_size(self):
        return self._size

# Try to import pygame; tests can still run with the MockSurface when pygame isn't usable
try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception:
    pygame = None
    PYGAME_AVAILABLE = False

@pytest.fixture(scope='session', autouse=True)
def sdl_dummy_env():
    """Ensure environment variables are set for the whole test session."""
    # already set above; keep for explicitness
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
    yield

@pytest.fixture
def pygame_display():
    """Initialize and yield the pygame module (or a lightweight stand-in).

    Use this fixture in tests that need pygame initialization.
    """
    if PYGAME_AVAILABLE:
        pygame.init()
        try:
            pygame.display.init()
        except Exception:
            # Some CI environments/drivers may raise; ignore and continue
            pass
        yield pygame
        try:
            pygame.quit()
        except Exception:
            pass
    else:
        # Provide a minimal stand-in exposing Surface
        class DummyPygame:
            def Surface(self, size):
                return MockSurface(size)
            def init(self):
                return None
            def quit(self):
                return None
            display = type('D', (), {'init': staticmethod(lambda: None), 'set_mode': staticmethod(lambda s: MockSurface(s))})
        yield DummyPygame()

@pytest.fixture
def surface(pygame_display):
    """Return a drawable surface for tests.

    Prefer pygame.Surface when available; otherwise return MockSurface.
    """
    try:
        surf = pygame_display.Surface((800, 600))
        return surf
    except Exception:
        return MockSurface((800, 600))
