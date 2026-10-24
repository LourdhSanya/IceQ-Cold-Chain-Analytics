
import pandas as pd


def create_risk_labels():
    # Step 1: Load the prepared dataset
    df = pd.read_csv(
        "data/prepared_sensor_readings.csv",
        parse_dates=["timestamp"]
    )

    # Step 2: Define illustrative temperature thresholds
    thresholds = {
        "Dairy": 5.0,
        "Produce": 8.0,
        "Frozen": -15.0
    }

    # Step 3: Assign a threshold to each reading
    df["risk_threshold_c"] = df["food_type"].map(thresholds)

    # Step 4: Create a rule-based risk label
    df["risk_label"] = (
        df["temperature_c"] > df["risk_threshold_c"]
    ).astype(int)

    # Step 5: Display the number of readings in each class
    print("\n--- RISK LABEL COUNTS ---")
    print(df["risk_label"].value_counts().sort_index())

    # Step 6: Display risk counts for each unit
    print("\n--- RISK COUNTS BY UNIT ---")
    print(
        df.groupby("unit_id")["risk_label"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "risk_readings"})
    )

    # Step 7: Display examples of flagged readings
    print("\n--- EXAMPLE FLAGGED READINGS ---")
    print(
        df.loc[
            df["risk_label"] == 1,
            [
                "timestamp",
                "unit_id",
                "food_type",
                "temperature_c",
                "risk_threshold_c",
                "risk_label"
            ]
        ].head(10)
    )

    # Step 8: Save the labelled dataset
    output_file = "data/labelled_sensor_readings.csv"
    df.to_csv(output_file, index=False)

    print("\nLabelled dataset shape:", df.shape)
    print("Saved to:", output_file)


if __name__ == "__main__":
    create_risk_labels()
