
import pandas as pd
from pathlib import Path

# 1. File paths
INPUT_PATH = Path("data/iceq_ml_dataset_clean_v1.csv")
DATA_DIR = Path("data")

# 2. Load the cleaned dataset
df = pd.read_csv(INPUT_PATH, parse_dates=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# 3. Find chronological split boundaries
unique_times = sorted(df["timestamp"].unique())
total_times = len(unique_times)

boundary_1 = pd.Timestamp(unique_times[int(total_times * 0.70)])
boundary_2 = pd.Timestamp(unique_times[int(total_times * 0.85)])

# The target uses the next 30 minutes.
# Keep a 30-minute gap around each boundary.
gap = pd.Timedelta(minutes=30)

train_end = boundary_1 - gap
validation_start = boundary_1 + gap
validation_end = boundary_2 - gap
test_start = boundary_2 + gap

# 4. Create chronological datasets
train_df = df[df["timestamp"] <= train_end].copy()

validation_df = df[
    (df["timestamp"] >= validation_start)
    & (df["timestamp"] <= validation_end)
].copy()

test_df = df[df["timestamp"] >= test_start].copy()

# 5. Save separate files
train_path = DATA_DIR / "iceq_train_v1.csv"
validation_path = DATA_DIR / "iceq_validation_v1.csv"
test_path = DATA_DIR / "iceq_test_v1.csv"

train_df.to_csv(train_path, index=False)
validation_df.to_csv(validation_path, index=False)
test_df.to_csv(test_path, index=False)

# 6. Report and verify the splits
target = "target_future_exceedance_30m"

for name, part in [
    ("TRAIN", train_df),
    ("VALIDATION", validation_df),
    ("TEST", test_df),
]:
    print("\n" + "=" * 50)
    print(name)
    print("=" * 50)
    print("Rows:", len(part))

    if len(part) > 0:
        print("Start:", part["timestamp"].min())
        print("End:  ", part["timestamp"].max())

        print("\nTarget counts:")
        print(part[target].value_counts().sort_index().to_string())

        print("\nPositive target percentage:",
              round(part[target].mean() * 100, 2), "%")
    else:
        print("WARNING: This split is empty.")

# 7. Check that the sets do not overlap in time
assert train_df["timestamp"].max() < validation_df["timestamp"].min()
assert validation_df["timestamp"].max() < test_df["timestamp"].min()

print("\nChronological split verification: PASSED")
print("Training file:   ", train_path.resolve())
print("Validation file: ", validation_path.resolve())
print("Testing file:    ", test_path.resolve())
