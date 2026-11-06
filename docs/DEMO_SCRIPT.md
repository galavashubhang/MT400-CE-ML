# Demo script — 5 minutes, in front of your professor

Use this order. It is designed so that a failure at any step still
leaves you with something honest to show, instead of a frozen screen.

## 0. Before the demo (do not skip)
- [ ] Train both models in Colab (notebooks 01 + 02) and download `best.pt` files.
- [ ] Run `python src/evaluate.py` and write the numbers into the PPT
      results slide — the slide in this repo has a blank table for
      exactly those numbers. Do not present another paper's metrics.
- [ ] Test the app with **one validation image** (never a training
      image) and one clean/healthy image. Know what each one does.
- [ ] Have a backup: the same validation images on a USB / laptop,
      and `notebooks/03_demo_colab.ipynb` ready in Colab.
- [ ] Charge the laptop, and have the GitHub repo link open in a tab.

## 1. The problem (30 seconds)
"Visual corrosion inspection is slow, subjective, and hard to repeat
across inspectors. This project screens a photo, locates corrosion,
and — only when asked — estimates type and severity in a
standards-based format."

## 2. Quick mode (1 minute)
Upload a validation image. Show: verdict, boxes, confidences.
Say: "Quick mode answers one question: corrosion or not, and where.
No corrosion detected means no box passed the threshold in this
image — not a guarantee the asset is clean."

## 3. Dive Deeper toggle (1.5 minutes)
Turn the toggle on, re-analyse the same image. Show:
- Type (top-2, with probabilities) — "appearance only, indicative,
  not a metallurgical diagnosis."
- Severity % — "rust pixels inside the boxes, not box area."
- ASTM D610 grade + distribution — "grade from the D610 table,
  distribution is our heuristic, labelled as such."
- Download the PDF — open it, point to the disclaimer on page 1.

## 4. Results (1 minute) — fill these in after training
- Detection: mAP50, mAP50-95, precision, recall (test split).
- Classification: top-1 / top-5 accuracy (test split).
- Say the split sizes and the dataset limits out loud: detection
  dataset is only 268 ship-cabin images; the classifier dataset is
  marine, 300/class subsample in Colab. Generalisation to a new
  asset type is untested until tested on that asset.

## 5. Limits + next steps (1 minute)
- Boxes overestimate area — that is why severity uses rust pixels,
  and box % is reported separately as an upper bound.
- No thickness, no rate, no subsurface corrosion from a photo.
- Next steps: larger, asset-specific dataset; segmentation instead
  of boxes for a truer area %; calibration of the rust-pixel
  threshold against hand-labelled masks.

## If something fails live
- App has no weights → show the Colab notebook training output and
  the code, and say the weights step is pending. Do not run a COCO
  model and pretend it detects corrosion.
- Wrong prediction on a demo image → that is a result, not a
  disaster. Show the confidence, the box, and say what the failure
  mode tells you about the dataset (domain shift, lighting, scale).
  Professors respect a student who can explain a failure.
