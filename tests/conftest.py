import sys
import os
import pytest

# Add parent directory to Python path so tests can import pumpkin_face module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
