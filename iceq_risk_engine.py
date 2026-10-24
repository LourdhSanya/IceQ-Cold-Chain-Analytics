
import pandas as pd
from pathlib import Path


def evaluate_sensor_readings(df):
    # Step 1: Make sure readings are in chronological order
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df.sort_values(
        ["unit_id", "timestamp"]
    ).reset_index(drop=True)

    # Step 2: Calculate how far the temperature exceeds its limit
    df["temperature_excess_c"] = (
        df["temperature_c"] - df["temperature_threshold_c"]
    ).clip(lower=0)

    # Step 3: Flag readings that exceed the configured threshold
    df["threshold_exceeded"] = (
        df["temperature_c"] > df["temperature_threshold_c"]
    ).astype(int)

    # Step 4: Calculate consecutive readings above threshold
    # Reset the count when the unit changes or the temperature returns
    # to the acceptable side of the configured threshold.
    df["excursion_group"] = (
        df["threshold_exceeded"].eq(0)
        | df["unit_id"].ne(df["unit_id"].shift())
    ).groupby(df["unit_id"]).cumsum()

    df["consecutive_exceedance_readings"] = (
        df.groupby(["unit_id", "excursion_group"])
        ["threshold_exceeded"]
        .cumsum()
    )

    # Step 5: Flag sustained excursions lasting at least 15 minutes.
    # With readings every 5 minutes, that means 3 consecutive readings.
    df["sustained_excursion"] = (
        df["consecutive_exceedance_readings"] >= 4
    ).astype(int)

    # Step 6: Assign a simple operational status
    df["risk_status"] = "NORMAL"

    df.loc[
        df["threshold_exceeded"] == 1,
        "risk_status"
    ] = "WARNING"

    df.loc[
        df["sustained_excursion"] == 1,
        "risk_status"
    ] = "CRITICAL"

    return df


def main():
    input_file = Path("data/iceq_simulated_readings_v2.csv")
    output_file = Path("data/iceq_risk_results_v2.csv")

    df = pd.read_csv(input_file)
    results = evaluate_sensor_readings(df)

    # Save results without changing the original simulation file
    results.to_csv(output_file, index=False)

    print("IceQ risk evaluation completed.")

    print("\n--- STATUS COUNTS ---")
    print(results["risk_status"].value_counts())

    print("\n--- RESULTS BY UNIT ---")
    print(
        results.groupby("unit_id").agg(
            total_readings=("timestamp", "count"),
            threshold_exceedances=("threshold_exceeded", "sum"),
            sustained_readings=("sustained_excursion", "sum")
        )
    )

    print("\n--- EXAMPLE ALERT READINGS ---")
    print(
        results.loc[
            results["risk_status"] != "NORMAL",
            [
                "timestamp",
                "unit_id",
                "temperature_c",
                "temperature_threshold_c",
                "temperature_excess_c",
                "consecutive_exceedance_readings",
                "risk_status"
            ]
        ].head(15).to_string(index=False)
    )

    print("\nSaved to:", output_file)


if __name__ == "__main__":
    main()
