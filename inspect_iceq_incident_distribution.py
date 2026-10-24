
import pandas as pd
from pathlib import Path

file_path = Path("data/iceq_simulated_readings_v2.csv")
df = pd.read_csv(file_path)

df["timestamp"] = pd.to_datetime(df["timestamp"])

print("=" * 55)
print("ICEQ INCIDENT DISTRIBUTION REPORT")
print("=" * 55)

# 1. Overall summary by unit
print("\n1. INCIDENT SUMMARY BY UNIT")

summary = df.groupby(
    ["unit_id", "food_type"]
).agg(
    total_readings=("timestamp", "size"),
    incident_readings=("incident_active", "sum"),
    threshold_exceedances=("threshold_exceeded", "sum"),
    unique_incidents=("incident_id", "nunique"),
)

summary["incident_rate_pct"] = (
    summary["incident_readings"]
    / summary["total_readings"] * 100
).round(2)

print(summary.to_string())

# 2. Incident distribution by calendar day
print("\n2. INCIDENT READINGS BY DAY AND UNIT")

df["date"] = df["timestamp"].dt.date

daily = df.pivot_table(
    index="date",
    columns="unit_id",
    values="incident_active",
    aggfunc="sum",
    fill_value=0,
)

print(daily.to_string())

# 3. Exact incident episodes
print("\n3. INDIVIDUAL INCIDENT EPISODES")

incidents = df[df["incident_active"] == 1].copy()

if incidents.empty:
    print("No active incidents found.")
else:
    episodes = incidents.groupby("incident_id").agg(
        unit_id=("unit_id", "first"),
        food_type=("food_type", "first"),
        start=("timestamp", "min"),
        end=("timestamp", "max"),
        readings=("timestamp", "size"),
        max_temperature=("temperature_c", "max"),
        threshold=("temperature_threshold_c", "first"),
    )

    print(episodes.to_string())

# 4. Confirm the source dataset was not changed.
print("\n4. DATASET CHECK")
print("Total rows:", len(df))
print("Date range:", df["timestamp"].min(), "to", df["timestamp"].max())
print("This script did not modify the dataset.")
