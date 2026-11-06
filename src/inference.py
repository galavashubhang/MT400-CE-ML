"""
Inference: Quick mode + Dive Deeper mode.

Quick mode (always):
  Run the YOLO detection model. If any box has confidence >= threshold,
  verdict = "Corrosion detected", otherwise "No corrosion detected".
  "No corrosion detected" means: no box passed the threshold in THIS
  image. It is not a guarantee that the asset is corrosion-free.

Dive Deeper mode (toggle, only meaningful after a detection):
  1. Type: run the YOLO classification model on the whole image and on
     the largest detected crop, report the top-2 classes with
     probabilities. Type from appearance alone is indicative only —
     it is not a metallurgical diagnosis (that needs microscopy,
     environment and history).
  2. Severity: see src/severity.py — rust-pixel %, box-area %,
     ASTM D610 grade, distribution heuristic, recommendation band.

Weights are NOT in this repo (they are large and trained by the user
in Colab). Expected locations, overridable by argument:
  models/detect/best.pt     (YOLO26 detection, single class "corrosion")
  models/classify/best.pt   (YOLO26 classification, 9 marine classes)
If a weights file is missing, functions raise FileNotFoundError with
the exact Colab step that produces it — the app shows that message
instead of inventing a result.
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field

import cv2
import numpy as np

from .severity import severity_report

DETECT_DEFAULT = "models/detect/best.pt"
CLASSIFY_DEFAULT = "models/classify/best.pt"
CLASSIFY_CLASSES = [
    "crevice_corrosion", "erosion_corrosion", "galvanic_corrosion",
    "healthy_structure", "mic_corrosion", "pitting_corrosion",
    "stress_corrosion", "under_insulation_corrosion", "uniform_corrosion",
]


@dataclass
class Detection:
    x1: float; y1: float; x2: float; y2: float
    conf: float; cls: int = 0; label: str = "corrosion"


@dataclass
class Result:
    verdict: str
    detections: list = field(default_factory=list)
    annotated_bgr: object = None
    severity: dict | None = None
    type_prediction: list | None = None  # [(label, prob), ...]
    model_info: dict = field(default_factory=dict)


def load_yolo(weights_path: str, task_hint: str):
    if not os.path.exists(weights_path):
        raise FileNotFoundError(
            f"Weights not found: {weights_path}. Train first with the "
            f"Colab notebook for {task_hint} (notebooks/01 or 02), then "
            f"copy best.pt to this path. Do not demo with a COCO "
            f"pretrained model — it has no corrosion class."
        )
    from ultralytics import YOLO
    return YOLO(weights_path)


def draw_boxes(image_bgr, detections):
    out = image_bgr.copy()
    for d in detections:
        cv2.rectangle(out, (int(d.x1), int(d.y1)), (int(d.x2), int(d.y2)),
                      (0, 0, 255), 2)
        label = f"{d.label} {d.conf:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(out, (int(d.x1), int(d.y1) - th - 8),
                      (int(d.x1) + tw + 6, int(d.y1)), (0, 0, 255), -1)
        cv2.putText(out, label, (int(d.x1) + 3, int(d.y1) - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return out


def run_detection(image_bgr, detect_model, conf: float = 0.25, iou: float = 0.45):
    """Run a YOLO detection model (or a mock with .predict in tests)."""
    results = detect_model.predict(image_bgr, conf=conf, iou=iou, verbose=False)
    r = results[0]
    detections = []
    if r.boxes is not None and len(r.boxes) > 0:
        xyxy = r.boxes.xyxy.cpu().numpy()
        confs = r.boxes.conf.cpu().numpy()
        clss = r.boxes.cls.cpu().numpy() if r.boxes.cls is not None else [0] * len(xyxy)
        names = getattr(r, "names", {0: "corrosion"})
        for (x1, y1, x2, y2), c, k in zip(xyxy, confs, clss):
            detections.append(Detection(float(x1), float(y1), float(x2), float(y2),
                                        float(c), int(k), str(names.get(int(k), "corrosion"))))
    return detections


def run_classifier(image_bgr, classify_model, crop_box=None, top_k: int = 2):
    """Return [(label, prob), ...] from a YOLO classification model."""
    img = image_bgr
    if crop_box is not None:
        x1, y1, x2, y2 = [int(v) for v in crop_box]
        h, w = image_bgr.shape[:2]
        img = image_bgr[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
        if img.size == 0:
            img = image_bgr
    results = classify_model.predict(img, verbose=False)
    probs = results[0].probs
    if probs is None:
        return []
    top = probs.top5 if hasattr(probs, "top5") else np.argsort(-probs.data.cpu().numpy())[:top_k]
    data = probs.data.cpu().numpy()
    names = results[0].names if hasattr(results[0], "names") else {i: n for i, n in enumerate(CLASSIFY_CLASSES)}
    out = []
    for idx in list(top)[:top_k]:
        out.append((str(names.get(int(idx), CLASSIFY_CLASSES[int(idx)] if int(idx) < len(CLASSIFY_CLASSES) else str(idx))),
                    float(data[int(idx)])))
    return out


def predict(image_bgr, detect_model, classify_model=None, dive_deeper: bool = False,
            conf: float = 0.25, iou: float = 0.45) -> Result:
    detections = run_detection(image_bgr, detect_model, conf=conf, iou=iou)
    verdict = "Corrosion detected" if detections else "No corrosion detected"
    annotated = draw_boxes(image_bgr, detections)
    severity = None
    type_pred = None
    if dive_deeper and detections:
        boxes = [(d.x1, d.y1, d.x2, d.y2) for d in detections]
        severity = severity_report(image_bgr, boxes)
        if classify_model is not None:
            largest = max(detections, key=lambda d: (d.x2 - d.x1) * (d.y2 - d.y1))
            type_pred = run_classifier(
                image_bgr, classify_model,
                crop_box=(largest.x1, largest.y1, largest.x2, largest.y2))
    return Result(verdict=verdict, detections=detections, annotated_bgr=annotated,
                  severity=severity, type_prediction=type_pred)
