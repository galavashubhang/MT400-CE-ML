#!/usr/bin/env bash
# Download the two Kaggle datasets. Kaggle requires an account + API token.
# 1. Kaggle -> Settings -> API -> Create New Token -> kaggle.json
# 2. In Colab: upload kaggle.json, then run:
#      mkdir -p ~/.kaggle && cp kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
# 3. Then run this script (or the same kaggle commands in Colab).
# Do NOT commit kaggle.json to GitHub. It is in .gitignore.
set -euo pipefail
mkdir -p data/raw

echo "== Detection: wednesday233/corrosion-detect-dataset (MIT, 268 images, YOLO labels) =="
kaggle datasets download -d wednesday233/corrosion-detect-dataset -p data/raw --unzip
# Kaggle unzips to data/raw/corrosion detect/ — normalise the name:
if [ -d "data/raw/corrosion detect" ]; then mv "data/raw/corrosion detect" data/raw/corrosion-detect; fi
ls data/raw/corrosion-detect

echo "== Classification: ebrahim007/marine-corrosion-dataset (Apache 2.0, 9,000 images, 4.71 GB) =="
echo "This is large. If Colab disk/time is tight, download it once, then use"
echo "src/prepare_classifier.py --max-per-class 300 to train on a subsample."
kaggle datasets download -d ebrahim007/marine-corrosion-dataset -p data/raw --unzip
ls data/raw/marine-corrosion-dataset 2>/dev/null || ls data/raw
echo "Done. Next: python src/prepare_detection.py && python src/prepare_classifier.py --max-per-class 300"
