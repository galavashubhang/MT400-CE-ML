"""
Severity estimation — with the standard kept separate from the heuristic.

What is from a standard (ASTM D610, SSPC-VIS 2):
  Rust grade is a 0-10 scale based on the percentage of visible surface
  rusted. The table below is the D610 Table 1 scale, as published:
    10: <=0.01%   9: >0.01-0.03%   8: >0.03-0.10%   7: >0.10-0.30%
     6: >0.30-1%    5: >1-3%         4: >3-10%        3: >10-16%
     2: >16-33%     1: >33-50%       0: >50%
  Distribution letters in D610 are S = spot, G = general, P = pinpoint,
  H = hybrid. D610's own method is visual comparison to pictorial
  standards (or an agreed electronic-scanning method).

What is a PROJECT HEURISTIC in this repo (not the standard):
  * rust_pixel_pct — % of pixels inside detected boxes whose colour
    falls in a rust-brown HSV range. It is an estimate of visible rust
    area, not a laboratory measurement of metal loss.
  * box_area_pct — union of detection boxes / image area. Boxes
    overestimate true corroded area (a diagonal patch fills a rectangle),
    so this is reported as an upper-bound coverage, never as severity.
  * distribution — inferred from box count/size/spread by the rules in
    `distribution_from_boxes`. It is NOT a D610 visual comparison.
  * recommendation_band — a project decision band for demo triage.
    It is NOT a repair threshold from ASTM, AMPP, API or any code.
    A real asset decision needs a qualified inspector, thickness
    measurement and the applicable code — see docs/STANDARDS.md.

ISO 8501-1 rust grades A-D are deliberately NOT output from a %:
  they describe the pre-treatment condition of uncoated steel
  (adhering mill scale, flaking, slight/general pitting visible), which
  cannot be inferred from a rust percentage alone.
"""
from __future__ import annotations
import numpy as np

D610_TABLE = [
    (10, 0.01), (9, 0.03), (8, 0.10), (7, 0.30), (6, 1.00),
    (5, 3.00), (4, 10.00), (3, 16.00), (2, 33.00), (1, 50.00), (0, 100.00),
]

RECOMMENDATION_BANDS = [
    ((9, 10), "Monitor — re-inspect at the next scheduled interval."),
    ((6, 8), "Plan maintenance — schedule cleaning / coating repair."),
    ((3, 5), "Prioritise — detailed inspection and repair planning."),
    ((0, 2), "Urgent detailed inspection — do not defer on a load-bearing asset."),
]


def d610_grade(rust_pct: float) -> int:
    """Map % rusted to ASTM D610 grade. rust_pct is clipped to [0, 100]."""
    p = float(np.clip(rust_pct, 0.0, 100.0))
    for grade, upper in D610_TABLE:
        if p <= upper:
            return grade
    return 0


def recommendation_band(grade: int) -> str:
    for (lo, hi), text in RECOMMENDATION_BANDS:
        if lo <= grade <= hi:
            return text
    return "Inspect — grade out of expected range."


def box_union_area_pct(boxes, img_w: int, img_h: int) -> float:
    """Union of boxes as % of image area (upper-bound coverage).

    boxes: list of (x1, y1, x2, y2) in pixels. Uses a coarse grid union
    so overlapping boxes are not double-counted.
    """
    if not boxes or img_w <= 0 or img_h <= 0:
        return 0.0
    mask = np.zeros((img_h, img_w), dtype=bool)
    for x1, y1, x2, y2 in boxes:
        xa, xb = max(0, int(x1)), min(img_w, int(x2))
        ya, yb = max(0, int(y1)), min(img_h, int(y2))
        if xb > xa and yb > ya:
            mask[ya:yb, xa:xb] = True
    return float(mask.mean() * 100.0)


def rust_pixel_pct(image_bgr, boxes) -> float:
    """% rust-coloured pixels inside detected boxes (heuristic).

    image_bgr: OpenCV BGR array. Rust brown/orange in HSV is roughly
    H 5-30, S >= 40, V 20-220 (OpenCV H range 0-179). If there are no
    boxes, returns 0.0 — severity is only reported where corrosion
    was detected.
    """
    import cv2
    if not boxes:
        return 0.0
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([5, 40, 20]), np.array([30, 255, 220]))
    h, w = mask.shape
    box_mask = np.zeros_like(mask)
    for x1, y1, x2, y2 in boxes:
        xa, xb = max(0, int(x1)), min(w, int(x2))
        ya, yb = max(0, int(y1)), min(h, int(y2))
        if xb > xa and yb > ya:
            box_mask[ya:yb, xa:xb] = 255
    inside = (box_mask > 0)
    if inside.sum() == 0:
        return 0.0
    return float((mask[inside] > 0).mean() * 100.0)


def distribution_from_boxes(boxes, img_w: int, img_h: int) -> str:
    """Heuristic S/G/P/H distribution from box geometry (not D610 visual).

    S (spot):     1 box, or 1 box dominating >50% of total box area.
    P (pinpoint): >=5 boxes and >=70% of them are <1% of image area each.
    G (general):  >=4 boxes, none dominating, spread across the image.
    H (hybrid):   everything else / mixed pattern.
    """
    if not boxes:
        return "—"
    areas = [max(0.0, (x2 - x1) * (y2 - y1)) for x1, y1, x2, y2 in boxes]
    img_area = max(1.0, float(img_w * img_h))
    total = sum(areas)
    if len(boxes) == 1 or (total > 0 and max(areas) / total > 0.5):
        return "S (spot — heuristic)"
    small = sum(1 for a in areas if a / img_area < 0.01)
    if len(boxes) >= 5 and small / len(boxes) >= 0.7:
        return "P (pinpoint — heuristic)"
    if len(boxes) >= 4:
        return "G (general — heuristic)"
    return "H (hybrid — heuristic)"


def severity_report(image_bgr, boxes) -> dict:
    """Full severity dict for one image. All % are of image area unless noted."""
    h, w = image_bgr.shape[:2]
    box_pct = box_union_area_pct(boxes, w, h)
    rust_pct = rust_pixel_pct(image_bgr, boxes)
    grade = d610_grade(rust_pct)
    return {
        "n_boxes": len(boxes),
        "box_area_pct": round(box_pct, 2),
        "rust_pixel_pct": round(rust_pct, 2),
        "severity_pct": round(rust_pct, 2),  # primary severity = rust-pixel %
        "astm_d610_grade": grade,
        "distribution": distribution_from_boxes(boxes, w, h),
        "recommendation": recommendation_band(grade),
        "method_note": (
            "Severity % = rust-coloured pixels inside detected boxes. "
            "Box area % is an upper-bound coverage only. "
            "D610 grade is from the % via the D610 table; distribution "
            "and recommendation are project heuristics, not the standard."
        ),
    }
