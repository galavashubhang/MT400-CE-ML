# 🔩 Corrosion Vision — YOLO26 corrosion detection + Dive Deeper severity

**Author:** Shubhang S. Galagali, 231MT049 — Metallurgical and Materials Engineering, NITK Surathkal
**Role in this repo:** ML Engineer + Corrosion Engineer (design, training, and the standards notes are written as one project, not as two separate documents)

A senior-undergraduate engineering project that screens a steel-surface photo, locates corrosion with YOLO, and — only when the user toggles **Dive Deeper** — estimates corrosion **type** and **severity %** in a report format based on **ASTM D610**.

**Visual screening only.** This is not a certified inspection, not a thickness measurement, and not a repair instruction. See `docs/STANDARDS.md`.

---

## What it does

| Mode | Output |
|---|---|
| **Quick (default)** | Corrosion vs no corrosion + bounding boxes + confidences |
| **🔍 Dive Deeper (toggle)** | + Corrosion type (top-2, appearance only) + severity % (rust pixels in boxes) + ASTM D610 grade + distribution heuristic + recommendation band + downloadable PDF report |

## Architecture (two models, on purpose)

```
Photo
  │
  ├─ Stage 1 — YOLO26 detection (yolo26n.pt, fine-tuned, 1 class: corrosion)
  │     └─ Quick verdict: detected / not detected + boxes
  │
  └─ Stage 2 — only if Dive Deeper is ON and Stage 1 detected something
        ├─ YOLO26 classification (yolo26n-cls.pt, 9 marine classes)
        │     └─ Type: uniform / pitting / crevice / galvanic / erosion /
        │        MIC / stress / under-insulation / healthy
        └─ Severity (src/severity.py)
              ├─ Severity % = rust-coloured pixels inside boxes
              ├─ Box-area % = upper-bound coverage only (boxes overestimate)
              ├─ ASTM D610 grade from severity % (Table 1)
              └─ Distribution S/G/P/H = project heuristic, labelled as such
```

Why two models? A detection dataset with boxes and a classification dataset with type labels are different datasets. Pretending one model does both, or that a box area *is* severity, would be the two most common ways to oversell a project like this.

## Datasets (Kaggle, verified 2026-11-05)

### 1. Detection — `wednesday233/corrosion-detect-dataset` (MIT)
- https://www.kaggle.com/datasets/wednesday233/corrosion-detect-dataset
- **268 images, 268 YOLO label files, 8.53 MB**, ship-cabin corrosion areas, manually annotated.
- Limitation: small, and ship cabins are not bridges/pipelines. Test on your target asset before claiming it works there.

### 2. Classification — `ebrahim007/marine-corrosion-dataset` (Apache 2.0)
- https://www.kaggle.com/datasets/ebrahim007/marine-corrosion-dataset
- **9,000 images, 9 folders × 1,000, 4.71 GB**: crevice, erosion, galvanic, healthy, MIC, pitting, stress, under-insulation, uniform.
- For free Colab, train on `--max-per-class 300` first (2,700 images).

Full download + licence notes: `data/README.md`.

## Model — YOLO, latest version

Ultralytics docs (checked 2026-11-05) state **YOLO26, released January 2026, is the latest release and the recommended starting point for new projects**, with **YOLO11 as the mature alternative**. This repo therefore defaults to:

- Detection: `yolo26n.pt` (fallback `yolo11n.pt`)
- Classification: `yolo26n-cls.pt` (fallback `yolo11n-cls.pt`)

If your installed `ultralytics` does not know `yolo26n.pt`, upgrade it (`pip install -U ultralytics`) or switch to the fallback in `configs/config.yaml`. Do not demo with a COCO-pretrained model — it has no corrosion class.

## Quickstart — Colab (the intended training path)

```bash
# 1. In Colab, upload kaggle.json (Kaggle → Settings → API), then:
mkdir -p ~/.kaggle && cp kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json

# 2. Clone your GitHub repo in Colab, cd into it, then:
!bash scripts/download_datasets.sh
!python src/prepare_detection.py
!python src/prepare_classifier.py --max-per-class 300

# 3. Train (or run notebooks/01 and 02, which do the same steps):
!python src/train_detect.py --epochs 50 --batch 16
!python src/train_classify.py --epochs 25 --batch 32

# 4. Evaluate — this is the ONLY source for the numbers in your PPT:
!python src/evaluate.py
# -> results/metrics.json
```

Ready-made notebooks are in `notebooks/`:
- `01_train_detection_colab.ipynb` — detection training + validation
- `02_train_classifier_colab.ipynb` — type-classifier training + validation
- `03_demo_colab.ipynb` — Gradio demo in Colab (same `src/inference.py` as the app)

## Run the frontend

```bash
pip install -r requirements.txt
# After training, copy best.pt files:
#   runs/detect/.../weights/best.pt  -> models/detect/best.pt
#   runs/classify/.../weights/best.pt -> models/classify/best.pt
streamlit run app/app.py
```

If weights are missing, the app stops with the exact training step instead of inventing a result.

## PDF report

Upload a photo → Quick or Dive Deeper → **Download PDF report**.
The PDF contains: verdict, boxes, severity %, D610 grade, distribution, recommendation band, method note, and the page-1 disclaimer. See `src/pdf_report.py`.

## Hosting (you upload the repo — see docs/HOSTING.md)

1. Push this folder to GitHub (instructions in `docs/HOSTING.md`, Step 1).
2. Connect the repo on **Streamlit Community Cloud** (`app/app.py`) for a public demo link, **or** on Hugging Face Spaces.
3. For demo day, also have the local / Colab demo ready — venue Wi-Fi is the most common demo failure, not the model.

GitHub hosts code. It does not run Streamlit by itself — that split is explained, with the weights problem, in `docs/HOSTING.md`.

## Results — read this before quoting any number

**There are no claimed metrics in this README.** Metrics only exist after *your* Colab training run, in `results/metrics.json` (via `src/evaluate.py`). Paste those — mAP50, mAP50-95, precision, recall, top-1/top-5 — into the PPT results slide. Do not copy metrics from another paper, another dataset, or a different YOLO version into that slide.

The PPT in this repo (`Corrosion_Vision_Demo.pptx`, at the repo root when delivered) therefore has a **blank results table with the exact fields to fill**, plus the demo script in `docs/DEMO_SCRIPT.md`.

## Project structure

```
corrosion-vision/
├── app/app.py                  # Streamlit frontend (Quick + Dive Deeper + PDF)
├── src/
│   ├── inference.py            # predict(): detection + optional type/severity
│   ├── severity.py             # D610 grade, rust-pixel %, box %, distribution
│   ├── pdf_report.py           # ReportLab PDF
│   ├── prepare_detection.py    # Kaggle detection -> YOLO format, 70/15/15
│   ├── prepare_classifier.py   # Kaggle marine -> classify format, 70/15/15
│   ├── train_detect.py         # YOLO26 detection training
│   ├── train_classify.py       # YOLO26 classification training
│   └── evaluate.py             # test metrics -> results/metrics.json
├── notebooks/                  # Colab notebooks 01/02/03
├── configs/config.yaml         # model names, thresholds, D610 table
├── docs/                       # STANDARDS, HOSTING, DEMO_SCRIPT
├── tests/test_severity.py      # pytest, no ML needed
├── scripts/download_datasets.sh
└── data/README.md
```

## Limitations (say these in the demo)

- Detection dataset is 268 ship-cabin images — small and domain-specific.
- Boxes overestimate corroded area; severity therefore uses rust pixels, and box % is reported separately as an upper bound.
- Type from a photo is indicative, not a metallurgical diagnosis.
- A photo cannot measure thickness, corrosion rate, or subsurface corrosion.
- "No corrosion detected" means no box passed the threshold in that image — not a clean bill of health.

## Licences

- Code in this repo: MIT (see `LICENSE`).
- Detection dataset: MIT (Kaggle page, `wednesday233`).
- Marine classification dataset: Apache 2.0 (Kaggle page, `ebrahim007`).
- Ultralytics YOLO weights/code: see the Ultralytics licence in their repo — check it before redistributing weights.
- Dataset licences apply to the datasets, not to this code, and vice versa.
