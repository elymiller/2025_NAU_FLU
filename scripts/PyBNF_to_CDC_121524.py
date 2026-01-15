import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Constants
BASE_DIR = '/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/results/'  # Update with the actual path
REFERENCE_DATE = datetime(2026, 1, 17)  # Reference date
QUANTILES = [0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 
             0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975, 0.99]
HORIZONS = [0, 1, 2, 3]  # Weeks ahead

# Load locations file and ensure two-digit formatting
locations_df = pd.read_csv("/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/locations.csv")
locations_df = locations_df[locations_df['location'].str.isdigit()]  # Keep only rows with numeric location
locations_df['location'] = locations_df['location'].astype(int).apply(lambda x: str(x).zfill(2))

# Initialize an empty list to store rows for the final CSV
rows = []

# Dictionary to store aggregated values for the US
us_aggregated = {(horizon, quantile): 0 for horizon in HORIZONS for quantile in QUANTILES}

# Function to process trajectory files and extract quantiles
def extract_quantiles(file_path):
    data = np.genfromtxt(file_path)  # Load data
    qtlMark = np.array(QUANTILES)  # Quantile markers
    qtlLog = np.zeros((len(qtlMark), 4))  # 4 weeks (last 4 columns)

    # Compute quantiles for the last 4 columns
    for i in range(4):
        qtlLog[:, i] = np.quantile(data[:, -(4 - i)], qtlMark)
    return qtlLog

# Loop through each state/territory folder
for state_name in os.listdir(BASE_DIR):
    state_path = os.path.join(BASE_DIR, state_name)
    traj_file = os.path.join(state_path, f'Results/A_MCMC/Runs/traj_noise_{state_name}_fluH_weekly_chain_0.txt')
    #print(traj_file)

    # Skip if trajectory file does not exist
    if not os.path.isfile(traj_file):
        print(f"Warning: Missing file for {state_name}")
        continue

    # Extract location number for this state
    location_row = locations_df[locations_df['location_name'] == state_name]  # Match state_name
    if location_row.empty:
        print(f"Warning: Location not found for {state_name}")
        continue
              
    location = location_row['location'].values[0]  # Extract location number (two-digit format)

    # Extract quantiles from the trajectory file
    quantiles_by_week = extract_quantiles(traj_file)

    # Fill rows for each horizon, quantile, and value
    for horizon in HORIZONS:  # Weeks 0-3
        target_end_date = (REFERENCE_DATE + timedelta(weeks=horizon)).strftime("%Y-%m-%d")
        for i, quantile in enumerate(QUANTILES):  # 23 quantiles
            value = quantiles_by_week[i, horizon]
            row = {
                'reference_date': REFERENCE_DATE.strftime("%Y-%m-%d"),
                'target': "wk inc flu hosp",
                'horizon': horizon,
                'target_end_date': target_end_date,
                'location': location,
                'output_type': "quantile",
                'output_type_id': quantile,
                'value': value  # Extracted quantile value
            }
            rows.append(row)
            
            # Aggregate values for the US
            us_aggregated[(horizon, quantile)] += value

# Add aggregated US rows to the final dataset
for (horizon, quantile), value in us_aggregated.items():
    target_end_date = (REFERENCE_DATE + timedelta(weeks=horizon)).strftime("%Y-%m-%d")
    us_row = {
        'reference_date': REFERENCE_DATE.strftime("%Y-%m-%d"),
        'target': "wk inc flu hosp",
        'horizon': horizon,
        'target_end_date': target_end_date,
        'location': "US",
        'output_type': "quantile",
        'output_type_id': quantile,
        'value': value
    }
    rows.append(us_row)

final_df = pd.DataFrame(rows)

# Sort by location (numerical order)
final_df['location'] = pd.Categorical(final_df['location'], ordered=True)
final_df = final_df.sort_values(['location', 'horizon', 'output_type_id'])

# Save to CSV
output_file = f"/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/{(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')}-LosAlamos_NAU-CModel_Flu.csv"
final_df.to_csv(output_file, index=False)
print(f"Results saved to {output_file}")
