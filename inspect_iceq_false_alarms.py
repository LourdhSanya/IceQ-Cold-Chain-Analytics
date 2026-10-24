
import pandas as pd
from pathlib import Path

DATA = Path("data")

valid = pd.read_csv(DATA / "iceq_validation_v1.csv")
cat = pd.read_csv(DATA / "iceq_validation_predictions_v1.csv")
xgb = pd.read_csv(DATA / "iceq_xgboost_validation_predictions_v1.csv")

df = valid.copy()
df["cat_probability"] = cat["predicted_probability"].to_numpy()
df["xgb_probability"] = xgb["predicted_probability"].to_numpy()

df["actual"] = df["target_future_exceedance_30m"].astype(int)

for model in ["cat", "xgb"]:
    df[f"{model}_predicted"] = (
        df[f"{model}_probability"] >= 0.50
    ).astype(int)

print("\n1. ACTUAL POSITIVE CASES BY UNIT")
print(
    df.groupby(["unit_id", "food_type"])["actual"]
    .agg(["count", "sum", "mean"])
    .rename(columns={"sum": "positive_cases", "mean": "positive_rate"})
    .round(3)
    .to_string()
)

for model in ["cat", "xgb"]:
    false_alarms = df[
        (df[f"{model}_predicted"] == 1) & (df["actual"] == 0)
    ].copy()

    print(f"\n2. {model.upper()} FALSE ALARMS BY UNIT")
    print(
        false_alarms.groupby(["unit_id", "food_type"])
        .size()
        .rename("false_alarms")
        .to_string()
    )

    print(f"\n3. {model.upper()} FALSE ALARMS BY CURRENT TEMPERATURE")
    false_alarms["temperature_band"] = pd.cut(
        false_alarms["temperature_current"],
        bins=[-100, -15, 0, 3, 4, 5, 8, 100],
        labels=[
            "Below -15", "-15 to 0", "0 to 3",
            "3 to 4", "4 to 5", "5 to 8", "Above 8"
        ],
        right=False
    )

    print(
        false_alarms.groupby("temperature_band", observed=False)
        .size()
        .rename("false_alarms")
        .to_string()
    )

    print(f"\n4. {model.upper()} PROBABILITY VS ACTUAL OUTCOME")
    df[f"{model}_probability_band"] = pd.cut(
        df[f"{model}_probability"],
        bins=[-0.001, 0.2, 0.4, 0.5, 0.6, 0.8, 1.001],
        labels=["0–0.2", "0.2–0.4", "0.4–0.5",
                "0.5–0.6", "0.6–0.8", "0.8–1.0"]
    )

    print(
        df.groupby(f"{model}_probability_band", observed=False)
        .agg(
            readings=("actual", "size"),
            actual_positive_rate=("actual", "mean")
        )
        .round(3)
        .to_string()
    )

print("\nAnalysis complete. No models or datasets were modified.")
