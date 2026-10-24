
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
from fastapi import FastAPI, HTTPException

import json
import re
from datetime import datetime, timezone
from pydantic import BaseModel, Field

app = FastAPI(
    title="IceQ API",
    description="Cold-chain monitoring using simulated sensor data",
    version="1.0.0"
)

# Allow the local IceQ frontend to access the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://ice-q-cold-chain-analytics.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"


@app.get("/")
def home():
    return {
        "application": "IceQ",
        "message": "IceQ API is running",
        "data_source": "simulated"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/units")
def get_units():
    file_path = DATA_DIR / "iceq_risk_results_v2.csv"

    if not file_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Risk results file not found"
        )

    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Get the latest reading for each unit
    latest = df.groupby("unit_id").tail(1)

    columns = [
        "unit_id",
        "food_type",
        "timestamp",
        "temperature_c",
        "humidity_pct",
        "temperature_threshold_c",
        "risk_status",
        "data_source"
    ]

    return latest[columns].to_dict(orient="records")


@app.get("/api/incidents")
def get_incidents():
    file_path = DATA_DIR / "iceq_incident_summary_v2.csv"

    if not file_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Incident summary file not found"
        )

    df = pd.read_csv(file_path)

    return df.to_dict(orient="records")




@app.get("/api/readings")
def get_readings(unit_id: str | None = None, limit: int = 1000):
    file_path = DATA_DIR / "iceq_risk_results_v2.csv"

    if not file_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Historical sensor readings file not found"
        )

    if limit < 1 or limit > 10000:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 10000"
        )

    df = pd.read_csv(file_path)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Optionally filter readings for one monitoring unit.
    if unit_id is not None:
        df = df[df["unit_id"] == unit_id]

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No readings found for unit {unit_id}"
            )

    df = df.sort_values("timestamp").tail(limit)

    columns = [
        "timestamp",
        "unit_id",
        "food_type",
        "temperature_c",
        "temperature_threshold_c",
        "risk_status",
        "data_source"
    ]

    # Convert timestamps to strings for a JSON-friendly response.
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S")

    return df[columns].to_dict(orient="records")



@app.get("/api/summary")
def get_summary():
    import pandas as pd

    from pathlib import Path

    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"

    risk_file = data_dir / "iceq_risk_results_v2.csv"
    incidents_file = data_dir / "incident_summary.csv"

    if not risk_file.exists():
        return {
            "total_units": 0,
            "latest_timestamp": None,
            "status_counts": {
                "NORMAL": 0,
                "WARNING": 0,
                "CRITICAL": 0,
            },
            "total_incidents": 0,
            "data_source": "simulated",
        }

    df = pd.read_csv(risk_file)

    if df.empty:
        return {
            "total_units": 0,
            "latest_timestamp": None,
            "status_counts": {
                "NORMAL": 0,
                "WARNING": 0,
                "CRITICAL": 0,
            },
            "total_incidents": 0,
            "data_source": "simulated",
        }

    latest_timestamp = pd.to_datetime(
        df["timestamp"], errors="coerce"
    ).max()

    latest_rows = df[
        pd.to_datetime(df["timestamp"], errors="coerce")
        == latest_timestamp
    ]

    latest_statuses = (
        latest_rows["risk_status"]
        .astype(str)
        .str.upper()
        .value_counts()
        .to_dict()
    )

    total_incidents = 0

    if incidents_file.exists():
        incident_df = pd.read_csv(incidents_file)
        total_incidents = len(incident_df)

    return {
        "total_units": int(latest_rows["unit_id"].nunique()),
        "latest_timestamp": (
            latest_timestamp.isoformat()
            if pd.notna(latest_timestamp)
            else None
        ),
        "status_counts": {
            "NORMAL": int(latest_statuses.get("NORMAL", 0)),
            "WARNING": int(latest_statuses.get("WARNING", 0)),
            "CRITICAL": int(latest_statuses.get("CRITICAL", 0)),
        },
        "total_incidents": int(total_incidents),
        "data_source": "simulated",
    }


class DemoRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    organisation: str = Field(min_length=2, max_length=150)
    message: str = Field(min_length=10, max_length=2000)


@app.post("/api/demo-requests")
def create_demo_request(request: DemoRequest):
    # Check the email format.
    email = request.email.strip()

    if not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email
    ):
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid email address."
        )

    # Store requests in the project's data folder.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / "demo_requests.json"

    try:
        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as file:
                requests = json.load(file)

            if not isinstance(requests, list):
                raise ValueError("Invalid demo request file")
        else:
            requests = []

        new_request = {
            "id": len(requests) + 1,
            "name": request.name.strip(),
            "email": email,
            "organisation": request.organisation.strip(),
            "message": request.message.strip(),
            "submitted_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": "NEW",
            "data_source": "website_demo_request"
        }

        requests.append(new_request)

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(requests, file, indent=4)

    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not save your request. Please try again."
        ) from exc

    return {
        "success": True,
        "message": "Your demo request has been received.",
        "request_id": new_request["id"]
    }