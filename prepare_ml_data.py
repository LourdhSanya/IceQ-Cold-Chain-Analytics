
import pandas as pd
from sklearn.model_selection import train_test_split


def prepare_ml_data():
    # Step 1: Load labelled sensor readings
    df = pd.read_csv(
        "data/labelled_sensor_readings.csv",
        parse_dates=["timestamp"]
    )

    # Step 2: Sort readings chronologically within each unit
    df = df.sort_values(
        ["unit_id", "timestamp"]
    ).reset_index(drop=True)

    # Step 3: Create numerical features from the food category
    df = pd.get_dummies(
        df,
        columns=["food_type"],
        dtype=int
    )

    # Step 4: Select input features for the first model
    feature_columns = [
        "temperature_c",
        "humidity_pct",
        "food_type_Dairy",
        "food_type_Frozen",
        "food_type_Produce"
    ]

    X = df[feature_columns]
    y = df["risk_label"]

    # Step 5: Split each unit by time
    # First 80% of each unit's readings: training
    # Last 20% of each unit's readings: testing
    train_parts = []
    test_parts = []

    for unit_id, unit_df in df.groupby("unit_id", sort=False):
        split_index = int(len(unit_df) * 0.8)

        train_parts.append(unit_df.iloc[:split_index])
        test_parts.append(unit_df.iloc[split_index:])

    train_df = pd.concat(train_parts)
    test_df = pd.concat(test_parts)

    X_train = train_df[feature_columns]
    y_train = train_df["risk_label"]

    X_test = test_df[feature_columns]
    y_test = test_df["risk_label"]

    # Step 6: Display dataset sizes and label distribution
    print("\n--- FEATURE COLUMNS ---")
    print(feature_columns)

    print("\n--- TRAINING DATA ---")
    print("X_train shape:", X_train.shape)
    print("y_train shape:", y_train.shape)
    print(y_train.value_counts().sort_index())

    print("\n--- TEST DATA ---")
    print("X_test shape:", X_test.shape)
    print("y_test shape:", y_test.shape)
    print(y_test.value_counts().sort_index())

    # Step 7: Save separate training and test datasets
    train_df.to_csv("data/train_data.csv", index=False)
    test_df.to_csv("data/test_data.csv", index=False)

    print("\nSaved training data to data/train_data.csv")
    print("Saved test data to data/test_data.csv")


if __name__ == "__main__":
    prepare_ml_data()
