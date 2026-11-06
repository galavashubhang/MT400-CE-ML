# Hosting — GitHub for code, Streamlit Cloud for the demo

GitHub does **not** run a Streamlit app by itself. The split below is
the standard, free, senior-project setup. You (the student) do the
upload — this repo is delivered as files, not pushed to any account,
because you said you will not connect GitHub here.

## Step 1 — Push the repo to GitHub (your machine, ~5 minutes)
```bash
cd corrosion-vision
git init
git add .
git commit -m "Corrosion Vision: YOLO26 detection + Dive Deeper severity"
git branch -M main
git remote add origin https://github.com/<your-username>/corrosion-vision.git
git push -u origin main
```
Check before pushing: `git status` must NOT show `kaggle.json`,
`data/raw/`, `data/yolo_detect/`, `data/cls/`, `runs/` or any `*.pt`
larger than GitHub's limit. `.gitignore` already excludes them.
If you want weights in the repo, use GitHub Releases (large files)
instead of committing them — see Step 2, option B.

## Step 2 — Host the app (choose one)

### Option A — Streamlit Community Cloud (recommended for the demo)
1. Go to https://share.streamlit.io (sign in with the same GitHub account).
2. New app → repository `corrosion-vision`, branch `main`, main file `app/app.py`.
3. Deploy. You get a public `https://<app>.streamlit.app` link.
4. Weights: Streamlit Cloud runs from the repo, so it cannot see
   `models/detect/best.pt` if you did not commit it. Two clean ways:
   - (a) Upload `best.pt` to a GitHub Release in the same repo, then
         set the sidebar weights path to that release URL is NOT
         supported by the app's file-path loader — instead, add a
         `models/` download step: in Streamlit Cloud, use an
         `app/download_weights.py` step, or simpler:
   - (b) For the class demo, run the app from your laptop (Step 3)
         and share your screen — the hosted link is for the code
         demo, not for live inference without weights.
   **Do this before demo day:** test the hosted link with a real
   validation image. A link that opens but has no weights is worse
   than no link.
5. If Streamlit Cloud asks for secrets, put nothing sensitive there
   for this project — there are no API keys in this app.

### Option B — Hugging Face Spaces (alternative, also free)
1. Create a Space → Streamlit SDK → connect the same GitHub repo
   (or upload the repo files directly in the Space).
2. Upload `models/detect/best.pt` and `models/classify/best.pt` to
   the Space (Files tab) — Spaces allow large files more easily
   than a git push.
3. Test with a validation image before sharing the link.

### Option C — Colab demo (no hosting, works offline-ish)
Use `notebooks/03_demo_colab.ipynb` (Gradio). It runs the same
`src/inference.py` code, with the weights you upload to Colab.
Good as a backup if the venue Wi-Fi fails and you have a local copy.

## Step 3 — Local demo (your LOQ, RTX 4050, as backup)
```bash
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
streamlit run app/app.py
```
Open the local URL it prints. This is the most reliable demo path:
no hosting, no Wi-Fi dependency, full GPU if available.

## What to put in the submission
- GitHub repo link (code, README, docs, notebooks).
- Hosted app link, if Step 2 worked with weights — otherwise state
  honestly: "Hosted code demo; live inference demoed locally in
  Colab / on laptop with trained weights."
- The PDF sample (generate one from a validation image after training
  and include it in the repo as `examples/sample_report.pdf` only if
  it is a real output, not a mock).
