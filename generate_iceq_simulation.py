
import pandas as pd
import numpy as np
from pathlib import Path


def generate_iceq_simulation():
    np.random.seed(42)

    # Step 1: Define the virtual storage units
    units = {
        "UNIT_001": {
            "food_type": "Dairy",
            "base_temp": 4.0,
            "base_humidity": 70.0,
            "threshold": 5.0
        },
        "UNIT_002": {
            "food_type": "Produce",
            "base_temp": 6.0,
            "base_humidity": 85.0,
            "threshold": 8.0
        },
        "UNIT_003": {
            "food_type": "Frozen",
            "base_temp": -18.0,
            "base_humidity": 60.0,
            "threshold": -15.0
        }
    }

    # Step 2: Define simulated temperature incidents
    # Times are illustrative, not real-world food-safety events.
    events = [
        {
            "event_id": "DAIRY_001",
            "unit_id": "UNIT_001",
            "start": "2026-10-16 10:00:00",
            "end": "2026-10-16 11:00:00",
            "temp_increase": 4.0
        },
        {
            "event_id": "DAIRY_002",
            "unit_id": "UNIT_001",
            "start": "2026-10-18 16:00:00",
            "end": "2026-10-18 17:30:00",
            "temp_increase": 4.5
        },
        {
            "event_id": "DAIRY_003",
            "unit_id": "UNIT_001",
            "start": "2026-10-21 03:00:00",
            "end": "2026-10-21 04:00:00",
            "temp_increase": 4.0
        },
        {
            "event_id": "PRODUCE_001",
            "unit_id": "UNIT_002",
            "start": "2026-10-17 13:00:00",
            "end": "2026-10-17 14:30:00",
            "temp_increase": 3.5
        },
        {
            "event_id": "PRODUCE_002",
            "unit_id": "UNIT_002",
            "start": "2026-10-21 15:00:00",
            "end": "2026-10-21 16:00:00",
            "temp_increase": 3.5
        },
        {
            "event_id": "FROZEN_001",
            "unit_id": "UNIT_003",
            "start": "2026-10-17 20:00:00",
            "end": "2026-10-17 21:00:00",
            "temp_increase": 4.5
        },
        {
            "event_id": "FROZEN_002",
            "unit_id": "UNIT_003",
            "start": "2026-10-21 10:00:00",
            "end": "2026-10-21 11:30:00",
            "temp_increase": 4.5
        }
    ]

    # Step 3: Generate readings every five minutes for seven days
    timestamps = pd.date_range(
        start="2026-10-15 00:00:00",
        periods=7 * 24 * 12,
        freq="5min"
    )

    records = []

    # Step 4: Simulate each unit independently
    for unit_id, details in units.items():
        unit_events = [
            event for event in events
            if event["unit_id"] == unit_id
        ]

        for timestamp in timestamps:
            temperature = (
                details["base_temp"] + np.random.normal(0, 0.5)
            )
            humidity = (
                details["base_humidity"] + np.random.normal(0, 3)
            )

            active_event = None

            # Apply a temperature increase during an event
            for event in unit_events:
                event_start = pd.Timestamp(event["start"])
                event_end = pd.Timestamp(event["end"])

                if event_start <= timestamp < event_end:
                    temperature += event["temp_increase"]
                    active_event = event
                    break

            records.append({
                "timestamp": timestamp,
                "unit_id": unit_id,
                "food_type": details["food_type"],
                "temperature_c": round(temperature, 2),
                "humidity_pct": round(
                    np.clip(humidity, 0, 100), 2
                ),
                "temperature_threshold_c": details["threshold"],
                "threshold_exceeded": int(
                    temperature > details["threshold"]
                ),
                "incident_active": int(active_event is not None),
                "incident_id": (
                    active_event["event_id"]
                    if active_event else ""
                ),
                "data_source": "simulated",
                "simulation_version": "2.0"
            })

    # Step 5: Create the dataset
    df = pd.DataFrame(records)

    # Step 6: Save without overwriting existing files
    output_folder = Path("data")
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder / "iceq_simulated_readings_v2.csv"
    df.to_csv(output_file, index=False)

    # Step 7: Display a summary
    print("IceQ simulation generated successfully!")
    print("Dataset shape:", df.shape)
    print("Time range:", df["timestamp"].min(), "to",
          df["timestamp"].max())

    print("\n--- READINGS PER UNIT ---")
    print(df["unit_id"].value_counts())

    print("\n--- KNOWN SIMULATED INCIDENT READINGS ---")
    print(df.groupby("unit_id")["incident_active"].agg(
        ["sum", "count"]
    ))

    print("\n--- THRESHOLD EXCEEDANCES ---")
    print(df.groupby("unit_id")["threshold_exceeded"].sum())

    print("\n--- INCIDENT SUMMARY ---")
    print(
        df[df["incident_active"] == 1]
        .groupby(["unit_id", "incident_id"])
        .size()
        .rename("readings")
    )

    print("\nSaved to:", output_file)


if __name__ == "__main__":
    generate_iceq_simulation()
