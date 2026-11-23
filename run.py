"""Launch the Streamlit application from the project root."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
APP_PATH = PROJECT_ROOT / "frontend" / "app.py"


def main() -> int:
    """Run Streamlit and return its exit status."""
    if not APP_PATH.is_file():
        print(f"Streamlit entry point was not found: {APP_PATH}", file=sys.stderr)
        return 1
    if importlib.util.find_spec("streamlit") is None:
        print(
            "Streamlit is not installed. Run 'python -m pip install -r requirements.txt'.",
            file=sys.stderr,
        )
        return 1

    try:
        return subprocess.call(
            [sys.executable, "-m", "streamlit", "run", str(APP_PATH)],
            cwd=PROJECT_ROOT,
        )
    except OSError as exc:
        print(f"Unable to launch Streamlit: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
