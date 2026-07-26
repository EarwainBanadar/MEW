from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parser import SemanticSvgParser


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AP9.1 SVG Semantic Parser")
    parser.add_argument("svg")
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        document = SemanticSvgParser(strict=args.strict).parse(args.svg)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                document.to_dict(),
                ensure_ascii=False,
                indent=2 if args.pretty else None,
            ),
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "output": str(output_path.resolve()),
                    "statistics": document.statistics,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
