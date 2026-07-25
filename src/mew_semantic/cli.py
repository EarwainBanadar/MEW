from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .parser import SemanticSvgParser

def main(argv=None) -> int:
    p=argparse.ArgumentParser(description='AP9.1 SVG Semantic Parser')
    p.add_argument('svg')
    p.add_argument('-o','--output',required=True)
    p.add_argument('--strict',action='store_true')
    p.add_argument('--pretty',action='store_true')
    a=p.parse_args(argv)
    try:
        doc=SemanticSvgParser(strict=a.strict).parse(a.svg)
        out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(doc.to_dict(),ensure_ascii=False,indent=2 if a.pretty else None),encoding='utf-8')
        print(json.dumps({"status":"PASS","output":str(out.resolve()),"statistics":doc.statistics},ensure_ascii=False,indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status":"FAIL","error":str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__': raise SystemExit(main())
