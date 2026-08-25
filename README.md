# Geo Shield AI

Interactive hackathon MVP for simulated Himalayan flash-flood and landslide intelligence.

## What it does
- Automatically changes synthetic weather, river, soil and ground-motion data.
- Generates village-level SAFE/WATCH/WARNING/EVACUATE assessments.
- Provides a weather-console interface inspired by modern weather dashboards, with hourly-style forecast cards, atmospheric widgets, precipitation radar, interactive risk map layers and satellite-style visualization.
- Includes light/dark theme switching, animated radar sweep, clickable villages, risk gauge, sensor pulse chart and satellite layer filters.
- Creates simulated SMS alerts automatically for EVACUATE conditions.
- Includes a real Twilio SMS provider behind an explicit `LIVE_SMS=true` backend switch.
- Never places Twilio credentials in frontend code.

## Run
```bash
cp .env.example .env
docker compose up --build
```
Open http://localhost:5173 and API docs at http://localhost:8000/docs.

## Real Twilio SMS
Twilio's Python SDK supports programmatic outbound SMS through the Messaging API. Configure the following backend variables:

```env
LIVE_SMS=true
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM=+1...
SMS_RECIPIENTS=+91XXXXXXXXXX,+91YYYYYYYYYY
```

The application keeps a cooldown per village to reduce duplicate emergency messages. Test the integration from **Alerts & SMS**. Production deployment should use Twilio API keys/secrets and comply with applicable Indian telecom/DLT/template requirements.

## Demo scenarios
- Simulate Flash Flood
- Landslide Scenario
- Reset Conditions

The automatic simulation ticks every 8 seconds while the dashboard is open.

## Important
All environmental values are synthetic. This is a decision-support demonstration and does not provide official warnings or validated forecasts.

## Image credits
The UI references Himalayan imagery from Wikimedia Commons, including `Monsoon in Himalayas.jpg` (CC BY 3.0) and other Commons Himalayan imagery. Verify license/attribution requirements before commercial reuse.

## Statement Coverage — Geo Shield AI

This release explicitly covers the requested problem statement:

- Hyper-local village/ward risk visualization for hilly Himalayan regions
- Flash-flood and landslide decision support
- Rainfall measurement and short-term precipitation indicators
- Soil-moisture monitoring
- Slope-stability / ground-movement indicators
- Historical hazard context in the explainable risk layer
- Simulated real-time IoT telemetry
- Satellite / remote-sensing intelligence panel
- Automatic risk escalation and actionable evacuation guidance
- Warning lead-time metric for simulation/demo use
- Real India map using OpenStreetMap geography with Himalayan village overlays
- Animated scanning layer over the satellite intelligence panel
- Automatic synthetic weather and sensor changes
- Twilio SMS integration with safe demo mode by default

### Satellite sources

The satellite screen is designed to connect to official Indian sources. The current UI embeds MOSDAC LIVE where browser framing permits it and provides an IMD INSAT-3DR Rapid Scan link. If an official source blocks embedding, Geo Shield AI falls back to the local demonstration imagery and keeps the scanning animation visible rather than pretending the fallback is live satellite data.

Official sources:
- MOSDAC LIVE: https://www.mosdac.gov.in/live-frame
- IMD INSAT-3DR Rapid Scan: https://mausam.imd.gov.in/imd_latest/contents/rapidscan.php

### Map

The command center uses OpenStreetMap tiles through Leaflet. The map is real geographic map data; the hazard circles, risk values, rainfall values, and Himalayan corridor overlay are demonstration/model layers and are not official hazard boundaries.


## Satellite fallback fix
The MOSDAC page is not embedded in an iframe because that service may refuse framing via browser security headers. Geo Shield AI now uses a local animated remote-sensing visualization with official IMD Rapid Scan and MOSDAC links that open directly in a new tab. The interface clearly labels the local frames as demo data.

## Latest UI update

Geo Shield AI now includes:
- Blue intelligence visual theme
- Updated Geo Shield AI mission banner
- Dedicated Landslide AI page and landslide simulation
- Animated slope/deformation scan visualization
- Priority slope ranking by simulated landslide score
- "Why Geo Shield AI" section explaining the product positioning
- Differentiator cards covering hyper-local, explainable, multi-source, actionable and failure-aware workflows
- Optional future feature panel for CAP alerts, WhatsApp/Push, offline PWA, InSAR deformation, road closures and shelter routing

### Positioning note
The prototype should not claim that the underlying science is unique to Geo Shield AI. India already has official landslide forecasting, susceptibility mapping and remote-sensing initiatives. Geo Shield AI's intended differentiation is the integrated operational experience: one village/ward view that combines multi-source signals, explainable risk, sensor health, simulation, evacuation guidance and notification workflow.

## Original SIH Presentation

The **Presentation** tab now plays the original user-provided SIH 2026 six-page PDF exactly as supplied, rendered slide-by-slide for reliable in-app playback. It is not a recreated presentation.

Controls: Play/Pause, Previous/Next, Fullscreen, Escape to close, Arrow keys, Space to pause/play.

The original PDF is also preserved at `frontend/public/presentation/original-sih-2026.pdf`.


## Twilio SMS configuration

The backend uses Twilio's Python SDK with server-side environment variables. Never put the Account Auth Token in React/frontend code.

Set these in `.env` (or the server environment):

```env
LIVE_SMS=true
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_rotated_auth_token
TWILIO_FROM=+1xxxxxxxxxx
TWILIO_TO=+91xxxxxxxxxx
```

You can instead use `SMS_RECIPIENTS` for multiple E.164 recipients. The **SMS Test Console** sends the literal test body `sms_internal_alerts`; evacuation scenarios generate a contextual Geo Shield AI alert.

The app remains in demo mode until `LIVE_SMS=true` is explicitly enabled.
