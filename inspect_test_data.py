
import pandas as pd


def inspect_test_data():
    df = pd.read_csv(
        "data/test_data.csv",
        parse_dates=["timestamp"]
    )

    print("\n--- TEST PERIOD BY UNIT ---")
    print(
        df.groupby("unit_id")["timestamp"]
        .agg(["min", "max", "count"])
    )

    print("\n--- RISK READINGS IN TEST DATA ---")
    risky = df[df["risk_label"] == 1]

    if risky.empty:
        print("No risk readings found in the test data.")
    else:
        print(
            risky[
                [
                    "timestamp",
                    "unit_id",
                    "temperature_c",
                    "risk_threshold_c",
                    "risk_label"
                ]
            ].to_string(index=False)
        )

    print("\n--- RISK COUNTS BY UNIT ---")
    print(
        df.groupby("unit_id")["risk_label"]
        .agg(["sum", "count"])
    )


if __name__ == "__main__":
    inspect_test_data()
