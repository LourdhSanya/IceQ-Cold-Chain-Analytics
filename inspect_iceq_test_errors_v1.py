
import pandas as pd

FILE_PATH = "data/iceq_test_predictions_v1.csv"

df = pd.read_csv(FILE_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Keep false positives only
false_alarms = df[
    (df["actual_future_exceedance"] == 0)
    & (df["predicted_future_exceedance"] == 1)
].copy()

print("Total false positives:", len(false_alarms))

print("\nFalse positives by food type:")
print(false_alarms["food_type"].value_counts())

print("\nTemperature summary by food type:")
print(
    false_alarms.groupby("food_type")["temperature_current"]
    .agg(["count", "mean", "min", "max"])
    .round(2)
)

# Sort and group consecutive 5-minute false-positive readings
false_alarms = false_alarms.sort_values(
    ["unit_id", "timestamp"]
)

false_alarms["time_gap"] = (
    false_alarms.groupby("unit_id")["timestamp"]
    .diff()
)

false_alarms["new_episode"] = (
    false_alarms["time_gap"].isna()
    | (false_alarms["time_gap"] > pd.Timedelta(minutes=5))
)

false_alarms["episode_id"] = (
    false_alarms.groupby("unit_id")["new_episode"]
    .cumsum()
)

episodes = (
    false_alarms.groupby(["unit_id", "food_type", "episode_id"])
    .agg(
        start=("timestamp", "min"),
        end=("timestamp", "max"),
        readings=("timestamp", "size"),
        mean_temperature=("temperature_current", "mean"),
        mean_probability=("predicted_probability", "mean"),
    )
    .reset_index()
)

episodes["duration_minutes"] = (
    episodes["end"] - episodes["start"]
).dt.total_seconds() / 60

episodes = episodes.sort_values(
    "readings", ascending=False
)

print("\nLongest false-positive episodes:")
print(episodes.head(15).round(3).to_string(index=False))

episodes.to_csv(
    "data/iceq_test_false_positive_episodes_v1.csv",
    index=False
)

print("\nEpisode summary saved.")
