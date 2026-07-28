"""Cross-platform local quality gate for MEW development.

The default workflow mirrors the agreed pre-commit process:
1. apply Ruff's safe automatic fixes,
2. verify the complete Ruff gate without fixes,
3. run the full pytest suite.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence


def _run(command: Sequence[str]) -> None:
    """Run one quality command and stop immediately on failure."""
    printable = " ".join(command)
    print(f"\n> {printable}", flush=True)
    subprocess.run(command, check=True)


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the local Ruff and pytest quality gates."""
    parser = argparse.ArgumentParser(
        description="Apply and verify Ruff checks, then run the full pytest suite."
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Do not modify files; run Ruff verification and pytest only.",
    )
    args = parser.parse_args(argv)

    python = sys.executable
    try:
        if not args.check_only:
            _run((python, "-m", "ruff", "check", "src", "tests", "--fix"))
        _run((python, "-m", "ruff", "check", "src", "tests"))
        _run((python, "-m", "pytest"))
    except subprocess.CalledProcessError as exc:
        print(f"\nQuality gate failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode

    print("\nQuality gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
