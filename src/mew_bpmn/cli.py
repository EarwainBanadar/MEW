
from __future__ import annotations
import argparse, json
from pathlib import Path
from .builder import SemanticModelBuilder

def main() -> int:
    p = argparse.ArgumentParser(description="AP9.2 BPMN Object Model builder")
    p.add_argument("semantic_json", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("--analysis", type=Path)
    args = p.parse_args()

    repo = SemanticModelBuilder().build_from_path(args.semantic_json)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(repo.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    analysis = repo.graph_analysis()
    payload = {
        "object_count": len(repo),
        "flow_count": len(repo.flows()),
        "flow_node_count": len(repo.flow_nodes()),
        "repository_errors": repo.validate(),
        "graph": {
            "node_count": analysis.node_count,
            "edge_count": analysis.edge_count,
            "roots": analysis.roots,
            "sinks": analysis.sinks,
            "unreachable": analysis.unreachable,
            "cycles": analysis.cycles,
        }
    }
    if args.analysis:
        args.analysis.parent.mkdir(parents=True, exist_ok=True)
        args.analysis.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not payload["repository_errors"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
