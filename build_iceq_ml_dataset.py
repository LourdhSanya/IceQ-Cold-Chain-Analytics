
import pandas as pd
from pathlib import Path

# 1. File paths
INPUT_PATH = Path("data/iceq_simulated_readings_v2.csv")
OUTPUT_PATH = Path("data/iceq_ml_dataset_v1.csv")

# 2. Load data
df = pd.read_csv(INPUT_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values(
    ["unit_id", "timestamp"]
).reset_index(drop=True)

# 3. Create the future prediction target
# A positive target means at least one exceedance
# occurs in the NEXT six readings (30 minutes).

future_flags = []

for step in range(1, 7):
    future_flags.append(
        df.groupby("unit_id")["threshold_exceeded"]
        .shift(-step)
        .rename(f"future_{step}")
    )

future_flags = pd.concat(future_flags, axis=1)

# Exclude rows that do not have a complete future window
valid_future = future_flags.notna().all(axis=1)

df["target_future_exceedance_30m"] = (
    future_flags.max(axis=1)
)

# 4. Create features using current and past data only
grouped = df.groupby("unit_id", group_keys=False)

# Current sensor readings
df["temperature_current"] = df["temperature_c"]
df["humidity_current"] = df["humidity_pct"]

# Difference between temperature and configured threshold
df["temperature_margin"] = (
    df["temperature_c"] - df["temperature_threshold_c"]
)

# Temperature changes compared with previous readings
df["temperature_change_5m"] = grouped[
    "temperature_c"
].diff(1)

df["temperature_change_15m"] = grouped[
    "temperature_c"
].diff(3)

df["temperature_change_30m"] = grouped[
    "temperature_c"
].diff(6)

# Historical rolling statistics.
# shift(1) ensures the rolling window excludes the current reading.
df["temperature_mean_previous_30m"] = grouped[
    "temperature_c"
].transform(
    lambda s: s.shift(1).rolling(6, min_periods=1).mean()
)

df["temperature_max_previous_30m"] = grouped[
    "temperature_c"
].transform(
    lambda s: s.shift(1).rolling(6, min_periods=1).max()
)

df["humidity_mean_previous_30m"] = grouped[
    "humidity_pct"
].transform(
    lambda s: s.shift(1).rolling(6, min_periods=1).mean()
)

# Time features available at prediction time
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek

# 5. Assemble the ML dataset

# 5. Assemble the ML dataset
# Keep only rows with a complete 30-minute history
# and a complete 30-minute future prediction window.

feature_columns = [
    "unit_id",
    "food_type",
    "temperature_current",
    "humidity_current",
    "temperature_threshold_c",
    "temperature_margin",
    "temperature_change_5m",
    "temperature_change_15m",
    "temperature_change_30m",
    "temperature_mean_previous_30m",
    "temperature_max_previous_30m",
    "humidity_mean_previous_30m",
    "hour",
    "day_of_week",
]

target_column = "target_future_exceedance_30m"

# Require all historical numeric features to be available.
history_columns = [
    "temperature_change_5m",
    "temperature_change_15m",
    "temperature_change_30m",
    "temperature_mean_previous_30m",
    "temperature_max_previous_30m",
    "humidity_mean_previous_30m",
]

valid_rows = (
    valid_future
    & df[history_columns].notna().all(axis=1)
)

ml_df = df.loc[
    valid_rows,
    ["timestamp"] + feature_columns
].copy()

ml_df[target_column] = (
    df.loc[valid_rows, target_column].astype(int)
)

# 6. Validate the prepared dataset.
print("=" * 60)
print("ICEQ CLEAN ML DATASET")
print("=" * 60)

print("\nDataset shape:", ml_df.shape)

print("\nRows per unit:")
print(ml_df.groupby("unit_id").size().to_string())

print("\nTarget counts:")
print(ml_df[target_column].value_counts().sort_index().to_string())

print("\nTarget percentages:")
print(
    (ml_df[target_column].value_counts(normalize=True) * 100)
    .round(2)
    .to_string()
)

print("\nMissing values:")
print(ml_df.isna().sum().to_string())

print("\nDuplicate rows:", ml_df.duplicated().sum())

print(
    "\nTimestamp range:",
    ml_df["timestamp"].min(),
    "to",
    ml_df["timestamp"].max()
)

# 7. Save as a new file. Do not overwrite the source dataset.
OUTPUT_PATH = Path("data/iceq_ml_dataset_clean_v1.csv")
ml_df.to_csv(OUTPUT_PATH, index=False)

print("\nSaved:", OUTPUT_PATH.resolve())
print("\nFirst five rows:")
print(ml_df.head().to_string(index=False))
