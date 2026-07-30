import argparse
import json
from pathlib import Path

from .kb_loader import KnowledgeBaseLoader


def main():
 p=argparse.ArgumentParser();p.add_argument('knowledge_base',type=Path);p.add_argument('-o','--output',type=Path,required=True);p.add_argument('--latest-only',action='store_true');a=p.parse_args();r=KnowledgeBaseLoader().load_directory(a.knowledge_base);m=r.manifest(a.latest_only);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(m,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps({'status':'PASS','rule_count':m['rule_count']}));return 0
if __name__=='__main__':
 raise SystemExit(main())
