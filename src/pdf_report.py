"""
PDF inspection report (ReportLab, no paid tools needed).

The PDF is a screening record, not a certified inspection report.
Every PDF carries the disclaimer on its first page, plus the method
note from severity.py, so a reader cannot mistake a box-area % for a
thickness measurement or a D610 grade for a repair instruction.
"""
from __future__ import annotations
import os
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle, Image as RLImage)


def _kv_table(rows):
    t = Table([[Paragraph(f"<b>{k}</b>", getSampleStyleSheet()["Normal"]),
                Paragraph(str(v), getSampleStyleSheet()["Normal"])] for k, v in rows],
              colWidths=[55 * mm, 110 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDE7F6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build_pdf(output_path: str, result, image_path: str, meta: dict) -> str:
    """result: src.inference.Result. image_path: annotated image on disk."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            topMargin=18 * mm, bottomMargin=18 * mm,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            title="Corrosion Vision — Inspection Screening Report",
                            author="Corrosion Vision (NITK Surathkal project)")
    story = []
    story.append(Paragraph("Corrosion Vision — Inspection Screening Report", styles["Title"]))
    story.append(Paragraph(
        "Visual screening only. This is not a certified inspection, not a "
        "thickness measurement, and not a repair instruction. A real asset "
        "decision needs a qualified inspector and the applicable code.",
        styles["Normal"]))
    story.append(Spacer(1, 4 * mm))
    story.append(_kv_table([
        ("Date (UTC)", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")),
        ("Image file", meta.get("filename", "—")),
        ("Asset / location", meta.get("asset", "—")),
        ("Inspector / notes", meta.get("notes", "—")),
        ("Detector model", meta.get("detect_model", "models/detect/best.pt")),
        ("Classifier model", meta.get("classify_model", "models/classify/best.pt (Dive Deeper only)")),
        ("Confidence threshold", meta.get("conf", 0.25)),
        ("Verdict", f"<b>{result.verdict}</b>"),
        ("Detections", len(result.detections)),
    ]))
    story.append(Spacer(1, 4 * mm))
    if image_path and os.path.exists(image_path):
        story.append(RLImage(image_path, width=150 * mm, height=110 * mm))
        story.append(Paragraph("Annotated image: red boxes = detected corrosion, with confidence.", styles["Normal"]))
    if result.detections:
        rows = [["#", "Box (px)", "Confidence"]]
        for i, d in enumerate(result.detections, 1):
            rows.append([str(i), f"({int(d.x1)}, {int(d.y1)}) – ({int(d.x2)}, {int(d.y2)})", f"{d.conf:.2f}"])
        t = Table(rows, colWidths=[12 * mm, 95 * mm, 35 * mm])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDE7F6")),
                               ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
        story.append(Spacer(1, 3 * mm)); story.append(t)
    if result.severity is not None:
        s = result.severity
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("Dive Deeper — severity (ASTM D610 basis, see method note)", styles["Heading2"]))
        story.append(_kv_table([
            ("Severity % (rust pixels in boxes)", f"{s['severity_pct']}%"),
            ("Box-area % (upper-bound coverage)", f"{s['box_area_pct']}%"),
            ("ASTM D610 rust grade", str(s["astm_d610_grade"])),
            ("Distribution (heuristic)", s["distribution"]),
            ("Recommendation band (project)", s["recommendation"]),
            ("Method note", s["method_note"]),
        ]))
    if result.type_prediction:
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("Dive Deeper — corrosion type (appearance only, indicative)", styles["Heading2"]))
        for label, prob in result.type_prediction:
            story.append(Paragraph(f"• {label}: {prob:.1%}", styles["Normal"]))
        story.append(Paragraph(
            "Type from a photograph alone cannot diagnose a corrosion "
            "mechanism. Confirm with microscopy, environment history and, "
            "where relevant, metallography before naming a mechanism in a "
            "formal report.", styles["Normal"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Standards referenced: ASTM D610 (SSPC-VIS 2), Standard Practice for "
        "Evaluating Degree of Rusting on Painted Steel Surfaces — 0–10 grade "
        "from % surface rusted. ISO 8501-1 rust grades A–D describe the "
        "pre-treatment condition of uncoated steel and are not derived from "
        "a percentage in this report. AMPP (formerly NACE + SSPC) inspection "
        "records are a format reference here, not a certification claim. "
        "See docs/STANDARDS.md for the full table and limits.", styles["Normal"]))
    doc.build(story)
    return output_path
