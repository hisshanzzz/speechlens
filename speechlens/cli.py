"""Command-line interface for SpeechLens.

Usage examples:
    python -m speechlens samples/icebreaker.txt
    python -m speechlens samples/icebreaker.txt --target 4-6
    python -m speechlens speech.txt --wpm 140 --json report.json
"""

import argparse
import json
import os
import sys

from .analyzer import DEFAULT_WPM, analyze
from .report import build_report


def parse_target(value):
    """Parse a target window like '5-7' into (5.0, 7.0)."""
    try:
        low, high = value.split("-")
        target_min, target_max = float(low), float(high)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "target must look like '5-7' (minutes)"
        )
    if target_min <= 0 or target_max <= target_min:
        raise argparse.ArgumentTypeError(
            "target window must be positive and increasing, e.g. '5-7'"
        )
    return target_min, target_max


def build_parser():
    parser = argparse.ArgumentParser(
        prog="speechlens",
        description=(
            "Analyze a speech script or transcript: estimated delivery "
            "time, filler words, vocabulary richness, and readability."
        ),
    )
    parser.add_argument(
        "path",
        help="path to a .txt file containing the speech",
    )
    parser.add_argument(
        "--wpm",
        type=int,
        default=DEFAULT_WPM,
        help="your speaking pace in words per minute (default: %(default)s)",
    )
    parser.add_argument(
        "--target",
        type=parse_target,
        default=(5.0, 7.0),
        metavar="MIN-MAX",
        help=(
            "target time window in minutes, e.g. 4-6 for a Toastmasters "
            "Ice Breaker (default: 5-7)"
        ),
    )
    parser.add_argument(
        "--json",
        metavar="FILE",
        help="also save the raw metrics as JSON to this file",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not os.path.isfile(args.path):
        parser.error("file not found: " + args.path)

    with open(args.path, "r", encoding="utf-8") as handle:
        text = handle.read()

    if not text.strip():
        parser.error("the file is empty: " + args.path)

    results = analyze(text, wpm=args.wpm)
    target_min, target_max = args.target

    title = os.path.basename(args.path)
    print(build_report(results, title, target_min, target_max))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(results, handle, indent=2)
        print("\nSaved raw metrics to " + args.json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
