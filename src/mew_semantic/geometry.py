from __future__ import annotations

import re
from collections.abc import Iterable

from lxml import etree

from .model import Geometry, Point

NUM_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def f(value: str | None) -> float | None:
    if value is None:
        return None
    match = NUM_RE.search(value)
    return float(match.group(0)) if match else None


def parse_points(value: str | None) -> list[Point]:
    if not value:
        return []
    numbers = [float(item) for item in NUM_RE.findall(value)]
    return [Point(numbers[index], numbers[index + 1]) for index in range(0, len(numbers) - 1, 2)]


def path_points(data: str | None) -> list[Point]:
    # AP9.1 extracts coordinate pairs conservatively. Precise Bézier bounds belong to AP10.
    if not data:
        return []
    numbers = [float(item) for item in NUM_RE.findall(data)]
    return [Point(numbers[index], numbers[index + 1]) for index in range(0, len(numbers) - 1, 2)]


def bbox_from_points(points: Iterable[Point]) -> dict[str, float] | None:
    point_list = list(points)
    if not point_list:
        return None
    x_values = [point.x for point in point_list]
    y_values = [point.y for point in point_list]
    return {
        "x": min(x_values),
        "y": min(y_values),
        "width": max(x_values) - min(x_values),
        "height": max(y_values) - min(y_values),
    }


def merge_bbox(boxes: Iterable[dict[str, float] | None]) -> dict[str, float] | None:
    present_boxes = [box for box in boxes if box]
    if not present_boxes:
        return None
    x1 = min(box["x"] for box in present_boxes)
    y1 = min(box["y"] for box in present_boxes)
    x2 = max(box["x"] + box["width"] for box in present_boxes)
    y2 = max(box["y"] + box["height"] for box in present_boxes)
    return {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1}


def geometry_for(
    element: etree._Element,
    child_boxes: Iterable[dict[str, float] | None] = (),
) -> Geometry:
    tag = etree.QName(element).localname
    x = f(element.get("x"))
    y = f(element.get("y"))
    width = f(element.get("width"))
    height = f(element.get("height"))
    cx = f(element.get("cx"))
    cy = f(element.get("cy"))
    radius = f(element.get("r"))
    rx = radius if tag == "circle" else f(element.get("rx"))
    ry = radius if tag == "circle" else f(element.get("ry"))
    points: list[Point] = []
    box = None

    if tag in ("rect", "image", "foreignObject", "svg") and None not in (
        x,
        y,
        width,
        height,
    ):
        box = {"x": x, "y": y, "width": width, "height": height}
    elif tag in ("circle", "ellipse") and None not in (cx, cy, rx, ry):
        box = {"x": cx - rx, "y": cy - ry, "width": 2 * rx, "height": 2 * ry}
    elif tag == "line":
        x1 = f(element.get("x1"))
        y1 = f(element.get("y1"))
        x2 = f(element.get("x2"))
        y2 = f(element.get("y2"))
        if None not in (x1, y1, x2, y2):
            points = [Point(x1, y1), Point(x2, y2)]
            box = bbox_from_points(points)
    elif tag in ("polygon", "polyline"):
        points = parse_points(element.get("points"))
        box = bbox_from_points(points)
    elif tag == "path":
        points = path_points(element.get("d"))
        box = bbox_from_points(points)
    elif tag == "text" and x is not None and y is not None:
        # Text dimensions are renderer-dependent; retain the anchor point only.
        box = {"x": x, "y": y, "width": 0.0, "height": 0.0}

    if tag == "g":
        box = merge_bbox(child_boxes)

    return Geometry(
        x=x,
        y=y,
        width=width,
        height=height,
        cx=cx,
        cy=cy,
        radius=radius,
        bbox=box,
        transform=element.get("transform"),
        path_data=element.get("d"),
        points=points,
    )
