# FreightDoc — MASTER DOCUMENT
OpenAI Build Week | Track: Work & Productivity

## 1. WHAT THIS PROJECT IS
FreightDoc is an agentic export-documentation generator. A user describes a
product in plain English, picks an origin/destination country pair, and the
system:
1. Classifies the correct HS (Harmonized System) code
2. Pulls live tariff/duty data
3. Determines which documents are legally required for that trade corridor
4. Generates all documents as structured data
5. Cross-validates every document against every other document for errors
6. Renders everything as downloadable PDFs

The single differentiator vs. every other "AI document generator" demo:
**Step 5, the cross-validator, is the product.** Anyone can generate a
commercial invoice with an LLM. Nobody else catches "your invoice says 500
units but your packing list says 480" or "you're shipping electronics to
Germany and have no CE Declaration" before the shipment leaves the warehouse.

## 2. WHY THIS PROJECT, WHY NOW
- $1.47T in cross-border e-commerce (2025) with tens of thousands of small
  exporters filling out customs paperwork manually or paying $500–$2,000/shipment
  to freight forwarders.
- HS classification requires specialized training; getting it wrong causes
  duty underpayment (illegal) or overpayment (wasted money).
- A single missing document (e.g., CE Declaration for electronics into the EU)
  can hold a shipment at the border for a week and trigger fines >$10,000.
- GPT-5.6-class models can now read a plain-English product description and
  output a defensible HS code + generate multi-document packages in one pass —
  this was not reliably possible at hackathon speed 18 months ago.

## 3. MODELS TO USE
| Task | Model | Why |
|---|---|---|
| Codex build sessions (writing the actual code) | **GPT-5.6 Terra** | Cheapest capable coding model; default for all Codex sessions |
| HS code classification (runtime) | **GPT-5.6 Luna** | Fast, cheap, structured JSON output |
| Document generation (runtime) | **GPT-5.6 Luna** | Same |
| Cross-validation (runtime) | **GPT-5.6 Luna** | Same |
| Any genuinely hard architecture decision during build | GPT-5.6 Sol (sparingly) | Reserve for stuck moments only |

Never call a model for something a rule engine or a free public API can do.
The tariff lookup, document-requirements matrix, and PDF rendering are **all
deterministic code, zero AI cost.**

## 4. FULL TECH STACK
- **Backend:** Python 3.11 + FastAPI, deployed on Railway (free tier)
- **Frontend:** React + Vite + Tailwind CSS, deployed on Vercel (free tier)
- **PWA:** vite-plugin-pwa (installable, offline shell)
- **PDF rendering:** ReportLab (pure Python, no external service, free)
- **State:** Stateless per request for MVP — no database required
- **AI:** OpenAI API (GPT-5.6 Luna runtime / Terra for Codex builds)
- **External data (all free):**
  - USITC HTS REST API — HS code + US duty rate lookup
  - UN Comtrade API — bilateral tariff data (free tier, needs a registration key)
  - EU TARIC — EU-specific duty/compliance flags
  - REST Countries API — country metadata, no auth

## 5. SETUP FROM SCRATCH
```bash
# 1. Clone/scaffold
mkdir freightdoc && cd freightdoc
mkdir backend frontend

# 2. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn openai httpx reportlab pydantic python-dotenv
touch main.py .env
echo "OPENAI_API_KEY=sk-..." >> .env

# 3. Frontend
cd ../frontend
npm create vite@latest . -- --template react
npm install
npm install -D tailwindcss postcss autoprefixer vite-plugin-pwa
npx tailwindcss init -p

# 4. Run locally
# terminal 1:
cd backend && uvicorn main:app --reload
# terminal 2:
cd frontend && npm run dev
```

## 6. HOW TO USE CODEX (STEP BY STEP)
1. Open Codex (in ChatGPT or via CLI) on the account holding your credits.
2. Start a **single persistent session** — do not open a fresh session per
   feature; you want one long build thread so your `/feedback` Session ID
   tells one coherent story.
3. Paste the seed prompt (see Doc 6, Technical Architecture) to scaffold the
   backend first.
4. Iterate feature by feature: classify → tariff → doc-requirements →
   generate → validate → PDF → frontend.
5. Before closing the session, always run `/feedback` and copy the returned
   Session ID into your README.

## 7. THE 8 LAUNCH TRADE CORRIDORS
US↔Germany, US↔UK, US↔India, US↔Japan, US↔Canada, US↔Australia,
India↔US, China↔EU.

## 8. BUDGET
Total credits: 2,500. FreightDoc build (Terra): ~400. FreightDoc runtime
testing (Luna): ~100. This leaves enormous headroom — do not micro-optimize
token usage during the hackathon, optimize for shipping.

## 9. POST-HACKATHON COST-DOWN PATH (if turned into a SaaS)
- Move HS classification + document generation to GPT-5.6-mini-tier or an
  open model (Llama 3.3 70B via Groq, free/cheap) once volume grows.
- Keep the cross-validator on a stronger model since that's the trust-critical
  step — errors here have real financial consequences.
- Move the tariff/requirements lookup fully into your own maintained JSON/DB
  — it already is; no change needed.
- Cache repeated HS classifications (same product description => same code)
  in Redis or even a dict for near-zero repeat cost.

## 10. DOCUMENT MAP (this repo's specs)
01_PROBLEM.md · 02_COMPETITIVE_ANALYSIS.md · 03_WHY_NOW.md ·
04_JUDGE_APPEAL.md · 05_DEMO_SCRIPT.md · 06_TECHNICAL_ARCHITECTURE.md ·
07_HACKATHON_FIT.md · 08_STARTUP_POTENTIAL.md · 09_RISKS.md ·
10_API_REFERENCE.md
