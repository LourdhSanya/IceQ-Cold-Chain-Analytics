
import pandas as pd
from pathlib import Path


def evaluate_alerts(df):
    # Convert the simulated incident label into 0 and 1
    actual = df["incident_active"].astype(int)

    # Check whether the temperature crossed its threshold
    threshold_alert = df["threshold_exceeded"].astype(int)

    # Check whether IceQ classified the reading as critical
    critical_alert = (
        df["risk_status"] == "CRITICAL"
    ).astype(int)

    print("TOTAL READINGS:", len(df))
    print("KNOWN INCIDENT READINGS:", actual.sum())

    print("\n--- THRESHOLD ALERT EVALUATION ---")

    print(
        "Correctly detected incident readings:",
        ((actual == 1) & (threshold_alert == 1)).sum()
    )

    print(
        "Missed incident readings:",
        ((actual == 1) & (threshold_alert == 0)).sum()
    )

    print(
        "Alerts outside known incidents:",
        ((actual == 0) & (threshold_alert == 1)).sum()
    )

    print("\n--- CRITICAL ALERT EVALUATION ---")

    print(
        "Incident readings classified CRITICAL:",
        ((actual == 1) & (critical_alert == 1)).sum()
    )

    print(
        "Incident readings not classified CRITICAL:",
        ((actual == 1) & (critical_alert == 0)).sum()
    )

    print(
        "CRITICAL readings outside known incidents:",
        ((actual == 0) & (critical_alert == 1)).sum()
    )

    print("\n--- RESULTS BY UNIT ---")

    print(
        df.groupby("unit_id").agg(
            known_incident_readings=("incident_active", "sum"),
            threshold_alerts=("threshold_exceeded", "sum"),
            critical_readings=("sustained_excursion", "sum")
        ).to_string()
    )


def main():
    input_file = Path("data/iceq_risk_results_v2.csv")

    df = pd.read_csv(input_file)

    evaluate_alerts(df)


if __name__ == "__main__":
    main()
