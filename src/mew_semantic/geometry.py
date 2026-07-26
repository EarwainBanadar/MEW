from __future__ import annotations
import math, re
from typing import Dict, Iterable, List, Optional, Tuple
from lxml import etree
from .model import Geometry, Point

NUM_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")

def f(value: Optional[str]) -> Optional[float]:
    if value is None: return None
    m=NUM_RE.search(value)
    return float(m.group(0)) if m else None

def parse_points(value: Optional[str]) -> List[Point]:
    if not value: return []
    nums=[float(x) for x in NUM_RE.findall(value)]
    return [Point(nums[i], nums[i+1]) for i in range(0,len(nums)-1,2)]

def path_points(d: Optional[str]) -> List[Point]:
    # AP9.1 extracts coordinate pairs conservatively. Precise Bézier bounds belong to AP10.
    if not d: return []
    nums=[float(x) for x in NUM_RE.findall(d)]
    return [Point(nums[i],nums[i+1]) for i in range(0,len(nums)-1,2)]

def bbox_from_points(points: Iterable[Point]) -> Optional[Dict[str,float]]:
    pts=list(points)
    if not pts: return None
    xs=[p.x for p in pts]; ys=[p.y for p in pts]
    return {"x":min(xs),"y":min(ys),"width":max(xs)-min(xs),"height":max(ys)-min(ys)}

def merge_bbox(boxes: Iterable[Optional[Dict[str,float]]]) -> Optional[Dict[str,float]]:
    bs=[b for b in boxes if b]
    if not bs: return None
    x1=min(b['x'] for b in bs); y1=min(b['y'] for b in bs)
    x2=max(b['x']+b['width'] for b in bs); y2=max(b['y']+b['height'] for b in bs)
    return {"x":x1,"y":y1,"width":x2-x1,"height":y2-y1}

def geometry_for(el: etree._Element, child_boxes: Iterable[Optional[Dict[str,float]]]=()) -> Geometry:
    tag=etree.QName(el).localname
    x=f(el.get('x')); y=f(el.get('y')); w=f(el.get('width')); h=f(el.get('height'))
    cx=f(el.get('cx')); cy=f(el.get('cy')); r=f(el.get('r'))
    rx=r if tag=='circle' else f(el.get('rx'))
    ry=r if tag=='circle' else f(el.get('ry'))
    pts=[]; box=None
    if tag in ('rect','image','foreignObject','svg') and None not in (x,y,w,h):
        box={"x":x,"y":y,"width":w,"height":h}
    elif tag in ('circle','ellipse') and None not in (cx,cy,rx,ry):
        box={"x":cx-rx,"y":cy-ry,"width":2*rx,"height":2*ry}
    elif tag=='line':
        x1=f(el.get('x1'));y1=f(el.get('y1'));x2=f(el.get('x2'));y2=f(el.get('y2'))
        if None not in (x1,y1,x2,y2): pts=[Point(x1,y1),Point(x2,y2)]; box=bbox_from_points(pts)
    elif tag in ('polygon','polyline'):
        pts=parse_points(el.get('points')); box=bbox_from_points(pts)
    elif tag=='path':
        pts=path_points(el.get('d')); box=bbox_from_points(pts)
    elif tag=='text':
        # text dimensions are renderer-dependent; retain anchor point only
        if x is not None and y is not None: box={"x":x,"y":y,"width":0.0,"height":0.0}
    if tag=='g': box=merge_bbox(child_boxes)
    return Geometry(x=x,y=y,width=w,height=h,cx=cx,cy=cy,radius=r,bbox=box,transform=el.get('transform'),path_data=el.get('d'),points=pts)
