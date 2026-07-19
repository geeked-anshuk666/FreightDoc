# FreightDoc — 06_TECHNICAL_ARCHITECTURE.md

## Full pipeline
User Input
│
▼
[1] Product Classifier (GPT-5.6 Luna)
Input: product name + description
Output: {hs_code, hs_description, confidence, category, notes}
│
▼
[2] Tariff Retrieval (API calls, zero AI cost)
USITC HTS API → US duty rate
UN Comtrade → bilateral tariff for the country pair
EU TARIC → EU-specific duty/compliance if destination is in EU
│
▼
[3] Document Requirements Engine (rule-based JSON lookup, zero AI cost)
Always: commercial invoice, packing list, certificate of origin
Conditional: CE declaration (electronics→EU), phytosanitary (food/plants),
CITES permit (wildlife), dangerous goods declaration
│
▼
[4] Document Generator (GPT-5.6 Luna, structured JSON output)
Single call generates all required documents as structured fields
│
▼
[5] Cross-Validator (GPT-5.6 Luna)
Checks: HS code consistency, value/quantity mismatches, missing fields,
destination-specific compliance gaps, origin consistency
Output: {errors[], compliance_score, ready_to_ship}
│
▼
[6] PDF Renderer (ReportLab, zero AI cost)
Each document → styled PDF
│
▼
Frontend: tabbed viewer, red/amber error panels, download-all ZIP

## Backend structure
freightdoc-backend/
├── main.py
├── routers/
│   ├── classify.py
│   ├── generate.py
│   ├── validate.py
│   └── health.py
├── services/
│   ├── openai_client.py
│   ├── hts_api.py
│   ├── tariff_api.py
│   ├── doc_engine.py
│   └── pdf_generator.py
├── models/
│   ├── shipment.py
│   └── documents.py
├── data/
│   └── country_rules.json
├── requirements.txt
└── Dockerfile

## Key endpoints
POST /api/classify          Step 1 only
POST /api/generate          Steps 2-4
POST /api/validate          Step 5
POST /api/full-pipeline     All steps in sequence — use this for the demo
GET  /api/country-pairs     List supported corridors
GET  /health

## Frontend structure
freightdoc-frontend/
├── src/
│   ├── App.jsx
│   ├── components/
│   │   ├── ShipmentForm.jsx
│   │   ├── PipelineProgress.jsx
│   │   ├── DocumentTabs.jsx
│   │   ├── ErrorPanel.jsx
│   │   ├── WarningPanel.jsx
│   │   └── DownloadBar.jsx
│   ├── hooks/useFreightPipeline.js
│   └── utils/countryList.js
├── public/manifest.json, icons/
└── vite.config.js  (includes vite-plugin-pwa)

## Codex seed prompt
I am building FreightDoc for the OpenAI Build Week hackathon. Deadline
July 21. I am solo. Use GPT-5.6 Luna for all runtime API calls.
FreightDoc is an agentic export documentation tool. Pipeline:

Classify HS code via GPT-5.6 Luna
Pull tariff rates from USITC HTS API and UN Comtrade API
Determine required documents via a rule-based engine (JSON config)
Generate all documents via GPT-5.6 Luna (structured JSON output)
Cross-validate all documents via GPT-5.6 Luna
Render PDFs via ReportLab

Backend: Python + FastAPI. Frontend: React + Vite + Tailwind +
vite-plugin-pwa. Deploy: Railway (backend) + Vercel (frontend).
Scaffold the complete FastAPI backend first: routes, services, Pydantic
models. Use the OpenAI Python SDK v1.x, model="gpt-5.6-luna", structured
JSON outputs, proper error handling, CORS enabled for the frontend.
Country rules for document requirements live in a JSON config file.
Support 8 corridors at launch: US→Germany, US→UK, US→India, US→Japan,
US→Canada, US→Australia, India→US, China→EU.
Build POST /api/full-pipeline first — it runs all 6 steps in sequence.
