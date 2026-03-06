"""
Mr. Pumpkin Audio Lip-Sync Recording Tool — Command-line interface.

Two-pass audio-to-animation pipeline:
  1. Gemini multimodal audio analysis → structured timing data
  2. LLM choreography generation → timeline JSON

Usage:
    python -m skill.lipsync_cli audio.mp3 --filename my_song
    python -m skill.lipsync_cli speech.wav -f story --prompt "pumpkin tells this with joy"
    python -m skill.lipsync_cli song.ogg -f dance --dry-run

Exit codes:
    0 — success
    1 — generation, analysis, or upload error
    2 — argument error
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from skill.audio_analyzer import get_provider as get_audio_provider, AudioAnalysis
from skill.generator import generate_timeline, GeminiProvider
from skill.uploader import upload_timeline, upload_audio

logger = logging.getLogger(__name__)


def build_lipsync_prompt(analysis: AudioAnalysis, user_prompt: str) -> str:
    """Build an enriched prompt for timeline generation from audio analysis.

    Combines audio timing data (words, beats, pauses) with user's artistic
    guidance to create a detailed choreography prompt for the LLM.

    Args:
        analysis: Structured audio analysis from AudioAnalysisProvider.
        user_prompt: Optional user guidance for artistic direction.

    Returns:
        Enriched prompt string ready for generate_timeline().
    """
    duration_sec = analysis.duration_ms / 1000.0
    
    # Start with preamble
    lines = [
        f"Create a lip-syncing animation for Mr. Pumpkin for a {duration_sec:.1f}-second audio clip."
    ]
    
    if user_prompt:
        lines.append(f"Artistic direction: {user_prompt}")
    
    lines.append(f"Overall emotion: {analysis.emotion}")
    lines.append("")
    
    # Word timing section (speech segments)
    if analysis.speech_segments:
        lines.append("AUDIO TIMING (word-by-word):")
        for seg in analysis.speech_segments:
            phoneme_hint = _phoneme_to_viseme_hint(seg.phoneme_group)
            lines.append(f"  - {seg.start_ms}ms-{seg.end_ms}ms: \"{seg.word}\" [{seg.phoneme_group} → {phoneme_hint}]")
        lines.append("")
    
    # Beat events section
    if analysis.beats:
        lines.append("BEATS:")
        for beat in analysis.beats:
            reaction = "eyebrow_raise + reset" if beat.strength in ("strong", "bar1") else "subtle reaction"
            if beat.strength == "bar1":
                reaction = "eyebrow_raise + turn_up 30 + center_head"
            lines.append(f"  - {beat.time_ms}ms: {beat.strength} beat → {reaction}")
        lines.append("")
    
    # Pause segments (for blink insertion)
    if analysis.pauses:
        lines.append("PAUSES (≥400ms → blink):")
        for pause in analysis.pauses:
            blink_note = "→ blink" if pause.duration_ms >= 400 else "(no blink, too short)"
            lines.append(f"  - {pause.start_ms}ms-{pause.end_ms}ms: {pause.duration_ms}ms pause {blink_note}")
        lines.append("")
    
    # Viseme mapping rules
    lines.append("VISEME MAPPING RULES:")
    lines.append("  - bilabial (M/B/P sounds): use 'mouth closed' viseme")
    lines.append("  - open_vowel (AH/AA): use 'mouth open' viseme")
    lines.append("  - spread_vowel (EE/IH): use 'mouth wide' viseme")
    lines.append("  - round_vowel (OO/OH): use 'mouth rounded' viseme")
    lines.append("  - neutral: use 'mouth neutral' or 'mouth closed'")
    lines.append("")
    
    # Generation instructions
    lines.append("Generate a complete timeline JSON that:")
    lines.append("  1. Drives mouth visemes precisely to the word timings above")
    lines.append("  2. Adds eyebrow reactions to beats (raise at beat time, reset 200ms later)")
    lines.append("  3. Adds blinks during pauses ≥400ms")
    lines.append("  4. Adds natural gaze shifts at sentence boundaries or between long phrases")
    lines.append(f"  5. Sets expression to match the overall emotion ({analysis.emotion} → set_expression {analysis.emotion})")
    lines.append("  6. Includes natural head movements for liveliness (subtle turns, return to center)")
    lines.append("")
    lines.append("Make Mr. Pumpkin look engaged, alive, and synchronized to the audio.")
    
    return "\n".join(lines)


def _phoneme_to_viseme_hint(phoneme_group: str) -> str:
    """Map phoneme group to viseme command hint."""
    mapping = {
        "bilabial": "mouth closed",
        "open_vowel": "mouth open",
        "spread_vowel": "mouth wide",
        "round_vowel": "mouth rounded",
        "neutral": "mouth neutral",
    }
    return mapping.get(phoneme_group, "mouth neutral")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mr-pumpkin-lipsync",
        description="Generate a lip-synced Mr. Pumpkin recording from an audio file.",
    )
    p.add_argument("audio_file", help="Path to audio file (.mp3, .wav, .ogg, etc.).")
    p.add_argument(
        "-f", "--filename",
        help="Name to store recording as on server (default: audio file stem, e.g., 'my_song').",
    )
    p.add_argument(
        "--prompt",
        default="",
        help="Optional artistic guidance (e.g., 'pumpkin sings this joyfully').",
    )
    p.add_argument("--host", default="localhost", help="Mr. Pumpkin server hostname (default: localhost).")
    p.add_argument("--tcp-port", type=int, default=5000, help="TCP port (default: 5000).")
    p.add_argument("--ws-port", type=int, default=5001, help="WebSocket port (default: 5001).")
    p.add_argument(
        "--protocol", choices=["tcp", "ws"], default="tcp",
        help="Upload protocol: tcp (default) or ws (WebSocket).",
    )
    p.add_argument(
        "--audio-provider", default="gemini",
        help="Audio analysis provider (default: gemini).",
    )
    p.add_argument(
        "--provider", default="gemini",
        help="LLM provider for timeline generation (default: gemini).",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Analyze and generate timeline, print JSON, but do NOT upload.",
    )
    return p


def main(argv=None) -> int:
    """Main entry point for lipsync CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    
    # Validate audio file
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"ERROR: Audio file not found: {audio_path}", file=sys.stderr)
        return 1

    _PLAYBACK_UNSUPPORTED = {".m4a", ".aac", ".flac"}
    if audio_path.suffix.lower() in _PLAYBACK_UNSUPPORTED:
        print(
            f"WARNING: {audio_path.suffix} files cannot be played back by Mr. Pumpkin "
            f"(pygame does not support this format).\n"
            f"  Please convert to .mp3 or .wav first, e.g.:\n"
            f"    ffmpeg -i {audio_path.name} {audio_path.stem}.mp3",
            file=sys.stderr,
        )
    
    # Determine filename
    filename = args.filename or audio_path.stem
    audio_filename = f"{filename}{audio_path.suffix}"
    
    # Pass 1: Audio analysis
    print(f"Analyzing audio: {audio_path.name}...")
    try:
        audio_provider = get_audio_provider(args.audio_provider)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (EnvironmentError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    
    try:
        analysis = audio_provider.analyze_audio(str(audio_path), prompt=args.prompt)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Audio analysis failed — {exc}", file=sys.stderr)
        return 1
    
    print(f"  Duration: {analysis.duration_ms}ms, Emotion: {analysis.emotion}")
    print(f"  Words: {len(analysis.speech_segments)}, Beats: {len(analysis.beats)}, Pauses: {len(analysis.pauses)}")
    
    # Pass 2: Generate timeline
    print("Generating choreography...")
    
    try:
        if args.provider.lower() == "gemini":
            llm_provider = GeminiProvider()
        else:
            print(f"ERROR: Unknown provider '{args.provider}'. Supported: gemini", file=sys.stderr)
            return 2
    except (EnvironmentError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    
    enriched_prompt = build_lipsync_prompt(analysis, args.prompt)
    
    try:
        timeline_dict = generate_timeline(enriched_prompt, provider=llm_provider)
    except ValueError as exc:
        print(f"ERROR: Timeline generation failed — {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Unexpected error during generation — {exc}", file=sys.stderr)
        return 1
    
    # Inject audio_file metadata
    timeline_dict["audio_file"] = audio_filename
    
    # Print generated timeline
    print("\nGenerated timeline:")
    print(json.dumps(timeline_dict, indent=2))
    
    if args.dry_run:
        print("\n--- Dry run complete (not uploaded) ---")
        return 0
    
    # Upload audio
    print(f"\nUploading audio: {audio_filename}...")
    try:
        audio_bytes = audio_path.read_bytes()
        upload_audio(
            audio_filename,
            audio_bytes,
            host=args.host,
            tcp_port=args.tcp_port,
            ws_port=args.ws_port,
            protocol=args.protocol,
        )
    except (ValueError, ConnectionError) as exc:
        print(f"ERROR: Audio upload failed — {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Unexpected error during audio upload — {exc}", file=sys.stderr)
        return 1
    
    # Upload timeline
    print(f"Uploading timeline: {filename}...")
    try:
        upload_timeline(
            filename,
            timeline_dict,
            host=args.host,
            tcp_port=args.tcp_port,
            ws_port=args.ws_port,
            protocol=args.protocol,
        )
    except (ValueError, ConnectionError) as exc:
        print(f"ERROR: Timeline upload failed — {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Unexpected error during timeline upload — {exc}", file=sys.stderr)
        return 1
    
    print(f"\n✓ Done. Play it with: play_recording {filename}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
