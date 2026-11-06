"""Generate the three Colab notebooks from the repo's own scripts.

The notebooks do not duplicate training logic: they install, download,
and call src/*.py, so the code a reviewer reads in GitHub is the code
that runs in Colab. Regenerate after editing the scripts:
    python make_notebooks.py
"""
import json
from pathlib import Path


def nb(cells):
    out = []
    for kind, text in cells:
        if kind == "md":
            out.append({"cell_type": "markdown", "metadata": {}, "source": text.splitlines(True)})
        else:
            out.append({"cell_type": "code", "execution_count": None, "metadata": {},
                        "outputs": [], "source": text.splitlines(True)})
    return {"cells": out,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                         "language_info": {"name": "python", "version": "3.11"}},
            "nbformat": 4, "nbformat_minor": 5}


def write(name, cells):
    Path("notebooks").mkdir(exist_ok=True)
    Path(f"notebooks/{name}").write_text(json.dumps(nb(cells), indent=1))
    print(name, len(cells), "cells")


COMMON_SETUP = """# Corrosion Vision — Colab setup
# 1. Runtime -> Change runtime type -> GPU (T4 is enough for nano models).
# 2. Upload your GitHub repo (or this folder) to Colab, and cd into it.
# 3. Upload kaggle.json (Kaggle -> Settings -> API) to Colab first.
import os, shutil
os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)
if os.path.exists("kaggle.json"):
    shutil.copy("kaggle.json", os.path.expanduser("~/.kaggle/kaggle.json"))
    os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)
    print("kaggle.json installed (never commit it).")
else:
    print("kaggle.json not found in this folder — upload it, then re-run this cell.")
!pip install -q -r requirements.txt
!python -c "import ultralytics; print('ultralytics', ultralytics.__version__)"
!nvidia-smi | head -12
"""

write("01_train_detection_colab.ipynb", [
    ("md", "# 01 — Train the YOLO26 corrosion detector (Colab)\n\n**Dataset:** Kaggle `wednesday233/corrosion-detect-dataset` (MIT, 268 images, YOLO labels, ship cabins).\n\n**Output:** `runs/detect/yolo26n-corrosion/weights/best.pt` → copy to `models/detect/best.pt` for the app.\n\n**No metrics are pre-filled anywhere in this project.** The metrics you report are the ones this notebook prints at the end."),
    ("code", COMMON_SETUP),
    ("code", "!bash scripts/download_datasets.sh\n!ls data/raw/corrosion-detect/"),
    ("code", "!python src/prepare_detection.py\n!cat data/yolo_detect/data.yaml"),
    ("code", "!python src/train_detect.py --model yolo26n.pt --epochs 50 --batch 16 --imgsz 640\n# If yolo26n.pt cannot be downloaded by your ultralytics version:\n#   !python src/train_detect.py --model yolo11n.pt --epochs 50 --batch 16 --imgsz 640"),
    ("code", "!python src/evaluate.py --detect runs/detect/yolo26n-corrosion/weights/best.pt --classify models/classify/best.pt\n# If you have not trained the classifier yet, the classifier line is skipped — that is expected."),
    ("md", "## What to download before closing Colab\n\n- `runs/detect/yolo26n-corrosion/weights/best.pt`\n- `results/metrics.json` (paste its detection numbers into the PPT results slide)\n- The training curves / confusion matrix from `runs/detect/yolo26n-corrosion/` for the demo appendix."),
])

write("02_train_classifier_colab.ipynb", [
    ("md", "# 02 — Train the YOLO26 corrosion-type classifier (Dive Deeper)\n\n**Dataset:** Kaggle `ebrahim007/marine-corrosion-dataset` (Apache 2.0, 9,000 images, 9 classes, 4.71 GB).\n\n**Colab default:** `--max-per-class 300` (2,700 images). Use the full set only if disk/time allow.\n\n**Output:** `runs/classify/yolo26n-corrosion-type/weights/best.pt` → copy to `models/classify/best.pt`."),
    ("code", COMMON_SETUP),
    ("code", "!bash scripts/download_datasets.sh\n!ls data/raw/ | head -20"),
    ("code", "!python src/prepare_classifier.py --max-per-class 300"),
    ("code", "!python src/train_classify.py --model yolo26n-cls.pt --epochs 25 --batch 32 --imgsz 224\n# Fallback if yolo26n-cls.pt is unavailable:\n#   !python src/train_classify.py --model yolo11n-cls.pt --epochs 25 --batch 32 --imgsz 224"),
    ("code", "!python src/evaluate.py --detect models/detect/best.pt --classify runs/classify/yolo26n-corrosion-type/weights/best.pt"),
    ("md", "## What to download before closing Colab\n\n- `runs/classify/yolo26n-corrosion-type/weights/best.pt`\n- `results/metrics.json` (paste its classification numbers into the PPT results slide)."),
])

write("03_demo_colab.ipynb", [
    ("md", "# 03 — Demo in Colab (Gradio, same code as the Streamlit app)\n\nUse this when the venue has no hosted app, or as a backup to Streamlit Cloud.\nIt runs `src/inference.py` directly, so a bug fixed in the app is fixed here too.\n\n**You need:** `models/detect/best.pt` (and `models/classify/best.pt` for Dive Deeper) uploaded to Colab. Without them, the demo stops with the training step — it will not pretend a COCO model detects corrosion."),
    ("code", COMMON_SETUP.replace("!python -c \"import ultralytics; print('ultralytics', ultralytics.__version__)\"", "!python -c \"import ultralytics; print('ultralytics', ultralytics.__version__)\"\n!pip install -q gradio")),
    ("code", """import gradio as gr, cv2, numpy as np, sys
sys.path.insert(0, ".")
from src.inference import load_yolo, predict

detect = load_yolo("models/detect/best.pt", "detection (notebook 01)")
print("Detector loaded. Upload a validation image below.")

def demo(image, dive_deeper, conf):
    if image is None:
        return "Upload an image first.", None
    bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    clf = None
    if dive_deeper:
        clf = load_yolo("models/classify/best.pt", "classification (notebook 02)")
    res = predict(bgr, detect, clf, dive_deeper=dive_deeper, conf=conf)
    ann = cv2.cvtColor(res.annotated_bgr, cv2.COLOR_BGR2RGB)
    lines = [f"Verdict: {res.verdict}  |  Boxes: {len(res.detections)}"]
    if res.severity:
        s = res.severity
        lines += [f"Severity %: {s['severity_pct']}%  |  ASTM D610 grade: {s['astm_d610_grade']}  |  "
                  f"Box-area % (upper bound): {s['box_area_pct']}%  |  Distribution: {s['distribution']}"]
        lines.append(s["recommendation"])
    if res.type_prediction:
        lines += [f"Type: {label} ({prob:.1%})" for label, prob in res.type_prediction]
    return "\\n".join(lines), ann

gr.Interface(
    fn=demo,
    inputs=[gr.Image(label="Steel-surface photo"),
            gr.Checkbox(label="Dive Deeper — type + severity %", value=False),
            gr.Slider(0.05, 0.95, 0.25, step=0.05, label="Confidence threshold")],
    outputs=[gr.Textbox(label="Result"), gr.Image(label="Annotated image")],
    title="Corrosion Vision — Colab demo",
    description="Visual screening only, not a certified inspection. See docs/STANDARDS.md.",
).launch(share=True)
"""),
])
print("done")
