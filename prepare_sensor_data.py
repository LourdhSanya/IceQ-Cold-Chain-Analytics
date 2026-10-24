
import pandas as pd


def prepare_sensor_data():
    # Step 1: Load the original dataset
    df = pd.read_csv("data/sensor_readings.csv")

    # Step 2: Convert timestamp text to datetime
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # Step 3: Check whether conversion created missing timestamps
    print("\n--- INVALID TIMESTAMPS ---")
    print(df["timestamp"].isnull().sum())

    # Step 4: Sort readings by unit and time
    df = df.sort_values(
        ["unit_id", "timestamp"]
    ).reset_index(drop=True)

    # Step 5: Check temperature statistics for each unit
    print("\n--- TEMPERATURE BY UNIT ---")
    print(
        df.groupby("unit_id")["temperature_c"]
        .agg(["count", "min", "mean", "max"])
        .round(2)
    )

    # Step 6: Check humidity limits
    print("\n--- HUMIDITY VALIDATION ---")
    invalid_humidity = (
        (df["humidity_pct"] < 0)
        | (df["humidity_pct"] > 100)
    )
    print("Invalid humidity readings:", invalid_humidity.sum())

    # Step 7: Save the prepared dataset
    output_file = "data/prepared_sensor_readings.csv"
    df.to_csv(output_file, index=False)

    print("\nPrepared dataset shape:", df.shape)
    print("Saved to:", output_file)
    print("\nFirst five prepared readings:")
    print(df.head())


if __name__ == "__main__":
    prepare_sensor_data()
