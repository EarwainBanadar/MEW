from __future__ import annotations
from pathlib import Path
import argparse, datetime, json
from .builder import ReleaseBuilder
from .models import ReleaseDescriptor

def main() -> int:
    p=argparse.ArgumentParser(description="AP9.3.5.2 Release Builder")
    p.add_argument("source_root",type=Path)
    p.add_argument("output_root",type=Path)
    p.add_argument("--release-id",required=True)
    p.add_argument("--version",required=True)
    p.add_argument("--title",required=True)
    p.add_argument("--work-package",default="AP9.3.5.2")
    p.add_argument("--include",action="append",required=True)
    p.add_argument("--required",action="append",default=[])
    args=p.parse_args()
    builder=ReleaseBuilder()
    files=builder.discover(args.source_root,args.include)
    records=builder.inventory(args.source_root,files,args.required)
    descriptor=ReleaseDescriptor(args.release_id,args.version,args.title,args.work_package,"RELEASE_CANDIDATE",datetime.datetime.now(datetime.timezone.utc).isoformat(),str(args.source_root.resolve()))
    result=builder.build(descriptor,records,args.output_root)
    verification=builder.verify(Path(result.release_directory))
    print(json.dumps({"build":result.to_dict(),"verification":verification},indent=2,ensure_ascii=False))
    return 0 if verification["status"]=="PASS" else 2

if __name__ == "__main__": raise SystemExit(main())
