
import pandas as pd
import numpy as np
from pathlib import Path


def generate_sensor_data():
    np.random.seed(42)

    # Three simulated refrigerated storage units
    units = {
        "UNIT_001": {"food_type": "Dairy", "base_temp": 4.0, "base_humidity": 70},
        "UNIT_002": {"food_type": "Produce", "base_temp": 6.0, "base_humidity": 85},
        "UNIT_003": {"food_type": "Frozen", "base_temp": -18.0, "base_humidity": 60}
    }

    # Generate readings every 5 minutes for 24 hours
    timestamps = pd.date_range(
        start="2026-10-21 00:00:00",
        periods=288,
        freq="5min"
    )

    records = []

    for unit_id, details in units.items():
        for timestamp in timestamps:

            temperature = details["base_temp"] + np.random.normal(0, 0.5)
            humidity = details["base_humidity"] + np.random.normal(0, 3)

            # Simulate a temperature excursion in the dairy unit
            if (
                unit_id == "UNIT_001"
                and pd.Timestamp("2026-10-21 10:00:00")
                <= timestamp
                <= pd.Timestamp("2026-10-21 11:00:00")
            ):
                temperature += 5

            # Keep relative humidity within 0–100%
            humidity = np.clip(humidity, 0, 100)

            records.append({
                "timestamp": timestamp,
                "unit_id": unit_id,
                "food_type": details["food_type"],
                "temperature_c": round(temperature, 2),
                "humidity_pct": round(humidity, 2),
                "data_source": "simulated"
            })

    df = pd.DataFrame(records)

    # Save the generated readings
    output_folder = Path("data")
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder / "sensor_readings.csv"
    df.to_csv(output_file, index=False)

    print("IceQ sensor data generated successfully!")
    print("Dataset shape:", df.shape)
    print("Saved to:", output_file)
    print("\nFirst 5 readings:")
    print(df.head())


if __name__ == "__main__":
    generate_sensor_data()
