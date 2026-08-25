# Geo Shield AI — One File Run Package

## Windows
1. Install Docker Desktop.
2. Double-click `START.bat`.
3. Open http://localhost:5173
4. API docs: http://localhost:8000/docs

## Linux/macOS
```bash
chmod +x start.sh
./start.sh
```

## Real Twilio SMS
The package starts safely with simulated SMS only. To enable real SMS, edit `.env`:

```env
LIVE_SMS=true
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_FROM=+xxxxxxxxxxxx
SMS_RECIPIENTS=+91xxxxxxxxxx,+91yyyyyyyyyy
```

Restart with the launcher after changing `.env`.

## What is automatic
- Synthetic Himalayan weather changes automatically.
- Fake IoT sensors update automatically.
- Satellite-style risk observations update automatically.
- AI/rules risk scores update automatically.
- Villages can escalate to WATCH/WARNING/EVACUATE.
- Simulated SMS alerts appear automatically.
- Flash flood and landslide demo scenarios are available.

All environmental data is synthetic/demo data. It is not an official forecast or government warning.

## New interactive interface
- Dark/light visual theme switch
- Weather-console hero with temperature, humidity, wind and visibility
- Clickable Himalayan risk map with Risk / Rain / Satellite layers
- Animated precipitation radar
- AI threat gauge
- 24-hour rain pulse chart
- Satellite Cloud / Moisture / Terrain filters
- Sensor network pulse visualization
- Mobile navigation drawer
