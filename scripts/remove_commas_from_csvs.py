import pandas as pd
import os

def remove_commas_from_csvs(input_dir, output_dir):
    for file in os.listdir(input_dir):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(input_dir, file))
            df = df.replace(r',', '', regex=True)
            df.to_csv(os.path.join(output_dir, file), index=False)

if __name__ == '__main__':
    remove_commas_from_csvs('/Users/elymiller/Desktop/Current_Research/2025_NAU_FLU/', '/Users/elymiller/Desktop/Current_Research/2025_NAU_FLU/cleaned_csvs/')