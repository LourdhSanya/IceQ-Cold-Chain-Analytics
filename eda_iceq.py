
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the original simulation dataset
DATA_PATH = Path("data/iceq_simulated_readings_v2.csv")
OUTPUT_DIR = Path("reports/eda")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# 2. Display basic dataset information
print("=" * 60)
print("ICEQ - EXPLORATORY DATA ANALYSIS")
print("=" * 60)

print("\nDATASET SHAPE")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# 3. Temperature statistics for each unit
print("\nTEMPERATURE STATISTICS BY UNIT")

temperature_summary = df.groupby(
    ["unit_id", "food_type"]
)["temperature_c"].agg(
    ["count", "mean", "min", "max", "std"]
).round(2)

print(temperature_summary.to_string())

# 4. Threshold exceedances by unit
print("\nTHRESHOLD EXCEEDANCES BY UNIT")

threshold_summary = df.groupby("unit_id").agg(
    total_readings=("temperature_c", "size"),
    exceedances=("threshold_exceeded", "sum"),
    incident_readings=("incident_active", "sum")
)

threshold_summary["exceedance_percentage"] = (
    threshold_summary["exceedances"]
    / threshold_summary["total_readings"] * 100
).round(2)

print(threshold_summary.to_string())

# 5. Chart 1: Temperature distribution by unit
plt.figure(figsize=(10, 6))

for unit, group in df.groupby("unit_id"):
    plt.hist(
        group["temperature_c"],
        bins=35,
        alpha=0.5,
        label=unit
    )

plt.title("IceQ: Temperature Distribution by Unit")
plt.xlabel("Temperature (°C)")
plt.ylabel("Number of Readings")
plt.legend()
plt.grid(alpha=0.2)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "temperature_distribution.png", dpi=150)
plt.close()

# 6. Chart 2: Temperature over time
fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)

for ax, (unit, group) in zip(axes, df.groupby("unit_id")):
    group = group.sort_values("timestamp")

    ax.plot(
        group["timestamp"],
        group["temperature_c"],
        linewidth=1,
        label="Temperature"
    )

    ax.plot(
        group["timestamp"],
        group["temperature_threshold_c"],
        linestyle="--",
        label="Configured threshold"
    )

    ax.set_title(f"{unit} - {group['food_type'].iloc[0]}")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()
    ax.grid(alpha=0.2)

axes[-1].set_xlabel("Timestamp")
fig.suptitle("IceQ: Temperature Trends and Thresholds")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "temperature_trends.png", dpi=150)
plt.close(fig)

# 7. Chart 3: Threshold exceedances by unit
exceedance_counts = df.groupby("unit_id")[
    "threshold_exceeded"
].sum()

plt.figure(figsize=(8, 5))
exceedance_counts.plot(kind="bar")

plt.title("IceQ: Threshold Exceedances by Unit")
plt.xlabel("Monitoring Unit")
plt.ylabel("Number of Exceeding Readings")
plt.xticks(rotation=0)
plt.grid(axis="y", alpha=0.2)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "threshold_exceedances.png", dpi=150)
plt.close()

# 8. Save summary tables without modifying the source data
temperature_summary.to_csv(
    OUTPUT_DIR / "temperature_summary.csv"
)

threshold_summary.to_csv(
    OUTPUT_DIR / "threshold_summary.csv"
)

print("\nEDA COMPLETE")
print("Charts and summary tables saved to:", OUTPUT_DIR.resolve())
print("\nGenerated files:")
for path in sorted(OUTPUT_DIR.iterdir()):
    print("-", path.name)
