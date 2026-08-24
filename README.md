# Flash Flood & Landslide Early Warning — Phase 1 MVP

A working implementation of **Phase 1** from the NDRF/MHA-style build spec
this was built against: *"Rainfall + historical inventory + DEM-derived
slope angle → threshold-based risk score per village → alert on breach."*
Built with free, no-API-key data sources end to end.

**This is a decision-support prototype, not a validated operational
system.** See "What this is and isn't" below before using it for anything
beyond a demo/hackathon submission.

## Free data sources used (all free, no signup, no API key)

| Signal | Source | Endpoint |
|---|---|---|
| Rainfall (3h/24h forecast) | Open-Meteo Forecast API | `api.open-meteo.com/v1/forecast` |
| Soil moisture (3 depths) | Open-Meteo Forecast API (same call) | same endpoint |
| Slope angle | Open-Meteo Elevation API (5-point sample, derived gradient) | `api.open-meteo.com/v1/elevation` |
| River discharge (regional context) | Open-Meteo Flood API (GloFAS) | `flood-api.open-meteo.com/v1/flood` |
| Historical landslide frequency | Your own village registry (`data/villages.json`) | — |

No IMD, GSI, or Bhuvan account needed to run this — those are the *better*
sources for production (see roadmap below) but aren't simple free public
APIs the way Open-Meteo's are.

## 1. Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000` — you'll see all sample villages showing "No
data yet". Click **"Refresh risk for all villages"** to pull live data and
compute risk scores.

## 2. Running the daily/hourly automated refresh

```bash
python3 scripts/recompute_risk.py
```

Set this up on a cron schedule (every 30-60 min during monsoon season is
reasonable given how fast conditions change):

```
*/30 * * * * /path/to/venv/bin/python3 /path/to/flood-prediction-mvp/scripts/recompute_risk.py >> /path/to/logs/recompute.log 2>&1
```

## 3. Adding real villages

Edit `data/villages.json`. Each entry needs `id`, `name`, `block`,
`district`, `state`, `latitude`, `longitude`, and the historical fields.

**Important**: the seed data's `historical_landslide_events` and
`historical_severity` fields are placeholder numbers for demoing the risk
engine — they are not verified disaster records. Replace them with real
figures from the [GSI Bhukosh landslide inventory](https://bhukosh.gsi.gov.in/),
your state Disaster Management Authority, or NDRF deployment records
before using this for anything beyond a demo.

## 4. How the risk engine works

`app/risk_engine.py` fuses four signals into a 0-1 score:

- **Rainfall** (35% weight) — 3-hour cumulative rainfall, piecewise-scaled against rough IMD heavy-rain intensity bands
- **Soil moisture** (25%) — averaged across 3 depth layers, normalized against typical saturation (~0.45 m³/m³)
- **Slope angle** (20%) — from the elevation-sampling gradient, normalized against 45°
- **Historical frequency** (20%) — from your village registry's recorded events + severity

Score maps to status: **Safe** (<0.30) → **Watch** (0.30-0.50) → **Warning**
(0.50-0.70) → **Evacuate** (≥0.70). Per the spec's instruction to
prioritize recall over precision for Evacuate-level alerts, these
thresholds sit on the sensitive side.

**None of these weights or thresholds are calibrated against real
outcomes.** They're a reasonable starting point for a rule-based Phase 1
model, exactly as the spec describes — not a trained or validated model.
Before this informs any real decision, a hydrologist/geotechnical
engineer/DDMA needs to review and tune them against actual historical
events for your specific villages.

**If a data source is unavailable** (network failure, API down), the
engine does NOT default to "Safe" — it explicitly returns "Unknown — no
live data available" when no live signal (rainfall/soil/slope) is
available, even if historical data exists. A missing live reading and a
calm live reading are never conflated. This was actually caught and fixed
during testing — worth knowing since it's the kind of bug that's easy to
introduce again if the engine gets modified later.

## 5. What this is and isn't (read before any real use)

- ✅ Proves the full pipeline: multi-source data → fused score → village-level status → dashboard
- ✅ Handles partial/total data-source failure without false confidence
- ❌ **Not connected to real IoT sensors** — Phase 2 in the original spec
- ❌ **Not validated against real landslide/flood outcomes** — the weights and thresholds are reasonable-looking placeholders, not a trained model
- ❌ **No SMS/IVR/siren alerting** — Phase 3 in the original spec
- ❌ **Slope angle is a coarse 90m-DEM proxy** (5-point elevation sample), not a proper GIS slope raster from Cartosat/SRTM
- ❌ **River discharge is shown as regional context only**, not blended into the local score — GloFAS's 5km resolution is too coarse to represent small hill catchments reliably

## 6. Roadmap toward the full spec

- **Phase 2**: Wire in real IoT soil-moisture/tilt sensor feeds (replace/augment the Open-Meteo soil moisture proxy); add river/stream gauge data for the catchments that actually matter locally
- **Phase 3**: Sensor health monitoring panel, tiered multi-channel alerting (SMS/IVR via Twilio or a local gateway, panchayat loudspeaker relay hooks), offline-first PWA for field responders, NDRF/DDMA command view
- **Phase 4**: Feedback loop logging each alert's real-world outcome (false alarm / confirmed event), then retraining the fusion model (scikit-learn/PyTorch) on accumulated historical + outcome data instead of the current fixed rule-based weights

## 7. Project structure

```
app/
  main.py           → FastAPI routes (dashboard, detail, refresh, JSON API)
  data_sources.py    → Open-Meteo API wrappers (rainfall, soil moisture, slope, river discharge)
  risk_engine.py       → fusion logic — the core of this MVP
  refresh.py             → shared refresh routine (used by both the API and the cron script)
  db.py                    → SQLite storage for cached risk snapshots
templates/                   → dashboard.html, village_detail.html (Jinja2)
static/style.css               → command-center dashboard styling, system fonts only
  (no external font/CDN loading — deliberate, since the spec calls out
  low-bandwidth, intermittent-connectivity as the dominant failure mode
  in hilly regions during storms)
scripts/recompute_risk.py         → cron entrypoint
data/villages.json                  → village registry (edit this)
data/app.db                          → SQLite cache, created on first run
```

## 8. Testing note

All core logic was tested before delivery: the risk engine against 6
scenarios (calm/extreme/moderate conditions, total data-source failure,
partial failure, and history-only data — which caught the false-"Safe"
bug described above), and the full HTTP pipeline against both real network
failures (Open-Meteo wasn't reachable from the build sandbox — a real test
of the failure path) and mocked live data (proving the happy path renders
correctly end to end, including status sorting and the color-coded
dashboard).
