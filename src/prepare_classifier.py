"""
Prepare the Kaggle marine-corrosion classification dataset.

Input (after `scripts/download_datasets.sh`):
  data/raw/marine-corrosion/<class>/*.jpg   (9 folders, 1,000 each)

Output (Ultralytics classify format — folder per class):
  data/cls/{train,val,test}/<class>/*.jpg

The full dataset is 4.71 GB. For a free-Colab run, use
--max-per-class 300 (2,700 images total). Use 0 for the full set
only if you have the time and disk. Splits are stratified per class,
seed 42, 70/15/15, and no file is copied to two splits.
"""
import argparse, random, shutil
from pathlib import Path

CLASSES = ["crevice_corrosion", "erosion_corrosion", "galvanic_corrosion",
           "healthy_structure", "mic_corrosion", "pitting_corrosion",
           "stress_corrosion", "under_insulation_corrosion", "uniform_corrosion"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw/marine-corrosion")
    ap.add_argument("--out", default="data/cls")
    ap.add_argument("--max-per-class", type=int, default=300)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    raw = Path(args.raw); out = Path(args.out)
    if not raw.exists():
        raise SystemExit(f"Folder not found: {raw}. Run scripts/download_datasets.sh first.")
    rng = random.Random(args.seed)
    total = 0
    for cls in CLASSES:
        src_dir = raw / cls
        if not src_dir.exists():
            print(f"WARNING: missing class folder {src_dir} — skipping"); continue
        files = sorted(p for p in src_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
        rng.shuffle(files)
        if args.max_per_class and len(files) > args.max_per_class:
            files = files[:args.max_per_class]
        n = len(files); n_train, n_val = int(n * 0.70), int(n * 0.15)
        for split, subset in [("train", files[:n_train]), ("val", files[n_train:n_train + n_val]),
                              ("test", files[n_train + n_val:])]:
            d = out / split / cls; d.mkdir(parents=True, exist_ok=True)
            for f in subset:
                shutil.copy2(f, d / f.name)
        print(f"{cls}: {len(files)} used (train {n_train}, val {n_val}, test {n - n_train - n_val})")
        total += len(files)
    print(f"total images: {total} -> {out}")


if __name__ == "__main__":
    main()
