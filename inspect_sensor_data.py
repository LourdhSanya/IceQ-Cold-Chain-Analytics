
import pandas as pd


def inspect_sensor_data():
    # Step 1: Load the CSV file
    df = pd.read_csv("data/sensor_readings.csv")

    # Step 2: Check the number of rows and columns
    print("\n--- DATASET SIZE ---")
    print(df.shape)

    # Step 3: Display the first five rows
    print("\n--- FIRST FIVE READINGS ---")
    print(df.head())

    # Step 4: Check column names and data types
    print("\n--- DATASET INFORMATION ---")
    df.info()

    # Step 5: Check missing values
    print("\n--- MISSING VALUES ---")
    print(df.isnull().sum())

    # Step 6: Check duplicate rows
    print("\n--- DUPLICATE ROWS ---")
    print(df.duplicated().sum())

    # Step 7: Count readings from each unit
    print("\n--- READINGS PER UNIT ---")
    print(df["unit_id"].value_counts())

    # Step 8: Calculate basic statistics
    print("\n--- TEMPERATURE STATISTICS ---")
    print(df["temperature_c"].describe())

    print("\n--- HUMIDITY STATISTICS ---")
    print(df["humidity_pct"].describe())


if __name__ == "__main__":
    inspect_sensor_data()
