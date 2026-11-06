from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation(); prs.slide_width = Inches(13.33); prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
WHITE = RGBColor(0xFF, 0xFF, 0xFF); BLACK = RGBColor(0, 0, 0)
PURPLE = RGBColor(0x5B, 0x2C, 0x8E); BLUE = RGBColor(0x1F, 0x4E, 0x9E)
GREY = RGBColor(0x55, 0x55, 0x55); LGREY = RGBColor(0xE8, 0xE8, 0xE8); RED = RGBColor(0xC0, 0x39, 0x2B)


def bg(s):
    s.background.fill.solid(); s.background.fill.fore_color.rgb = WHITE


def tb(s, l, t, w, h, text, size=28, bold=True, color=BLACK, align=PP_ALIGN.LEFT):
    tx = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h)).text_frame
    tx.word_wrap = True; p = tx.paragraphs[0]; p.text = text
    p.font.size = Pt(size); p.font.bold = bold; p.font.color.rgb = color; p.alignment = align
    return tx


def bullets(s, l, t, w, h, items, size=19):
    tx = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h)).text_frame; tx.word_wrap = True
    for i, (pre, txt) in enumerate(items):
        p = tx.paragraphs[0] if i == 0 else tx.add_paragraph()
        p.space_after = Pt(10)
        if pre:
            r = p.add_run(); r.text = pre; r.font.bold = True; r.font.size = Pt(size)
            r2 = p.add_run(); r2.text = txt; r2.font.size = Pt(size)
        else:
            p.text = "•  " + txt; p.font.size = Pt(size)
    return tx


def header(s, title):
    bg(s); tb(s, 0.6, 0.35, 12.1, 0.9, title, size=32)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.25), Inches(1.6), Inches(0.07))
    bar.fill.solid(); bar.fill.fore_color.rgb = PURPLE; bar.line.fill.background()
    tb(s, 9.0, 7.05, 3.7, 0.3, "Corrosion Vision  •  Shubhang S. Galagali, 231MT049", size=9, bold=False, color=GREY, align=PP_ALIGN.RIGHT)


def table(s, l, t, rows, colw):
    sh = s.shapes.add_table(len(rows), len(rows[0]), Inches(l), Inches(t), Inches(sum(colw)), Inches(0.4 * len(rows)))
    tbl = sh.table
    for j, w in enumerate(colw): tbl.columns[j].width = Inches(w)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = tbl.cell(i, j); c.text = str(v); c.fill.solid(); c.fill.fore_color.rgb = LGREY if i == 0 else WHITE
            for p in c.text_frame.paragraphs:
                p.font.size = Pt(13 if i else 14); p.font.bold = (i == 0)
    return sh


def note(s, text):
    tb(s, 0.6, 6.55, 12.1, 0.4, text, size=11, bold=False, color=GREY)


# 1 Title
s = prs.slides.add_slide(BLANK); bg(s)
tb(s, 0.5, 0.4, 12.3, 0.4, "National Institute of Technology Karnataka, Surathkal  •  Metallurgical and Materials Engineering", size=13, bold=False, color=GREY, align=PP_ALIGN.CENTER)
tb(s, 0.5, 1.2, 12.3, 1.2, "Corrosion Vision", size=48, align=PP_ALIGN.CENTER)
tb(s, 0.5, 2.3, 12.3, 0.7, "YOLO26 detection + Dive Deeper severity for steel infrastructure", size=24, bold=False, align=PP_ALIGN.CENTER)
tb(s, 0.5, 3.3, 12.3, 0.5, "Shubhang S. Galagali, 231MT049", size=22, align=PP_ALIGN.CENTER)
tb(s, 0.5, 3.8, 12.3, 0.4, "shubgalagali.231mt049@nitk.edu.in", size=16, bold=False, color=BLUE, align=PP_ALIGN.CENTER)
tb(s, 0.5, 4.8, 12.3, 0.6, "Live demo + code repo  •  Quick mode: corrosion vs no corrosion  •  Dive Deeper: type + severity % + PDF", size=17, bold=False, align=PP_ALIGN.CENTER)
tb(s, 0.5, 6.2, 12.3, 0.5, "Visual screening only — not a certified inspection. See the limitations slide.", size=13, bold=False, color=RED, align=PP_ALIGN.CENTER)

# 2 Problem
s = prs.slides.add_slide(BLANK); header(s, "The problem: inspection is slow and subjective")
bullets(s, 0.6, 1.6, 12.1, 5.0, [
    ("Visual inspection varies by inspector, light and fatigue. ", "Two inspectors can grade the same bridge or pipeline section differently, and there is no repeatable record to compare next year."),
    ("Pipelines, bridges, tanks and marine steel all corrode the same way in a photo: ", "brown, rough, localised patches — but the photo alone cannot tell you thickness, rate, or what is happening under a coating."),
    ("This project does one job well: ", "screen a photo, locate corrosion, and — only when asked — estimate type and severity in a standards-based format, with a PDF record."),
    ("It does not claim: ", "a thickness measurement, a corrosion rate, a certified inspection, or a repair instruction. Those need instruments and a qualified inspector."),
], size=20)

# 3 Datasets
s = prs.slides.add_slide(BLANK); header(s, "Datasets: two Kaggle sets, two different jobs")
table(s, 0.6, 1.6, [["Dataset (Kaggle)", "Size / licence", "Job in this project"],
                     ["wednesday233 / corrosion-detect-dataset", "268 images, YOLO labels, MIT", "Detection: 1 class, corrosion"],
                     ["ebrahim007 / marine-corrosion-dataset", "9,000 images, 9 × 1,000, Apache 2.0", "Classification: 9 types (Dive Deeper)"]],
      [4.5, 3.5, 4.1])
bullets(s, 0.6, 3.6, 12.1, 2.9, [
    ("Why two? ", "A box dataset and a type dataset are different things. Pretending one model does both would be overselling."),
    ("Honest limit: ", "Detection data are ship-cabin images, not bridges/pipelines specifically, and only 268 of them. Test on your target asset before claiming it works there."),
    ("Colab default: ", "classifier trained on 300/class (2,700 images) first; full 9,000 only if disk/time allow."),
], size=18)
note(s, "Dataset pages verified 2026-11-05. Full download + licence notes: data/README.md in the repo.")

# 4 Architecture
s = prs.slides.add_slide(BLANK); header(s, "Architecture: two models, on purpose")
bullets(s, 0.6, 1.6, 12.1, 5.0, [
    ("Stage 1 — Detection: ", "YOLO26n fine-tuned, single class 'corrosion'. Output: boxes + confidences. Verdict: corrosion detected / no box passed the threshold."),
    ("Stage 2 — Dive Deeper (toggle only): ", "YOLO26-cls fine-tuned on 9 marine classes. Output: top-2 type with probabilities, run on the largest detected crop."),
    ("Severity (same toggle): ", "Rust-pixel % inside boxes (primary), box-area % as an upper-bound coverage only, ASTM D610 grade from the %, distribution heuristic, recommendation band."),
    ("Frontend: ", "Streamlit app (app/app.py) + Gradio demo in Colab (notebook 03). Both call the same src/inference.py — a fix in one is a fix in both."),
    ("Weights: ", "Trained in Colab, copied to models/detect/best.pt and models/classify/best.pt. Not committed to GitHub by default (see HOSTING.md)."),
], size=19)

# 5 YOLO choice
s = prs.slides.add_slide(BLANK); header(s, "Why YOLO26 — and what the fallback is")
bullets(s, 0.6, 1.6, 12.1, 5.0, [
    ("Latest, verified: ", "Ultralytics docs (checked 2026-11-05) state YOLO26, released January 2026, is the latest release and the recommended starting point for new projects."),
    ("Mature alternative: ", "YOLO11, for stable production workloads. This repo defaults to yolo26n / yolo26n-cls, with yolo11n / yolo11n-cls as the fallback in configs/config.yaml."),
    ("Why nano (n)? ", "Free Colab T4, fast demo inference, and a 268-image detection set does not justify a large model that will overfit it. Size is a choice, not a virtue."),
    ("Training: ", "Detection 50 epochs, 640 px, batch 16; classification 25 epochs, 224 px, batch 32. Seed 42, 70/15/15 splits, no image in two splits."),
], size=19)
note(s, "If your ultralytics install does not know yolo26n.pt, upgrade it or switch to the fallback — do not demo with a COCO model.")

# 6 Quick vs Dive Deeper
s = prs.slides.add_slide(BLANK); header(s, "Quick mode vs Dive Deeper — what the toggle actually does")
table(s, 0.6, 1.6, [["", "Quick (default)", "Dive Deeper (toggle)"],
                     ["Question", "Corrosion or not, and where?", "What type, and how severe?"],
                     ["Models", "Detection only", "Detection + classification"],
                     ["Output", "Boxes + confidences", "+ Type top-2, severity %, D610 grade, PDF"],
                     ["Risk if misread", "False negative = missed patch", "Type/severity treated as diagnosis"]],
      [2.2, 5.0, 5.0])
bullets(s, 0.6, 4.4, 12.1, 2.1, [
    ("Design rule: ", "Severity and type are never shown unless the user asks for them. A quick screen should stay quick."),
], size=18)

# 7 Severity standards
s = prs.slides.add_slide(BLANK); header(s, "Severity: ASTM D610, with the heuristic kept separate")
table(s, 0.6, 1.6, [["D610 grade", "% rusted", "D610 grade", "% rusted"],
                     ["10", "≤ 0.01", "5", "> 1 – 3"],
                     ["9", "> 0.01 – 0.03", "4", "> 3 – 10"],
                     ["8", "> 0.03 – 0.10", "3", "> 10 – 16"],
                     ["7", "> 0.10 – 0.30", "2", "> 16 – 33"],
                     ["6", "> 0.30 – 1.0", "1 / 0", "> 33 – 50 / > 50"]],
      [2.2, 3.0, 2.2, 3.0])
bullets(s, 7.2, 1.6, 5.5, 4.9, [
    ("From the standard: ", "Grade (0–10) from % surface rusted, plus distribution S/G/P/H (spot / general / pinpoint / hybrid)."),
    ("From this project: ", "Severity % = rust pixels inside boxes. Box % is an upper bound only — boxes overestimate a diagonal patch."),
    ("Not from a %: ", "ISO 8501-1 grades A–D (mill scale + pitting visibility). This project does not output them."),
    ("AMPP: ", "Format reference for the inspection record, not a certification claim."),
], size=16)
note(s, "Full table, method note and limits: docs/STANDARDS.md. Tests for the D610 boundaries: tests/test_severity.py.")

# 8 Frontend + hosting
s = prs.slides.add_slide(BLANK); header(s, "Frontend + hosting: GitHub is not the host")
bullets(s, 0.6, 1.6, 12.1, 5.0, [
    ("Frontend: ", "Streamlit app — upload, confidence slider, Dive Deeper toggle, annotated image, boxes table, PDF download. Same inference code as Colab."),
    ("GitHub: ", "Hosts the code (README, licences, notebooks, docs). You push it yourself — this repo is delivered as files, not pushed to any account."),
    ("Demo host: ", "Streamlit Community Cloud (app/app.py) or Hugging Face Spaces, connected to the GitHub repo. Weights are the catch — see HOSTING.md Step 2 before demo day."),
    ("Backup: ", "Colab Gradio notebook (03) + local run on the LOQ (streamlit run app/app.py). Venue Wi-Fi is the most common demo failure, not the model."),
], size=19)

# 9 Colab workflow
s = prs.slides.add_slide(BLANK); header(s, "Colab workflow: the exact steps")
bullets(s, 0.6, 1.6, 12.1, 5.0, [
    ("1. ", "Upload kaggle.json (never commit it) → bash scripts/download_datasets.sh"),
    ("2. ", "python src/prepare_detection.py  →  data/yolo_detect/ + data.yaml (70/15/15, seed 42)"),
    ("3. ", "python src/prepare_classifier.py --max-per-class 300  →  data/cls/"),
    ("4. ", "python src/train_detect.py (50 epochs)  •  python src/train_classify.py (25 epochs)"),
    ("5. ", "python src/evaluate.py  →  results/metrics.json  →  paste into the next slide"),
    ("6. ", "Copy best.pt files to models/ → streamlit run app/app.py → demo + PDF"),
], size=20)
note(s, "Notebooks 01/02/03 in the repo do exactly these steps in Colab, with no duplicated training logic.")

# 10 Results (blank, to fill)
s = prs.slides.add_slide(BLANK); header(s, "Results: fill this slide after your Colab run")
tb(s, 0.6, 1.5, 12.1, 0.5, "Do NOT copy metrics from another paper or dataset. These are the fields from results/metrics.json:", size=16, bold=False, color=RED)
table(s, 0.6, 2.1, [["Model (test split)", "Metric", "Value (fill in)"],
                     ["Detection (YOLO26n)", "mAP50 / mAP50-95", "— / —"],
                     ["Detection (YOLO26n)", "Precision / Recall", "— / —"],
                     ["Classification (YOLO26n-cls)", "Top-1 / Top-5 accuracy", "— / —"],
                     ["Splits", "Train / Val / Test", "Detection: — / — / —  •  Classifier: — / — / —"]],
      [4.5, 4.0, 3.6])
bullets(s, 0.6, 4.6, 12.1, 1.9, [
    ("How to fill it: ", "Run src/evaluate.py after notebooks 01 + 02, then type the numbers here. The demo script (docs/DEMO_SCRIPT.md) tells you what to say about them."),
], size=17)
note(s, "This slide is intentionally blank in the delivered deck. A blank, honest results slide beats an invented one in front of a professor.")

# 11 Limitations
s = prs.slides.add_slide(BLANK); header(s, "Limitations — say these before the examiner does")
bullets(s, 0.6, 1.6, 12.1, 5.0, [
    ("Small detection set: ", "268 ship-cabin images. Domain shift to bridges/pipelines is untested until tested on those assets."),
    ("Boxes overestimate area: ", "That is why severity uses rust pixels, and box % is labelled as an upper bound."),
    ("Type is indicative: ", "A photo cannot diagnose a corrosion mechanism. Microscopy, environment and history are needed for a formal mechanism name."),
    ("No thickness, no rate, no subsurface: ", "A photo cannot measure metal loss or what is under a coating or insulation."),
    ("No corrosion detected ≠ clean: ", "It means no box passed the threshold in that image, at that confidence, in that light."),
], size=19)

# 12 Demo flow
s = prs.slides.add_slide(BLANK); header(s, "Live demo: 5 minutes")
bullets(s, 0.6, 1.6, 12.1, 5.0, [
    ("0. Before: ", "Train, evaluate, test one validation + one healthy image, have a Colab/local backup ready."),
    ("1. Quick mode: ", "Upload a validation image → verdict, boxes, confidences. Never a training image."),
    ("2. Dive Deeper: ", "Toggle on → type top-2, severity %, D610 grade, distribution, PDF download. Open the PDF, point to the page-1 disclaimer."),
    ("3. Results: ", "Read the filled-in numbers from the previous slide, with split sizes and dataset limits."),
    ("4. If it fails: ", "Explain the failure mode (lighting, scale, domain shift). A student who can explain a failure is more convincing than a perfect demo."),
], size=19)

# 13 References
s = prs.slides.add_slide(BLANK); header(s, "References")
bullets(s, 0.6, 1.6, 12.1, 5.0, [
    ("[1] ", "Ultralytics, YOLO26 / YOLO11 documentation — latest release YOLO26 (Jan 2026), recommended for new projects; YOLO11 as mature alternative. docs.ultralytics.com/models"),
    ("[2] ", "Wednesday233, Corrosion Detect Dataset, Kaggle, MIT licence — 268 images, YOLO labels, ship cabins. kaggle.com/datasets/wednesday233/corrosion-detect-dataset"),
    ("[3] ", "Ebrahim007, Marine Corrosion Dataset, Kaggle, Apache 2.0 — 9,000 images, 9 classes. kaggle.com/datasets/ebrahim007/marine-corrosion-dataset"),
    ("[4] ", "ASTM D610 (SSPC-VIS 2), Standard Practice for Evaluating Degree of Rusting on Painted Steel Surfaces — 0–10 grade from % surface rusted."),
    ("[5] ", "ISO 8501-1, Preparation of steel substrates — Visual assessment of surface cleanliness — rust grades A–D (referenced, not derived from %)."),
    ("[6] ", "Project repo: Corrosion Vision — README, src/, notebooks/, docs/STANDARDS.md, docs/HOSTING.md, docs/DEMO_SCRIPT.md (this deck's source)."),
], size=16)
note(s, "Template: seminar deck style — white background, black headings, purple accents. No institute logos are reproduced.")

# 14 Thank you
s = prs.slides.add_slide(BLANK); bg(s)
tb(s, 0.5, 2.2, 12.3, 1.0, "Thank you", size=44, align=PP_ALIGN.CENTER)
tb(s, 0.5, 3.3, 12.3, 0.6, "Questions welcome — and a live demo beats a perfect slide.", size=20, bold=False, align=PP_ALIGN.CENTER)
tb(s, 0.5, 4.2, 12.3, 0.5, "Repo: github.com/<your-username>/corrosion-vision  •  App: see docs/HOSTING.md", size=15, bold=False, color=GREY, align=PP_ALIGN.CENTER)

prs.save("Corrosion_Vision_Demo.pptx")
print("slides:", len(prs.slides))
