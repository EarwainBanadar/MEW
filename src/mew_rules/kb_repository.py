from __future__ import annotations

import re
from dataclasses import dataclass

from .model import RuleDefinition


class KnowledgeBaseError(RuntimeError):
 pass
class DuplicateKnowledgeRule(KnowledgeBaseError):
 pass
class InvalidKnowledgeRule(KnowledgeBaseError):
 pass
class UnsupportedKnowledgeFormat(KnowledgeBaseError):
 pass
def parse_semver(v:str)->tuple[int,int,int]:
 m=re.fullmatch(r"(\d+)\.(\d+)\.(\d+)",v.strip())
 if not m: raise InvalidKnowledgeRule(f"Invalid semantic version: {v}")
 return tuple(map(int,m.groups()))
@dataclass(frozen=True)
class KnowledgeRuleRecord:
 definition:RuleDefinition; source_path:str; source_format:str; source_sha256:str
 def to_dict(self): return {'definition':self.definition.to_dict(),'source_path':self.source_path,'source_format':self.source_format,'source_sha256':self.source_sha256}
class KnowledgeBaseRepository:
 def __init__(self): self._records:dict[tuple[str,str],KnowledgeRuleRecord]={}
 def __len__(self): return len(self._records)
 def add(self,r):
  k=(r.definition.rule_id,r.definition.version); parse_semver(k[1])
  if k in self._records: raise DuplicateKnowledgeRule(f"{k[0]}@{k[1]}")
  self._records[k]=r
 def get(self,rule_id,version:str | None=None):
  if version is not None:
   if (rule_id,version) not in self._records: raise KeyError(f"Unknown rule version: {rule_id}@{version}")
   return self._records[(rule_id,version)]
  vs=[v for r,v in self._records if r==rule_id]
  if not vs: raise KeyError(f"Unknown rule: {rule_id}")
  return self._records[(rule_id,max(vs,key=parse_semver))]
 def versions(self,rule_id): return sorted([v for r,v in self._records if r==rule_id],key=parse_semver)
 def list(self,category=None,severity=None,enabled_only=False,latest_only=False):
  rs=list(self._records.values())
  if latest_only:
   d={}
   for r in rs:
    rid=r.definition.rule_id
    if rid not in d or parse_semver(r.definition.version)>parse_semver(d[rid].definition.version): d[rid]=r
   rs=list(d.values())
  if category is not None: rs=[r for r in rs if r.definition.category==category]
  if severity is not None: rs=[r for r in rs if r.definition.severity==severity]
  if enabled_only: rs=[r for r in rs if r.definition.enabled_by_default]
  return sorted(rs,key=lambda r:(r.definition.rule_id,parse_semver(r.definition.version)))
 def manifest(self,latest_only=False):
  rs=self.list(latest_only=latest_only); return {'rule_count':len(rs),'latest_only':latest_only,'rules':[r.to_dict() for r in rs]}
