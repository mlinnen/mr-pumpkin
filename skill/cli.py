"""
Mr. Pumpkin Recording Skill — Command-line interface.

Translates a natural language prompt into a timeline animation and uploads
it to the Mr. Pumpkin server.

Usage:
    python -m skill.cli "make the pumpkin look surprised then blink" --filename my_show
    python -m skill.cli "wave hello" -f wave --host 192.168.1.10 --protocol ws

Exit codes:
    0 — success
    1 — generation or upload error
    2 — argument error
"""

import argparse
import json
import sys


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mr-pumpkin-record",
        description="Generate a Mr. Pumpkin timeline from a natural language prompt and upload it.",
    )
    p.add_argument("prompt", help="Natural language description of the animation.")
    p.add_argument(
        "-f", "--filename",
        required=True,
        help="Name to store the timeline as on the server (no .json extension).",
    )
    p.add_argument("--host", default="localhost", help="Mr. Pumpkin server hostname (default: localhost).")
    p.add_argument("--tcp-port", type=int, default=5000, help="TCP port (default: 5000).")
    p.add_argument("--ws-port", type=int, default=5001, help="WebSocket port (default: 5001).")
    p.add_argument(
        "--protocol", choices=["tcp", "ws"], default="tcp",
        help="Upload protocol: tcp (default) or ws (WebSocket).",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Generate the timeline and print it without uploading.",
    )
    p.add_argument(
        "--provider", default="gemini",
        help="LLM provider to use (default: gemini).",
    )
    return p


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Resolve LLM provider
    try:
        from skill.generator import generate_timeline, GeminiProvider
        if args.provider.lower() == "gemini":
            provider = GeminiProvider()
        else:
            print(f"ERROR: Unknown provider '{args.provider}'. Supported: gemini", file=sys.stderr)
            return 2
    except ImportError as exc:
        print(f"ERROR: Could not import skill package: {exc}", file=sys.stderr)
        return 1
    except (EnvironmentError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Generate timeline
    print(f"Generating timeline for: {args.prompt!r}")
    try:
        timeline = generate_timeline(args.prompt, provider=provider)
    except ValueError as exc:
        print(f"ERROR: Generation failed — {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Unexpected error during generation — {exc}", file=sys.stderr)
        return 1

    # Print generated timeline for user confirmation
    print("\nGenerated timeline:")
    print(json.dumps(timeline, indent=2))

    if args.dry_run:
        print("\n(Dry run — not uploading.)")
        return 0

    # Upload
    from skill.uploader import upload_timeline
    print(f"\nUploading '{args.filename}' to {args.host} via {args.protocol.upper()}...")
    try:
        upload_timeline(
            filename=args.filename,
            timeline_dict=timeline,
            host=args.host,
            tcp_port=args.tcp_port,
            ws_port=args.ws_port,
            protocol=args.protocol,
        )
    except ValueError as exc:
        print(f"ERROR: Upload failed — {exc}", file=sys.stderr)
        return 1
    except ConnectionError as exc:
        print(f"ERROR: Connection failed — {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Unexpected error during upload — {exc}", file=sys.stderr)
        return 1

    print(f"✓ Timeline '{args.filename}' uploaded successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
