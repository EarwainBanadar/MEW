from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .kb_repository import (
 InvalidKnowledgeRule,
 KnowledgeBaseRepository,
 KnowledgeRuleRecord,
 UnsupportedKnowledgeFormat,
)
from .model import RuleCategory, RuleDefinition, RuleScope, RuleSeverity

REQ={'rule_id','version','title','description','rationale','category','severity','scope'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def definition(d:dict[str,Any]):
 miss=sorted(REQ-set(d))
 if miss:
  raise InvalidKnowledgeRule('Missing required fields: '+', '.join(miss))
 try:
  return RuleDefinition(rule_id=str(d['rule_id']),version=str(d['version']),title=str(d['title']),description=str(d['description']),rationale=str(d['rationale']),category=RuleCategory(str(d['category'])),severity=RuleSeverity(str(d['severity'])),scope=RuleScope(str(d['scope'])),enabled_by_default=bool(d.get('enabled_by_default',True)),tags=list(d.get('tags',[])),acceptance_criteria=list(d.get('acceptance_criteria',[])))
 except Exception as e:
  raise InvalidKnowledgeRule(str(e)) from e
def parse_markdown_rule(text):
 m=re.match(r'\A---\s*\n(.*?)\n---(?:\s*\n|\Z)',text,re.S)
 if not m:
  raise InvalidKnowledgeRule('Markdown rule requires YAML-like front matter')
 d={}
 for raw in m.group(1).splitlines():
  line=raw.strip()
  if not line or line.startswith('#'):
   continue
  if ':' not in line:
   raise InvalidKnowledgeRule(f'Invalid metadata line: {raw}')
  k,v=map(str.strip,line.split(':',1))
  if v.lower() in ('true','false'):
   d[k]=v.lower()=='true'
  elif v.startswith('[') and v.endswith(']'):
   x=v[1:-1].strip(); d[k]=[] if not x else [i.strip() for i in x.split(',')]
  else:
   d[k]=v
 return d
class KnowledgeBaseLoader:
 def load_file(self,path:Path):
  s=path.suffix.lower()
  if s=='.json': d=json.loads(path.read_text(encoding='utf-8')); fmt='json'
  elif s in ('.md','.markdown'): d=parse_markdown_rule(path.read_text(encoding='utf-8')); fmt='markdown'
  else: raise UnsupportedKnowledgeFormat(str(path))
  return KnowledgeRuleRecord(definition(d),str(path),fmt,sha(path))
 def load_directory(self,directory:Path,recursive=True):
  repo=KnowledgeBaseRepository(); it=directory.rglob('*') if recursive else directory.glob('*')
  for p in sorted([p for p in it if p.is_file() and p.suffix.lower() in ('.json','.md','.markdown')],key=str): repo.add(self.load_file(p))
  return repo
