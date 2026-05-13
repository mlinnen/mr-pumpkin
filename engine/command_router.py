"""
engine/command_router.py
Vi backend CommandRouter adapter stub for squad/99-vi-engine
"""
from typing import Any, Dict

class CommandRouter:
    """Protocol-agnostic command router stub.
    Will be populated by porting parsing logic from command_handler.py.
    """
    def __init__(self, pumpkin_face):
        self.pumpkin = pumpkin_face

    def execute(self, command_str: str, mode: str = "text") -> Any:
        """Execute a command string and return protocol-appropriate response.
        mode: 'text' returns plain OK/ERROR strings; 'json' returns dicts.
        """
        # TODO: Implement parsing and dispatch
        if mode == "json":
            return {"status": "error", "message": "Not implemented"}
        return "ERROR Not implemented"
