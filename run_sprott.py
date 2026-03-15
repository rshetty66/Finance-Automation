#!/usr/bin/env python3
"""
Sprott Finance Transformation — CLI entry point.

Usage:
    python run_sprott.py                          # demo with bundled sample files
    python run_sprott.py --input file1.xlsx       # single file
    python run_sprott.py --input a.xlsx b.pdf     # multiple files
    python run_sprott.py --input file.xlsx --out my_report.html
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def demo_files() -> list[str]:
    """Return bundled sample files for the demo."""
    candidates = [
        "PCC_Integrated_Diagnostic_JE_FAA_Rec_Correlation.xlsx",
        "FAA_Activity_Analysis (2).pdf",
    ]
    found = []
    for name in candidates:
        p = ROOT / name
        if p.exists():
            found.append(str(p))
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Sprott consulting deliverable from input files")
    parser.add_argument("--input", nargs="+", metavar="FILE", help="Input files (Excel, PDF, CSV)")
    parser.add_argument("--out", default="sprott_roadmap.html", metavar="FILE", help="Output HTML path")
    parser.add_argument("--no-open", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()

    # Resolve input files
    input_files = args.input or demo_files()
    if not input_files:
        print("ERROR: No input files found. Pass --input <file(s)> or place sample files in project root.")
        sys.exit(1)

    # Validate files exist
    for f in input_files:
        if not Path(f).exists():
            print(f"ERROR: File not found: {f}")
            sys.exit(1)

    # Run engagement
    from sprott.engagement import run_sprott_engagement
    html_path = run_sprott_engagement(input_files, output_path=args.out, verbose=True)

    # Open in browser
    if not args.no_open:
        print(f"\nOpening in browser: {html_path}")
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", html_path])
            elif sys.platform.startswith("linux"):
                subprocess.run(["xdg-open", html_path], stderr=subprocess.DEVNULL)
            else:
                os.startfile(html_path)
        except Exception:
            pass  # Browser open is best-effort

    print(f"\n{'='*60}")
    print(f"  DONE — open this file in your browser:")
    print(f"  {html_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
