#!/usr/bin/env python3
"""Top-level CLI wrapper: forwards the user's query to `src/run.py`.

Usage:
  python run.py "Analyze ROAS drop in last 7 days"

This wrapper forwards the full joined argv to `src/run.py` so the project can be run from the repository root.
"""
import sys
import subprocess

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python run.py \"<analysis query>\"")
        sys.exit(1)

    # Join all args into a single query string (behaviour consistent with existing CLI)
    query = " ".join(sys.argv[1:])

    cmd = [sys.executable, "src/run.py", query]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"run.py: analysis failed with exit code {e.returncode}")
        sys.exit(e.returncode)
