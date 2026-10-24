
import pandas as pd
from pathlib import Path


def create_incident_summary(df):
    # Convert timestamps to datetime format
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Keep only readings belonging to known simulated incidents
    incidents = df[df["incident_id"].notna()].copy()

    # Summarize each incident
    summary = incidents.groupby("incident_id").agg(
        unit_id=("unit_id", "first"),
        start_time=("timestamp", "min"),
        end_time=("timestamp", "max"),
        total_readings=("timestamp", "count"),
        max_temperature_c=("temperature_c", "max"),
        threshold_c=("temperature_threshold_c", "first"),
        critical_readings=(
            "risk_status",
            lambda status: (status == "CRITICAL").sum()
        ),
        warning_readings=(
            "risk_status",
            lambda status: (status == "WARNING").sum()
        )
    ).reset_index()

    # Calculate how far the maximum temperature exceeded the limit
    summary["max_temperature_excess_c"] = (
        summary["max_temperature_c"] - summary["threshold_c"]
    ).clip(lower=0)

    # Calculate elapsed time between the first and last readings
    summary["elapsed_minutes"] = (
        summary["end_time"] - summary["start_time"]
    ).dt.total_seconds() / 60

    # Label the summary as simulated data
    summary["data_source"] = "simulated"

    # Arrange incidents chronologically
    summary = summary.sort_values("start_time")

    return summary


def main():
    input_file = Path("data/iceq_risk_results_v2.csv")
    output_file = Path("data/iceq_incident_summary_v2.csv")

    df = pd.read_csv(input_file)

    summary = create_incident_summary(df)

    # Save to a new file; preserve all existing datasets
    summary.to_csv(output_file, index=False)

    print("IceQ incident summary created successfully!")

    print("\n--- INCIDENT SUMMARY ---")
    print(summary.to_string(index=False))

    print("\nTotal simulated incidents:", len(summary))
    print("Saved to:", output_file)


if __name__ == "__main__":
    main()
