"""Corrosion Vision — Streamlit frontend.

Run locally:  streamlit run app/app.py
Hosted:       push this repo to GitHub, then connect it on Streamlit
              Community Cloud (see docs/HOSTING.md). No weights are
              committed to GitHub by default — upload best.pt via the
              Streamlit Cloud file / secrets flow, or point the sidebar
              paths at a hosted weights URL your team controls.

The app never invents a result: if weights are missing it stops with
the exact training step, instead of running a COCO model.
"""
import sys, tempfile, os
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.inference import load_yolo, predict, DETECT_DEFAULT, CLASSIFY_DEFAULT
from src.pdf_report import build_pdf

st.set_page_config(page_title="Corrosion Vision", page_icon="🔩", layout="wide")
st.title("🔩 Corrosion Vision — steel infrastructure inspection screening")
st.caption("Shubhang S. Galagali, 231MT049 · Metallurgical and Materials Engineering, NITK Surathkal · "
           "YOLO26 detection + classification · Visual screening only, not a certified inspection.")

with st.sidebar:
    st.header("Model")
    detect_path = st.text_input("Detector weights", DETECT_DEFAULT)
    classify_path = st.text_input("Classifier weights (Dive Deeper)", CLASSIFY_DEFAULT)
    conf = st.slider("Confidence threshold", 0.05, 0.95, 0.25, 0.05)
    dive = st.toggle("🔍 Dive Deeper — type + severity %", value=False,
                     help="Runs the type classifier and the ASTM D610 severity estimate. "
                          "Off = Quick mode only: corrosion vs no corrosion.")
    st.header("Inspection record (for the PDF)")
    asset = st.text_input("Asset / location", "")
    notes = st.text_area("Inspector notes", "")

uploaded = st.file_uploader("Upload a steel-surface photo (JPG/PNG)", type=["jpg", "jpeg", "png"])
if uploaded is None:
    st.info("Upload a photo to begin. For the demo, use a validation image from "
            "data/yolo_detect/test/images — never a training image.")
    st.stop()

pil = Image.open(uploaded).convert("RGB")
img_rgb = np.array(pil)
img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

try:
    detect_model = load_yolo(detect_path, "detection (notebooks/01)")
except FileNotFoundError as e:
    st.error(str(e)); st.stop()

classify_model = None
if dive:
    try:
        classify_model = load_yolo(classify_path, "classification (notebooks/02)")
    except FileNotFoundError as e:
        st.error(str(e)); st.stop()

if st.button("Analyse image", type="primary"):
    with st.spinner("Running YOLO…"):
        result = predict(img_bgr, detect_model, classify_model,
                         dive_deeper=dive, conf=conf)
    if result.verdict == "Corrosion detected":
        st.success(f"## ✅ {result.verdict}  ({len(result.detections)} box(es))")
    else:
        st.warning(f"## {result.verdict}\nNo box passed the {conf:.2f} confidence threshold in this image. "
                   "That is not a guarantee the asset is corrosion-free.")
    ann_rgb = cv2.cvtColor(result.annotated_bgr, cv2.COLOR_BGR2RGB)
    st.image(ann_rgb, caption="Annotated image", use_container_width=True)
    if result.detections:
        st.table([{"#": i + 1, "Box (px)": f"({int(d.x1)}, {int(d.y1)}) – ({int(d.x2)}, {int(d.y2)})",
                   "Confidence": round(d.conf, 3)} for i, d in enumerate(result.detections)])
    if dive and result.severity is not None:
        s = result.severity
        st.subheader("🔍 Dive Deeper — severity")
        c1, c2, c3 = st.columns(3)
        c1.metric("Severity % (rust pixels)", f"{s['severity_pct']}%")
        c2.metric("ASTM D610 grade", str(s["astm_d610_grade"]))
        c3.metric("Box-area % (upper bound)", f"{s['box_area_pct']}%")
        st.write(f"**Distribution (heuristic):** {s['distribution']}")
        st.write(f"**Recommendation band (project, not a code):** {s['recommendation']}")
        st.caption(s["method_note"])
    if dive and result.type_prediction:
        st.subheader("🔍 Dive Deeper — corrosion type (appearance only)")
        for label, prob in result.type_prediction:
            st.write(f"- **{label}**: {prob:.1%}")
        st.caption("Type from a photograph alone is indicative, not a metallurgical diagnosis.")
    # PDF
    with tempfile.TemporaryDirectory() as td:
        ann_path = os.path.join(td, "annotated.jpg")
        cv2.imwrite(ann_path, result.annotated_bgr)
        pdf_path = os.path.join(td, "corrosion_report.pdf")
        build_pdf(pdf_path, result, ann_path, {
            "filename": uploaded.name, "asset": asset, "notes": notes,
            "detect_model": detect_path, "classify_model": classify_path, "conf": conf})
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download PDF report (ASTM D610 basis)",
                               data=f.read(), file_name="corrosion_report.pdf",
                               mime="application/pdf")
    st.caption("Visual screening only. Confirm any formal finding with a qualified inspector, "
               "thickness measurement and the applicable code. See docs/STANDARDS.md.")
