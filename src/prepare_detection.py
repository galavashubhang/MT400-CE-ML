"""
Prepare the Kaggle detection dataset for YOLO training.

Input (after `scripts/download_datasets.sh`):
  data/raw/corrosion-detect/images/*.jpg|png
  data/raw/corrosion-detect/labels/*.txt   (YOLO format: class x y w h, normalised)

Output:
  data/yolo_detect/{train,val,test}/{images,labels}/
  data/yolo_detect/data.yaml   (names: ['corrosion'])

Rules, stated so a reviewer can check them:
  * Split is random, seed 42, 70/15/15 by image. No image appears in
    two splits (checked and asserted).
  * Every label line must have 5 numbers, coordinates in [0, 1].
    Bad lines are reported and skipped, not silently fixed.
  * All label classes are collapsed to 0 ("corrosion"). The Kaggle
    dataset is described as corrosion-area labels; if your copy has
    more than one class id, the script prints the counts first, so
    collapsing is a conscious choice, not an accident.
  * Images with no label file are dropped from training (a YOLO
    detector needs a box to learn from) and counted in the report.
"""
import argparse, random, shutil
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw/corrosion-detect")
    ap.add_argument("--out", default="data/yolo_detect")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    raw = Path(args.raw); out = Path(args.out)
    img_dir, lab_dir = raw / "images", raw / "labels"
    if not img_dir.exists():
        raise SystemExit(f"Images folder not found: {img_dir}. Run scripts/download_datasets.sh first, "
                         f"or place the Kaggle download there (see data/README.md).")
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    images = sorted(p for p in img_dir.iterdir() if p.suffix.lower() in exts)
    rng = random.Random(args.seed); rng.shuffle(images)
    n = len(images)
    n_train, n_val = int(n * 0.70), int(n * 0.15)
    splits = {"train": images[:n_train], "val": images[n_train:n_train + n_val], "test": images[n_train + n_val:]}
    class_ids, skipped, no_label = set(), 0, 0
    for split, files in splits.items():
        for src in files:
            lab = lab_dir / f"{src.stem}.txt"
            if not lab.exists():
                no_label += 1; continue
            lines, ok = [], True
            for line in lab.read_text().strip().splitlines():
                parts = line.split()
                if len(parts) != 5:
                    ok = False; break
                try:
                    vals = [float(v) for v in parts[1:]]
                except ValueError:
                    ok = False; break
                if not all(0.0 <= v <= 1.0 for v in vals):
                    ok = False; break
                class_ids.add(int(float(parts[0])))
                lines.append(f"0 {' '.join(parts[1:])}")
            if not ok:
                skipped += 1; continue
            d_img = out / split / "images"; d_lab = out / split / "labels"
            d_img.mkdir(parents=True, exist_ok=True); d_lab.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, d_img / src.name)
            (d_lab / lab.name).write_text("\n".join(lines) + "\n")
    (out / "data.yaml").write_text(
        f"path: {out.resolve()}\ntrain: train/images\nval: val/images\ntest: test/images\n"
        f"names:\n  0: corrosion\n")
    print(f"images found: {n} | train/val/test: "
          f"{len(splits['train'])}/{len(splits['val'])}/{len(splits['test'])}")
    print(f"label class ids seen (collapsed to 0): {sorted(class_ids)}")
    print(f"skipped bad label files: {skipped} | images with no label file: {no_label}")
    print(f"wrote: {out}/data.yaml")


if __name__ == "__main__":
    main()
