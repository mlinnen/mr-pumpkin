---
layout: page
title: Contributing
permalink: /contributing
description: How to contribute to Mr. Pumpkin — pull requests, issues, and guidelines.
---

# Contributing

Mr. Pumpkin is an open-source project and contributions are welcome!

## Getting Started

1. **Fork** the repository on [GitHub](https://github.com/mlinnen/mr-pumpkin)
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/mr-pumpkin.git
   cd mr-pumpkin
   ```
3. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```
4. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

## Development Workflow

### Run the tests

```bash
pytest                                          # All 430+ tests
pytest tests/test_projection_mapping.py -v      # Specific file
pytest -vv                                      # Verbose output
```

All tests must pass before submitting a PR. If you're adding a new feature, please add corresponding tests.

### Code standards

- Python 3.x, no external dependencies beyond what's in `requirements.txt`
- Projection-first rendering: pure black `(0,0,0)` background, pure white `(255,255,255)` features
- Minimum 15:1 contrast ratio (21:1 preferred) for all visual elements
- No branching `if projection_mode` — projection is the baseline

## Submitting a Pull Request

1. Make sure all tests pass: `pytest`
2. Write a clear commit message:
   ```
   feat: add wink_nose animation command (#42)
   ```
3. Push your branch and open a PR against `dev`
4. Describe what you changed and why in the PR body

## Open Issues

Browse [open issues](https://github.com/mlinnen/mr-pumpkin/issues) to find something to work on. Issues labelled `good first issue` are great starting points.

- [Open Issues](https://github.com/mlinnen/mr-pumpkin/issues)
- [Discussions](https://github.com/mlinnen/mr-pumpkin/discussions)

## Architecture Notes

The project has a clear team architecture:

- **`pumpkin_face.py`** — Main application: rendering, state machine, socket servers
- **`command_handler.py`** — Shared CommandRouter used by both TCP and WebSocket
- **`timeline.py`** — Timeline playback engine (record, play, pause, seek)
- **`skill/`** — AI recording skill (LLM provider abstraction, CLI, uploader)
- **`tests/`** — Full test suite (pytest)

New expressions follow the pattern in `pumpkin_face.py`'s `Expression` enum. New commands are added to `command_handler.py`'s `CommandRouter` and must be covered by tests.

## Code of Conduct

Please be respectful and constructive. This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.

## License

This project is released under the [MIT License]({{ '/license' | relative_url }}).
