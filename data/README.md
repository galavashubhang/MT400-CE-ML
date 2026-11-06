# Data — read before downloading

Data and trained weights are **not** committed to GitHub (see `.gitignore`).
Download them in Colab, train there, and copy only `best.pt` out for the app.

## 1. Detection — Kaggle, MIT licence
- Dataset: `wednesday233/corrosion-detect-dataset`
- Page: https://www.kaggle.com/datasets/wednesday233/corrosion-detect-dataset
- Verified 2026-11-05: 268 images, 268 YOLO label files, 8.53 MB, ship-cabin
  corrosion areas, manually annotated YOLO labels.
- Limitation to state in the demo: 268 images is small, and the domain is
  ship cabins, not specifically bridges/pipelines. Generalisation to a new
  asset type must be tested on that asset type — do not claim it works
  there until you have tested it there.

## 2. Classification (Dive Deeper type) — Kaggle, Apache 2.0 licence
- Dataset: `ebrahim007/marine-corrosion-dataset`
- Page: https://www.kaggle.com/datasets/ebrahim007/marine-corrosion-dataset
- Verified 2026-11-05: 9,000 images in 9 folders of 1,000 each, 4.71 GB:
  crevice, erosion, galvanic, healthy_structure, mic, pitting, stress,
  under_insulation, uniform corrosion. Images are 512×512 in the
  literature that uses this dataset; check your download's sizes.
- For free Colab, train on `--max-per-class 300` first (2,700 images).
  Full 9,000 only if disk/time allow.

## 3. How to get them in Colab
1. Kaggle → Settings → API → Create New Token → download `kaggle.json`.
2. In Colab, upload it, then:
   ```
   mkdir -p ~/.kaggle && cp kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
   !bash scripts/download_datasets.sh
   ```
3. Never commit `kaggle.json`. Never paste its contents in chat or in a notebook.

## 4. Folder layout expected by the code
```
data/raw/corrosion-detect/images/*.jpg
data/raw/corrosion-detect/labels/*.txt
data/raw/marine-corrosion/<class>/*.jpg
data/yolo_detect/{train,val,test}/{images,labels}/ + data.yaml   (made by prepare_detection.py)
data/cls/{train,val,test}/<class>/                               (made by prepare_classifier.py)
models/detect/best.pt                                            (after training)
models/classify/best.pt                                          (after training)
```
