import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# Number of samples
data_size = 100

data = {
    "Time_of_Day": np.random.randint(0, 24, data_size),
    "Day_of_Week": np.random.randint(1, 8, data_size),
    "Month": np.random.randint(1, 13, data_size),
    "Weather_Condition": np.random.choice([1, 2], data_size, p=[0.7, 0.3]),
    "Temperature": np.round(np.random.normal(25, 10, data_size), 2),
    "Humidity": np.round(np.random.uniform(10, 100, data_size), 2),
    "Traffic_Volume": np.random.randint(50, 350, data_size),
    "Event_Indicator": np.random.choice([0, 1], data_size, p=[0.7, 0.3])
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Adjustment Factor logic
def calculate_adjustment(row):
    factor = 0

    # High traffic increases adjustment
    if row.Traffic_Volume > 250:
        factor += 15
    elif row.Traffic_Volume > 150:
        factor += 10
    elif row.Traffic_Volume > 100:
        factor += 5

    # Bad weather
    if row.Weather_Condition == 2:
        factor += 5

    # Events
    if row.Event_Indicator == 1:
        factor += 10

    # Morning/evening rush hours
    if 7 <= row.Time_of_Day <= 10 or 17 <= row.Time_of_Day <= 20:
        factor += 10

    # Low temp + high humidity combo (likely foggy)
    if row.Temperature < 10 and row.Humidity > 70:
        factor += 5

    return min(factor, 45)  # Cap at 45%

# Apply adjustment factor
df["Adjustment_Factor"] = df.apply(calculate_adjustment, axis=1)

# Show a sample
print(df.head())

# Optionally save to CSV
df.to_csv("synthetic_traffic_data.csv", index=False)
