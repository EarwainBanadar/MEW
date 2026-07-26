from pathlib import Path
import argparse, json
from .engine import ReportingEngine
from .models import ReportMetadata

def main() -> int:
    p = argparse.ArgumentParser(description="AP9.3.5.1 Reporting Engine")
    p.add_argument("evaluation", type=Path)
    p.add_argument("-o", "--output-dir", type=Path, required=True)
    p.add_argument("--title", default="AP9.3 Rule Evaluation Report")
    p.add_argument("--report-id", default="AP9.3-REPORT")
    p.add_argument("--stem", default="AP9.3_Evaluation_Report")
    a = p.parse_args()
    engine = ReportingEngine()
    data = engine.load_evaluation(a.evaluation)
    meta = ReportMetadata(report_id=a.report_id, title=a.title, source_name=str(a.evaluation))
    outputs = engine.write_all(data, meta, a.output_dir, a.stem)
    print(json.dumps({"status":"PASS","outputs":outputs,"summary":engine.summarize(data)}, indent=2, ensure_ascii=False))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
