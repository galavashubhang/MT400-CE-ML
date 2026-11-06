"""
Evaluate trained models and write results/metrics.json.

This script produces NO numbers until you have trained. Run it after
notebooks 01/02, then paste its output into the PPT results slide
(docs/DEMO_SCRIPT.md tells you exactly which fields to copy).
Do not copy metrics from any other paper or dataset into that slide.
"""
import argparse, json
from pathlib import Path
from ultralytics import YOLO


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--detect", default="models/detect/best.pt")
    ap.add_argument("--classify", default="models/classify/best.pt")
    ap.add_argument("--data", default="data/yolo_detect/data.yaml")
    ap.add_argument("--cls-data", default="data/cls")
    ap.add_argument("--out", default="results/metrics.json")
    args = ap.parse_args()
    out = {}
    if Path(args.detect).exists():
        m = YOLO(args.detect)
        r = m.val(data=args.data, split="test", verbose=False)
        out["detection_test"] = {
            "map50": float(r.box.map50), "map50_95": float(r.box.map),
            "precision": float(r.box.mp), "recall": float(r.box.mr),
        }
        print("detection:", out["detection_test"])
    else:
        print(f"detector not found: {args.detect} — skipped")
    if Path(args.classify).exists():
        m = YOLO(args.classify)
        r = m.val(data=args.cls_data, split="test", verbose=False)
        out["classification_test"] = {"top1": float(r.top1), "top5": float(r.top5)}
        print("classification:", out["classification_test"])
    else:
        print(f"classifier not found: {args.classify} — skipped")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
