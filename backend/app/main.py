from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import os
import random


# ============================================================
# GEO SHIELD AI - FASTAPI BACKEND
# ============================================================

try:
    from twilio.rest import Client
except Exception:
    Client = None


app = FastAPI(
    title="Geo Shield AI API",
    description="Flood and landslide early warning demonstration API",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

DEMO = os.getenv("DEMO_MODE", "true").lower() == "true"

LIVE_SMS = os.getenv("LIVE_SMS", "false").lower() == "true"

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_FROM", "")

SMS_RECIPIENTS = [
    x.strip()
    for x in os.getenv("SMS_RECIPIENTS", "").split(",")
    if x.strip()
]

TWILIO_TO = os.getenv("TWILIO_TO", "").strip()

if TWILIO_TO and TWILIO_TO not in SMS_RECIPIENTS:
    SMS_RECIPIENTS.append(TWILIO_TO)


# ============================================================
# DEMO VILLAGES
# ============================================================

villages = [
    {
        "id": 1,
        "name": "Devgaon",
        "region": "Himachal Frontier",
        "block": "North Valley",
        "lat": 32.18,
        "lng": 76.34,
        "elevation": 1480,
        "rain": 38,
        "temp": 19,
        "humidity": 78,
        "soil": 57,
        "slope": 28,
        "river": 35,
    },
    {
        "id": 2,
        "name": "Pahadi Tola",
        "region": "Uttarakhand Ridge",
        "block": "Upper Hills",
        "lat": 30.34,
        "lng": 78.05,
        "elevation": 2050,
        "rain": 64,
        "temp": 15,
        "humidity": 86,
        "soil": 76,
        "slope": 39,
        "river": 51,
    },
    {
        "id": 3,
        "name": "Riverbend",
        "region": "Sikkim Valley",
        "block": "River Valley",
        "lat": 27.33,
        "lng": 88.61,
        "elevation": 1320,
        "rain": 82,
        "temp": 18,
        "humidity": 91,
        "soil": 84,
        "slope": 31,
        "river": 76,
    },
    {
        "id": 4,
        "name": "Lakshmi Nagar",
        "region": "Himachal Frontier",
        "block": "Lower Valley",
        "lat": 31.10,
        "lng": 77.17,
        "elevation": 1450,
        "rain": 27,
        "temp": 21,
        "humidity": 70,
        "soil": 42,
        "slope": 21,
        "river": 28,
    },
    {
        "id": 5,
        "name": "Upper Valley",
        "region": "Ladakh Foothills",
        "block": "High Pass",
        "lat": 34.15,
        "lng": 77.58,
        "elevation": 3200,
        "rain": 22,
        "temp": 8,
        "humidity": 48,
        "soil": 31,
        "slope": 43,
        "river": 29,
    },
    {
        "id": 6,
        "name": "Cloud Hamlet",
        "region": "Sikkim Valley",
        "block": "East Ridge",
        "lat": 27.46,
        "lng": 88.50,
        "elevation": 2180,
        "rain": 71,
        "temp": 14,
        "humidity": 88,
        "soil": 79,
        "slope": 46,
        "river": 58,
    },
    {
        "id": 7,
        "name": "Pine Crest",
        "region": "Uttarakhand Ridge",
        "block": "Forest Belt",
        "lat": 30.15,
        "lng": 78.32,
        "elevation": 1770,
        "rain": 53,
        "temp": 16,
        "humidity": 82,
        "soil": 69,
        "slope": 35,
        "river": 43,
    },
    {
        "id": 8,
        "name": "Snowline",
        "region": "Himachal Frontier",
        "block": "High Ridge",
        "lat": 32.41,
        "lng": 77.19,
        "elevation": 2760,
        "rain": 31,
        "temp": 5,
        "humidity": 61,
        "soil": 46,
        "slope": 51,
        "river": 33,
    },
]


# ============================================================
# SHELTERS
# ============================================================

shelters = [
    {
        "id": 1,
        "name": "Devgaon Community Hall",
        "location": "Devgaon",
        "capacity": 500,
        "occupancy": 182,
        "distance": "1.8 km",
    },
    {
        "id": 2,
        "name": "Upper Hills School",
        "location": "Pahadi Tola",
        "capacity": 320,
        "occupancy": 260,
        "distance": "2.4 km",
    },
    {
        "id": 3,
        "name": "Valley Relief Centre",
        "location": "Riverbend",
        "capacity": 700,
        "occupancy": 488,
        "distance": "3.1 km",
    },
]


# ============================================================
# GLOBAL STATE
# ============================================================

alerts = []
last_sms = {}
scenario = "NORMAL"
last_updated = datetime.now(timezone.utc)


WEATHER_TYPES = [
    "Light rain",
    "Moderate rain",
    "Heavy rain",
    "Thunderstorms",
    "Cloudy",
    "Mist & rain",
]


# ============================================================
# HELPERS
# ============================================================

def clamp(x, a=0, b=100):
    return max(a, min(b, x))


def now():
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# RISK ENGINE
# ============================================================

def risk(v):

    flood = clamp(
        v["rain"] * 0.52
        + v["river"] * 0.28
        + v["soil"] * 0.20
    )

    landslide = clamp(
        v["slope"] * 1.45
        + v["soil"] * 0.35
        + v["rain"] * 0.32
        + max(0, v["humidity"] - 65) * 0.25
    )

    combined = clamp(
        0.55 * flood
        + 0.45 * landslide
    )

    critical = (
        v["river"] >= 94
        or (
            v["soil"] >= 96
            and v["rain"] >= 92
        )
        or v.get("ground", 0) >= 90
    )

    if critical:
        level = "EVACUATE"

    elif combined >= 75:
        level = "EVACUATE"

    elif combined >= 50:
        level = "WARNING"

    elif combined >= 25:
        level = "WATCH"

    else:
        level = "SAFE"

    coverage = (
        91
        if v["id"] not in (5, 8)
        else random.randint(54, 72)
    )

    confidence = (
        "HIGH"
        if coverage >= 80
        else "MEDIUM"
        if coverage >= 50
        else "LOW"
    )

    weather_reason = (
        f"{v['rain']} mm/h simulated rain "
        f"and {v['humidity']}% humidity"
    )

    explanation = [
        weather_reason,
        f"Soil saturation proxy {v['soil']}%",
        f"Slope exposure {v['slope']}°",
        f"River level index {v['river']}%",
    ]

    if v.get("ground", 0) > 60:
        explanation.append(
            f"Ground movement index {v['ground']}%"
        )

    simple = {
        "SAFE":
            "Conditions currently look stable. "
            "Keep monitoring official updates.",

        "WATCH":
            "Rain and terrain signals are increasing. "
            "Stay alert and keep an evacuation plan ready.",

        "WARNING":
            "Multiple hazard signals are elevated. "
            "Authorities should prepare response teams "
            "and residents should be ready to move.",

        "EVACUATE":
            "Dangerous conditions are simulated. "
            "Move toward the nearest designated safe shelter "
            "and follow official instructions.",
    }[level]

    return {
        "flood_score": round(flood),
        "landslide_score": round(landslide),
        "score": round(combined),
        "level": level,
        "coverage": coverage,
        "confidence": confidence,
        "explanation": explanation,
        "simple_explanation": simple,
        "model": "Explainable hybrid rules engine v1.0-demo",
    }


# ============================================================
# SNAPSHOT
# ============================================================

def snapshot(v):

    base = max(0.1, v["rain"])

    rain_series = {
        "rainfall_15m": round(base * 0.22, 1),
        "rainfall_1h": round(base, 1),
        "rainfall_3h": round(base * 2.15, 1),
        "rainfall_6h": round(base * 3.55, 1),
        "rainfall_24h": round(base * 6.8, 1),

        "forecast_1h": round(
            base * random.uniform(0.85, 1.25),
            1,
        ),

        "forecast_3h": round(
            base * random.uniform(1.7, 2.8),
            1,
        ),

        "rain_source":
            "Simulated rain gauge / forecast fusion",
    }

    return {
        **v,
        **rain_series,
        "risk": risk(v),
    }


# ============================================================
# ALERT SYSTEM
# ============================================================

def build_message(v, r):

    shelter = min(
        shelters,
        key=lambda s: float(
            s["distance"].split()[0]
        ),
    )

    return (
        f"GEO SHIELD AI: {r['level']} at {v['name']}. "
        f"Risk {r['score']}/100. "
        f"{r['simple_explanation']} "
        f"Nearest demo shelter: {shelter['name']}."
    )


def send_sms(v, r):

    body = (
        f"GEO SHIELD AI ALERT - {r['level']}\n"
        f"Location: {v['name']}\n"
        f"Risk: {r['score']}/100\n"
        f"{r['simple_explanation']}\n"
        "Follow official local authority instructions."
    )

    if not LIVE_SMS:
        return "SIMULATED"

    if not (
        Client
        and TWILIO_ACCOUNT_SID
        and TWILIO_AUTH_TOKEN
        and TWILIO_FROM
        and SMS_RECIPIENTS
    ):
        return "SMS_NOT_CONFIGURED"

    key = v["id"]

    if (
        key in last_sms
        and datetime.now(timezone.utc) - last_sms[key]
        < timedelta(minutes=20)
    ):
        return "COOLDOWN"

    try:

        client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN,
        )

        statuses = []

        for to in SMS_RECIPIENTS:

            msg = client.messages.create(
                body=body,
                from_=TWILIO_FROM,
                to=to,
            )

            statuses.append(
                msg.status or "queued"
            )

        last_sms[key] = datetime.now(timezone.utc)

        return "SENT" if statuses else "FAILED"

    except Exception:
        return "FAILED"


def maybe_alert(v, r):

    global alerts

    if r["level"] not in (
        "WARNING",
        "EVACUATE",
    ):
        return

    existing = next(
        (
            a
            for a in alerts
            if a["village_id"] == v["id"]
            and a["status"]
            in ("ACTIVE", "ACKNOWLEDGED")
        ),
        None,
    )

    if existing:

        if existing["level"] != r["level"]:

            existing["level"] = r["level"]
            existing["score"] = r["score"]
            existing["message"] = build_message(v, r)
            existing["updated_at"] = now()

        return

    alert = {
        "id": len(alerts) + 1,
        "village_id": v["id"],
        "village": v["name"],
        "level": r["level"],
        "score": r["score"],
        "message": build_message(v, r),
        "status": "ACTIVE",
        "created_at": now(),
        "sms": "SIMULATED",
        "updated_at": now(),
    }

    if r["level"] == "EVACUATE":
        alert["sms"] = send_sms(v, r)

    alerts.insert(0, alert)


# ============================================================
# SIMULATION ENGINE
# ============================================================

def auto_tick():

    global last_updated, scenario

    intensity = (
        1
        if scenario == "NORMAL"
        else 1.8
        if scenario == "HEAVY_RAIN"
        else 2.8
    )

    for v in villages:

        drift = (
            random.uniform(-3, 4)
            * intensity
        )

        v["rain"] = round(
            clamp(
                v["rain"]
                + drift
                + (
                    4
                    if v["id"] in (2, 3, 6)
                    and scenario != "NORMAL"
                    else 0
                ),
                0,
                120,
            )
        )

        v["soil"] = round(
            clamp(
                v["soil"]
                + random.uniform(-1, 2)
                * intensity
                + (
                    2
                    if scenario != "NORMAL"
                    else 0
                ),
                10,
                99,
            )
        )

        v["river"] = round(
            clamp(
                v["river"]
                + random.uniform(-2, 3)
                * intensity
                + (
                    3
                    if v["id"] in (2, 3)
                    and scenario != "NORMAL"
                    else 0
                ),
                5,
                99,
            )
        )

        v["humidity"] = round(
            clamp(
                v["humidity"]
                + random.uniform(-2, 2),
                35,
                99,
            )
        )

        v["temp"] = round(
            v["temp"]
            + random.uniform(-0.5, 0.5),
            1,
        )

        v["ground"] = round(
            clamp(
                v.get("ground", 35)
                + random.uniform(-3, 4)
                + (
                    3
                    if scenario == "LANDSLIDE"
                    and v["id"] in (5, 6, 8)
                    else 0
                ),
                5,
                98,
            )
        )

        maybe_alert(
            v,
            risk(v),
        )

    last_updated = datetime.now(timezone.utc)

    return current()


# ============================================================
# ROOT ROUTES
# ============================================================

@app.get("/")
def root():

    return {
        "name": "Geo Shield AI",
        "status": "online",
        "message": "Geo Shield AI backend is running successfully.",
        "version": "1.0.0",
        "mode": "DEMO" if DEMO else "LIVE",
        "api": "/api/risk/current",
        "health": "/health",
        "docs": "/docs",
        "redoc": "/redoc",
        "timestamp": now(),
    }


@app.get("/api")
def api_root():

    return {
        "name": "Geo Shield AI API",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "risk": "/api/risk/current",
            "weather": "/api/weather/forecast",
            "alerts": "/api/alerts",
            "sensors": "/api/sensors/health",
            "shelters": "/api/shelters",
            "config": "/api/config",
            "docs": "/docs",
        },
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "Geo Shield AI",
        "database": "demo-memory",
        "mqtt": "simulated",
        "sms": "live" if LIVE_SMS else "demo",
        "workers": "frontend-polling",
        "timestamp": now(),
    }


# ============================================================
# CURRENT RISK
# ============================================================

@app.get("/api/risk/current")
def current():

    return {
        "updated_at": last_updated.isoformat(),
        "scenario": scenario,
        "locations": [
            snapshot(v)
            for v in villages
        ],
        "alerts": alerts[:10],
    }


# ============================================================
# WEATHER FORECAST
# ============================================================

@app.get("/api/weather/forecast")
def forecast():

    out = []

    for i in range(7):

        rain = round(
            clamp(
                30
                + random.random() * 75
                + (
                    18
                    if scenario != "NORMAL"
                    else 0
                )
            )
        )

        temp = round(
            random.uniform(5, 24),
            1,
        )

        out.append(
            {
                "day": (
                    datetime.now(timezone.utc)
                    + timedelta(days=i)
                ).strftime("%a"),

                "temp": temp,

                "rain_mm": rain,

                "chance": min(
                    98,
                    round(
                        rain * 0.9
                        + random.randint(5, 20)
                    ),
                ),

                "condition":
                    random.choice(
                        WEATHER_TYPES
                    ),
            }
        )

    return {
        "region":
            "Indian Himalayan Region · simulated",

        "generated_at":
            now(),

        "forecast":
            out,
    }


# ============================================================
# SIMULATION TICK
# ============================================================

@app.post("/api/simulation/tick")
def tick():

    return auto_tick()


# ============================================================
# FLASH FLOOD SCENARIO
# ============================================================

@app.post("/api/simulation/flash-flood")
def flash_flood():

    global scenario

    scenario = "HEAVY_RAIN"

    for v in villages:

        if v["id"] in (2, 3, 6):

            v["rain"] = min(
                120,
                v["rain"]
                + random.randint(18, 30),
            )

            v["soil"] = min(
                99,
                v["soil"]
                + random.randint(8, 15),
            )

            v["river"] = min(
                99,
                v["river"]
                + random.randint(10, 18),
            )

        maybe_alert(
            v,
            risk(v),
        )

    return current()


# ============================================================
# LANDSLIDE SCENARIO
# ============================================================

@app.post("/api/simulation/landslide")
def landslide():

    global scenario

    scenario = "LANDSLIDE"

    for v in villages:

        if v["id"] in (5, 6, 8):

            v["soil"] = min(
                99,
                v["soil"]
                + random.randint(10, 18),
            )

            v["rain"] = min(
                120,
                v["rain"]
                + random.randint(10, 24),
            )

            v["ground"] = min(
                99,
                v.get("ground", 35)
                + random.randint(20, 35),
            )

        maybe_alert(
            v,
            risk(v),
        )

    return current()


# ============================================================
# NORMAL SCENARIO
# ============================================================

@app.post("/api/simulation/normal")
def normal():

    global scenario

    scenario = "NORMAL"

    for v in villages:

        v["rain"] = round(
            random.uniform(18, 48)
        )

        v["soil"] = round(
            random.uniform(35, 65)
        )

        v["river"] = round(
            random.uniform(20, 48)
        )

        v["ground"] = round(
            random.uniform(15, 45)
        )

    return current()


# ============================================================
# RESET
# ============================================================

@app.post("/api/simulation/reset")
def reset():

    return normal()


# ============================================================
# ALERTS
# ============================================================

@app.get("/api/alerts")
def get_alerts():

    return {
        "alerts": alerts
    }


@app.post(
    "/api/alerts/{alert_id}/acknowledge"
)
def acknowledge(alert_id: int):

    for a in alerts:

        if a["id"] == alert_id:

            a["status"] = "ACKNOWLEDGED"
            a["updated_at"] = now()

            return a

    raise HTTPException(
        status_code=404,
        detail="Alert not found",
    )


@app.post(
    "/api/alerts/{alert_id}/resolve"
)
def resolve(alert_id: int):

    for a in alerts:

        if a["id"] == alert_id:

            a["status"] = "RESOLVED"
            a["updated_at"] = now()

            return a

    raise HTTPException(
        status_code=404,
        detail="Alert not found",
    )


# ============================================================
# SMS TEST
# ============================================================

class SmsTest(BaseModel):

    phone: str


@app.post("/api/notifications/test")
def test_sms(payload: SmsTest):

    if not payload.phone.startswith("+"):

        raise HTTPException(
            status_code=400,
            detail="Use E.164 format, e.g. +9198...",
        )

    if not LIVE_SMS:

        return {
            "status": "SIMULATED",
            "to": payload.phone,
            "mode": "demo",
        }

    if not (
        Client
        and TWILIO_ACCOUNT_SID
        and TWILIO_AUTH_TOKEN
        and TWILIO_FROM
    ):

        return {
            "status":
                "SMS_NOT_CONFIGURED",

            "detail":
                "Set TWILIO_ACCOUNT_SID, "
                "TWILIO_AUTH_TOKEN and "
                "TWILIO_FROM in the server environment.",
        }

    try:

        msg = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN,
        ).messages.create(
            to=payload.phone,
            from_=TWILIO_FROM,
            body="Geo Shield AI internal alert test.",
        )

        return {
            "status": "SENT",
            "message_sid": msg.sid,
            "provider_status":
                msg.status or "queued",
        }

    except Exception:

        return {
            "status": "FAILED",
            "detail":
                "Twilio request failed. "
                "Check server logs and Twilio configuration.",
        }


# ============================================================
# SENSOR HEALTH
# ============================================================

@app.get("/api/sensors/health")
def sensor_health():

    return {
        "total": 52,
        "online": 46,
        "offline": 4,
        "warning": 2,

        "items": [
            {
                "id": "RAIN-021",
                "type": "RAIN_GAUGE",
                "location": "Riverbend",
                "battery": 18,
                "signal": 31,
                "status": "STALE",
            },
            {
                "id": "TILT-014",
                "type": "TILT",
                "location": "Pahadi Tola",
                "battery": 77,
                "signal": 82,
                "status": "ONLINE",
            },
            {
                "id": "SAT-007",
                "type": "SATELLITE_PROXY",
                "location": "Himalayan Pass",
                "battery": 100,
                "signal": 96,
                "status": "ONLINE",
            },
        ],
    }


# ============================================================
# SHELTERS
# ============================================================

@app.get("/api/shelters")
def get_shelters():

    return {
        "shelters": shelters
    }


# ============================================================
# CONFIG
# ============================================================

@app.get("/api/config")
def config():

    sms_configured = bool(
        Client
        and TWILIO_ACCOUNT_SID
        and TWILIO_AUTH_TOKEN
        and TWILIO_FROM
        and SMS_RECIPIENTS
    )

    return {
        "demo_mode": DEMO,
        "live_sms": LIVE_SMS,
        "sms_configured": sms_configured,
        "twilio_from_configured": bool(
            TWILIO_FROM
        ),
        "recipient_count":
            len(SMS_RECIPIENTS),
        "region":
            "Indian Himalayan Region",
    }
