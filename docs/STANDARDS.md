# Standards used — and, just as important, what is NOT claimed

## ASTM D610 (SSPC-VIS 2) — used, with its table reproduced
**Title:** Standard Practice for Evaluating Degree of Rusting on Painted Steel Surfaces.
**Method in brief:** Select an area, determine the rust distribution type,
estimate the % of surface area rusted (by visual comparison to the
standard's pictorial examples, or by an agreed electronic-scanning
method), then read the grade from Table 1. Report grade + distribution,
e.g. "5-G".

**Table 1 (D610) — % surface rusted → grade:**
| Grade | % rusted |
|---|---|
| 10 | ≤ 0.01 |
| 9 | > 0.01 – 0.03 |
| 8 | > 0.03 – 0.10 |
| 7 | > 0.10 – 0.30 |
| 6 | > 0.30 – 1.0 |
| 5 | > 1.0 – 3.0 |
| 4 | > 3.0 – 10.0 |
| 3 | > 10.0 – 16.0 |
| 2 | > 16.0 – 33.0 |
| 1 | > 33.0 – 50.0 |
| 0 | > 50 |

**Distribution letters (D610):** S = spot (rust concentrated in a few
localised areas), G = general (spots randomly distributed), P = pinpoint
(very small individual specks), H = hybrid (mixed pattern).

**How this project uses it:** the PDF reports a D610 grade computed from
the rust-pixel % via the table above. That is an *electronic-scanning-style*
estimate, not a visual comparison to the pictorial standards, and the
PDF says so. Distribution in this project is a box-geometry heuristic
(see `src/severity.py`), not a D610 visual comparison — the PDF labels
it "(heuristic)" for that reason.

## ISO 8501-1 — referenced, NOT derived from a percentage
**Title:** Preparation of steel substrates before application of paints
and related products — Visual assessment of surface cleanliness.
**Rust grades (uncoated steel, before preparation):**
- A: largely covered with adhering mill scale, little if any rust.
- B: begun to rust, mill scale begun to flake.
- C: mill scale rusted away or scrapable, slight pitting visible.
- D: mill scale rusted away, general pitting visible.
These describe mill scale + pitting visibility, not a rust %. This
project therefore does **not** output an ISO 8501-1 grade from a photo's
rust %. If a formal report needs an ISO grade, a human inspector must
assign it by comparison to the standard's pictorial references.

## AMPP (formerly NACE + SSPC) — format reference only
AMPP coating-inspection records, API 510/570/653 inspection programmes
and bridge-inspection records are the *format* this PDF is modelled on:
timestamped, image-backed, per-asset findings with severity and location.
This project is **not** AMPP-certified, does not claim an AMPP inspector
qualification, and does not replace API/NACE/AMPP inspection intervals
or acceptance criteria. Those are owned by the asset's integrity team.

## What this system cannot measure (say this in the demo)
- Metal loss / remaining thickness (needs UT, not a photo).
- Corrosion rate in mm/year (needs time series + environment).
- Subsurface, under-insulation or internal corrosion (needs NDT).
- A corrosion mechanism with certainty (needs microscopy/history).
A photo can screen and prioritise. It cannot certify.
