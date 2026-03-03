# Recording Skill

The Mr. Pumpkin recording skill lets you describe an animation in plain English and have it automatically generated and uploaded to your pumpkin server.

## How it works

1. You describe the animation you want (e.g. "make the pumpkin look surprised then blink twice")
2. The skill sends your description to an LLM (Google Gemini by default)
3. The LLM generates a timeline JSON file following the [timeline schema](timeline-schema.md)
4. The generated timeline is validated locally before upload
5. The timeline is uploaded to the Mr. Pumpkin server and stored as a recording

## Prerequisites

1. **Python 3.10+** — the skill uses the `match` statement via `Union` type syntax

2. **Gemini API key** — set the environment variable:
   ```
   set GEMINI_API_KEY=your-api-key-here       # Windows
   export GEMINI_API_KEY=your-api-key-here    # macOS/Linux
   ```
   Get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey).

3. **Install skill dependencies** from the `skill/` folder:
   ```
   pip install -r skill/requirements.txt
   ```

## Quick start

```bash
python -m skill.cli "make the pumpkin look surprised then blink" --filename my_animation
```

This generates a timeline, prints it for your review, then uploads it to `localhost:5000` via TCP.

## Usage

```
python -m skill.cli <prompt> --filename <name> [options]
```

### Required arguments

| Argument | Description |
|----------|-------------|
| `prompt` | Natural language description of the animation |
| `-f`, `--filename` | Name to store the timeline as on the server (no `.json` extension) |

### Optional arguments

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `localhost` | Mr. Pumpkin server hostname or IP |
| `--tcp-port` | `5000` | TCP server port |
| `--ws-port` | `5001` | WebSocket server port |
| `--protocol` | `tcp` | Upload protocol: `tcp` or `ws` |
| `--dry-run` | off | Generate and print the timeline without uploading |
| `--provider` | `gemini` | LLM provider (currently only `gemini`) |

## Examples

**Simple blink animation:**
```bash
python -m skill.cli "blink twice slowly" --filename slow_blink
```

**Emotional sequence:**
```bash
python -m skill.cli "look surprised, then happy, then wink" --filename surprise_wink
```

**Preview before uploading:**
```bash
python -m skill.cli "sleepy pumpkin nodding off" --filename sleepy --dry-run
```

**Upload to a remote server via WebSocket:**
```bash
python -m skill.cli "happy greeting" --filename hello --host 192.168.1.10 --protocol ws
```

## Error handling

| Error | Cause | Fix |
|-------|-------|-----|
| `No Gemini API key found` | `GEMINI_API_KEY` not set | Set the environment variable |
| `Generation failed` | LLM produced invalid JSON or unknown commands | Rephrase the prompt and try again |
| `Upload failed — ERROR: already exists` | A file with that name already exists on the server | Choose a different `--filename` |
| `Connection failed` | Server not reachable | Verify the server is running and the host/port are correct |

## Using the API directly

You can also use the skill programmatically:

```python
from skill import generate_timeline, upload_timeline

# Generate a timeline dict
timeline = generate_timeline("make the pumpkin look confused")

# Upload it
upload_timeline("confused_pumpkin", timeline, host="localhost")
```

### Custom LLM provider

The skill is designed to be provider-agnostic. You can swap in any LLM by implementing the `LLMProvider` interface:

```python
from skill.generator import LLMProvider, generate_timeline

class MyLocalModel(LLMProvider):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Call your local model here
        return my_model.chat(system=system_prompt, user=user_prompt)

timeline = generate_timeline("wave hello", provider=MyLocalModel())
```

## Recording Chaining

You can embed one recording inside another by using the `play_recording` command in a timeline. When the playback engine reaches a `play_recording` command, it pauses the parent timeline, plays the named sub-recording in full, and then resumes the parent from the next command.

This lets you build reusable animation building-blocks (a slow blink, an excited wiggle) and compose them into larger sequences without duplicating content.

### The LLM generator already knows this

The recording skill's LLM generator has `play_recording` in its command vocabulary. You can describe chained animations in plain English:

```bash
python -m skill.cli "do our standard greeting animation, then look surprised and do the excitement wiggle" \
  --filename composed_greeting
```

The LLM may choose to reference existing recordings by name using `play_recording` if you describe them in the prompt. If you want to guarantee chaining, name the sub-recordings explicitly:

```bash
python -m skill.cli "play 'slow_blink' then 'excited_wiggle' with a happy expression in between" \
  --filename happy_sequence
```

### Depth limit

Recordings can be nested up to **5 levels** deep. If a `play_recording` command is reached at the maximum depth, it is skipped (an error is logged) and the parent continues playing. Circular references (A → B → A) are prevented by this limit.

---

## Playing back a recording

After uploading, play the recording using the `play_timeline` command:

```
play_timeline my_animation
```

See [Building a Client](building-a-client.md) for the full command reference.
