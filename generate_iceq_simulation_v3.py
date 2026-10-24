
import pandas as pd
import numpy as np
from pathlib import Path


def generate_iceq_simulation_v3():
    rng = np.random.default_rng(73)

    # 1. Define virtual storage units
    units = {
        "UNIT_001": {
            "food_type": "Dairy",
            "base_temp": 4.0,
            "base_humidity": 70.0,
            "threshold": 5.0,
        },
        "UNIT_002": {
            "food_type": "Produce",
            "base_temp": 6.0,
            "base_humidity": 85.0,
            "threshold": 8.0,
        },
        "UNIT_003": {
            "food_type": "Frozen",
            "base_temp": -18.0,
            "base_humidity": 60.0,
            "threshold": -15.0,
        },
    }

    # 2. Generate seven days of readings at five-minute intervals
    timestamps = pd.date_range(
        start="2026-10-15 00:00:00",
        periods=7 * 24 * 12,
        freq="5min",
    )

    # 3. Randomly create incidents for each unit.
    # Incident times are synthetic and are not real food-safety records.
    events = []

    for unit_id, details in units.items():
        event_count = 8

        # Choose varied start times across the seven-day period.
        possible_starts = np.arange(12, len(timestamps) - 36)
        selected_starts = np.sort(
            rng.choice(possible_starts, size=event_count, replace=False)
        )

        for number, start_index in enumerate(selected_starts, start=1):
            duration_steps = int(rng.integers(6, 19))
            end_index = min(
                start_index + duration_steps,
                len(timestamps),
            )

            # Increase temperature enough to create a mixture
            # of small warnings and stronger threshold excursions.
            threshold_gap = details["threshold"] - details["base_temp"]
            increase = max(
                0.3,
                threshold_gap + rng.uniform(-0.3, 2.5),
            )

            events.append({
                "event_id": f"{unit_id}_EVENT_{number:02d}",
                "unit_id": unit_id,
                "start_index": int(start_index),
                "end_index": int(end_index),
                "temp_increase": float(increase),
                "recovery_steps": int(rng.integers(3, 10)),
            })

    # 4. Generate sensor readings
    records = []

    for unit_id, details in units.items():
        unit_events = [
            event for event in events
            if event["unit_id"] == unit_id
        ]

        # A small drifting component makes readings less uniform.
        drift = 0.0

        for index, timestamp in enumerate(timestamps):
            drift = 0.95 * drift + rng.normal(0, 0.035)

            temperature = (
                details["base_temp"]
                + drift
                + rng.normal(0, 0.45)
            )
            humidity = (
                details["base_humidity"]
                + rng.normal(0, 3.0)
            )

            active_event = None

            # 5. Apply incident rise and gradual recovery
            for event in unit_events:
                if event["start_index"] <= index < event["end_index"]:
                    elapsed = index - event["start_index"]

                    # A gradual rise avoids an identical fixed jump
                    # at every reading during the event.
                    rise_factor = min(1.0, (elapsed + 1) / 3.0)
                    temperature += event["temp_increase"] * rise_factor
                    active_event = event
                    break

                elif event["end_index"] <= index < (
                    event["end_index"] + event["recovery_steps"]
                ):
                    recovery_progress = (
                        index - event["end_index"] + 1
                    ) / event["recovery_steps"]

                    temperature += (
                        event["temp_increase"]
                        * max(0.0, 1.0 - recovery_progress)
                    )

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
                "simulation_version": "3.0",
            })

    # 6. Save to a new file. Never overwrite the V2 dataset.
    df = pd.DataFrame(records)

    output_folder = Path("data")
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder / "iceq_simulated_readings_v3.csv"
    df.to_csv(output_file, index=False)

    # 7. Print summary
    print("IceQ simulation V3 generated.")
    print("Dataset shape:", df.shape)
    print("Time range:", df["timestamp"].min(), "to", df["timestamp"].max())

    print("\nReadings per unit:")
    print(df.groupby("unit_id").size())

    print("\nIncident readings per unit:")
    print(df.groupby("unit_id")["incident_active"].sum())

    print("\nThreshold exceedances per unit:")
    print(df.groupby("unit_id")["threshold_exceeded"].sum())

    print("\nIncident counts per unit:")
    print(
        df[df["incident_active"] == 1]
        .groupby("unit_id")["incident_id"]
        .nunique()
    )

    print("\nSaved to:", output_file)


if __name__ == "__main__":
    generate_iceq_simulation_v3()
