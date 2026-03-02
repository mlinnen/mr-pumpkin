"""
Prompt-to-Timeline generator for Mr. Pumpkin.

Translates natural language animation descriptions into validated timeline JSON
using an LLM backend. Supports pluggable providers; defaults to Gemini.

Usage:
    from skill.generator import generate_timeline
    timeline_dict = generate_timeline("Make the pumpkin look surprised then blink twice")
"""

import json
import os
import re
import sys
from abc import ABC, abstractmethod

# Allow importing timeline.py from the project root when running as a package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from timeline import Timeline  # noqa: E402


_SYSTEM_PROMPT = """\
You are an animation choreographer for Mr. Pumpkin, an animated jack-o'-lantern face.
Your job is to translate natural language descriptions into precise timeline JSON.

## JSON Schema

Respond with ONLY a valid JSON object matching this exact schema — no prose, no markdown fences:

{
  "version": "1.0",
  "duration_ms": <integer — total animation length in ms>,
  "commands": [
    {"time_ms": <integer>, "command": "<name>"},
    {"time_ms": <integer>, "command": "<name>", "args": {<key>: <value>}}
  ]
}

## Constraints

- `version` MUST be the string "1.0"
- `time_ms` values MUST be non-negative integers sorted in ascending order
- `duration_ms` MUST equal the last `time_ms` value plus a natural buffer (200–500 ms)
- All `command` values MUST come from the vocabulary below
- `args` is optional; omit it when the command takes no arguments

## Command Vocabulary

| Command                 | Args                                                     | Notes                                    |
|-------------------------|----------------------------------------------------------|------------------------------------------|
| set_expression          | {"expression": "<name>"}                                 | neutral, happy, sad, angry, surprised, scared, sleeping |
| blink                   | (none)                                                   | Both eyes blink (~300 ms animation)      |
| wink_left               | (none)                                                   | Left eye wink                            |
| wink_right              | (none)                                                   | Right eye wink                           |
| roll_clockwise          | (none)                                                   | Eyes roll clockwise (~1000 ms)           |
| roll_counterclockwise   | (none)                                                   | Eyes roll counter-clockwise (~1000 ms)   |
| gaze                    | {"x": float, "y": float}                                 | Both eyes; -90 to +90 degrees            |
| gaze                    | {"lx": float, "ly": float, "rx": float, "ry": float}     | Independent eye control                  |
| eyebrow_raise           | (none)                                                   | Raise both eyebrows                      |
| eyebrow_lower           | (none)                                                   | Lower both eyebrows                      |
| eyebrow_raise_left      | (none)                                                   | Raise left eyebrow only                  |
| eyebrow_lower_left      | (none)                                                   | Lower left eyebrow only                  |
| eyebrow_raise_right     | (none)                                                   | Raise right eyebrow only                 |
| eyebrow_lower_right     | (none)                                                   | Lower right eyebrow only                 |
| eyebrow_reset           | (none)                                                   | Reset eyebrows to neutral                |
| eyebrow                 | {"value": float}                                         | Both eyebrows to numeric offset          |
| eyebrow                 | {"left": float, "right": float}                          | Independent eyebrow control              |
| turn_left               | {"amount": int}                                          | Head turn left; default 50 px            |
| turn_right              | {"amount": int}                                          | Head turn right; default 50 px           |
| turn_up                 | {"amount": int}                                          | Head tilt up; default 50 px              |
| turn_down               | {"amount": int}                                          | Head tilt down; default 50 px            |
| center_head             | (none)                                                   | Return head to center                    |
| twitch_nose             | {"magnitude": float}                                     | Quick nose twitch; default 50.0          |
| wiggle_nose             | {"magnitude": float}                                     | Nose wiggle; default 50.0                |
| scrunch_nose            | {"magnitude": float}                                     | Nose scrunch; default 50.0               |
| reset_nose              | (none)                                                   | Return nose to neutral                   |
| projection_reset        | (none)                                                   | Reset projection offset                  |
| jog_offset              | {"dx": int, "dy": int}                                   | Nudge projection by dx/dy pixels         |
| set_offset              | {"x": int, "y": int}                                     | Absolute projection offset               |

## Timing Guidelines

- Expression transitions feel natural with 400–600 ms between them
- Blink animations complete in ~300 ms; allow 300+ ms after before the next command
- Eye roll animations take ~1000 ms; allow 1000+ ms after before the next command
- Gaze shifts should allow 200–400 ms for the eyes to settle before the next movement
- Eyebrow changes layer on top of expressions; they can overlap slightly (100–200 ms gap)
- Head turns are slow and deliberate; allow 500+ ms per movement
- A minimal animation should be at least 1000 ms; a comfortable sequence is 3000–8000 ms
- Always start with `set_expression` to establish the base state

## Example 1 — "surprised, then relieved"

{
  "version": "1.0",
  "duration_ms": 5200,
  "commands": [
    {"time_ms": 0,    "command": "set_expression", "args": {"expression": "neutral"}},
    {"time_ms": 400,  "command": "eyebrow_raise"},
    {"time_ms": 500,  "command": "set_expression", "args": {"expression": "surprised"}},
    {"time_ms": 1800, "command": "blink"},
    {"time_ms": 2300, "command": "gaze", "args": {"x": 0.0, "y": 0.0}},
    {"time_ms": 2800, "command": "eyebrow_reset"},
    {"time_ms": 3200, "command": "set_expression", "args": {"expression": "happy"}},
    {"time_ms": 4200, "command": "blink"},
    {"time_ms": 5000, "command": "set_expression", "args": {"expression": "neutral"}}
  ]
}

## Example 2 — "getting sleepy"

{
  "version": "1.0",
  "duration_ms": 6300,
  "commands": [
    {"time_ms": 0,    "command": "set_expression", "args": {"expression": "neutral"}},
    {"time_ms": 800,  "command": "blink"},
    {"time_ms": 1400, "command": "eyebrow_lower"},
    {"time_ms": 2000, "command": "blink"},
    {"time_ms": 2600, "command": "gaze", "args": {"x": 0.0, "y": -15.0}},
    {"time_ms": 3200, "command": "blink"},
    {"time_ms": 4000, "command": "eyebrow_lower"},
    {"time_ms": 4600, "command": "blink"},
    {"time_ms": 5200, "command": "set_expression", "args": {"expression": "sleeping"}},
    {"time_ms": 6000, "command": "set_expression", "args": {"expression": "neutral"}}
  ]
}

Now generate a timeline for the user's animation description. Reply with ONLY the JSON object.
"""

_VALID_COMMANDS = {
    "set_expression", "blink", "wink_left", "wink_right",
    "roll_clockwise", "roll_counterclockwise", "gaze",
    "eyebrow_raise", "eyebrow_lower", "eyebrow_raise_left", "eyebrow_lower_left",
    "eyebrow_raise_right", "eyebrow_lower_right", "eyebrow_reset", "eyebrow",
    "turn_left", "turn_right", "turn_up", "turn_down", "center_head",
    "twitch_nose", "wiggle_nose", "scrunch_nose", "reset_nose",
    "projection_reset", "jog_offset", "set_offset",
}


class LLMProvider(ABC):
    """Abstract base class for LLM backends."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Call the LLM and return its text response.

        Args:
            system_prompt: System-level instructions for the model.
            user_prompt: User request to fulfil.

        Returns:
            Raw text response from the model.
        """


class GeminiProvider(LLMProvider):
    """LLM provider backed by Google Gemini (gemini-1.5-flash).

    API key is read from the ``GEMINI_API_KEY`` environment variable,
    falling back to ``GOOGLE_API_KEY``.

    Raises:
        EnvironmentError: If no API key is found in the environment.
        ImportError: If the ``google-generativeai`` package is not installed.
    """

    MODEL = "gemini-flash-latest"

    def __init__(self):
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ImportError(
                "google-generativeai is required for GeminiProvider. "
                "Install it with: pip install google-generativeai>=0.7.0"
            ) from exc

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "No Gemini API key found. Set the GEMINI_API_KEY environment variable."
            )

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            model_name=self.MODEL,
            system_instruction=_SYSTEM_PROMPT,
        )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response using Gemini.

        The ``system_prompt`` parameter is ignored here because the system
        instruction was embedded at construction time; this signature exists to
        satisfy the ``LLMProvider`` interface.
        """
        response = self._model.generate_content(user_prompt)
        return response.text


def _validate_extra(data: dict) -> None:
    """Apply extra validation rules beyond what Timeline.from_dict() checks.

    Validates:
    - version is exactly "1.0"
    - commands list is non-empty
    - all command names are in the known vocabulary
    - time_ms values are in ascending (non-decreasing) order

    Raises:
        ValueError: With a descriptive message for any failed check.
    """
    version = data.get("version")
    if version != "1.0":
        raise ValueError(f"Invalid timeline version: {version!r}. Expected '1.0'.")

    commands = data.get("commands", [])
    if not commands:
        raise ValueError("Empty commands list — timeline must contain at least one command.")

    prev_time = -1
    for entry in commands:
        name = entry.get("command", "")
        if name not in _VALID_COMMANDS:
            raise ValueError(
                f"Unknown command: {name!r}. Must be one of the recognised vocabulary commands."
            )
        t = entry.get("time_ms", 0)
        if t < prev_time:
            raise ValueError(
                f"Commands must be in ascending time_ms order. "
                f"Found time_ms={t} after previous time_ms={prev_time}."
            )
        prev_time = t



def _repair(data: dict) -> dict:
    """Apply heuristic repairs to LLM-generated timeline dicts.

    Currently handles:
    - Normalises ``timestamp_ms`` → ``time_ms`` in command entries.
    """
    commands = data.get("commands", [])
    repaired = []
    for entry in commands:
        if "timestamp_ms" in entry and "time_ms" not in entry:
            entry = dict(entry)
            entry["time_ms"] = entry.pop("timestamp_ms")
        repaired.append(entry)
    data = dict(data)
    data["commands"] = repaired
    return data


def _extract_json(text: str) -> str:
    """Strip markdown code fences from an LLM response, if present."""
    # Match ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        return match.group(1)
    return text.strip()


def generate_timeline(prompt: str, provider: LLMProvider | None = None) -> dict:
    """Generate a validated timeline dict from a natural language prompt.

    Args:
        prompt: Natural language description of the desired animation.
        provider: LLM provider to use. Defaults to ``GeminiProvider``.

    Returns:
        A validated timeline dict ready for ``Timeline.from_dict()`` or JSON
        serialisation and upload.

    Raises:
        ValueError: If the LLM response cannot be parsed as valid JSON or if
            the resulting structure fails ``Timeline.from_dict()`` validation.
    """
    if provider is None:
        provider = GeminiProvider()

    raw = provider.generate(_SYSTEM_PROMPT, prompt)
    json_text = _extract_json(raw)

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned non-JSON output. JSONDecodeError: {exc}\n\nRaw response:\n{raw}"
        ) from exc

    data = _repair(data)

    _validate_extra(data)

    try:
        Timeline.from_dict(data)
    except Exception as exc:
        raise ValueError(
            f"Generated timeline failed validation: {exc}\n\nTimeline dict:\n{json.dumps(data, indent=2)}"
        ) from exc

    return data
