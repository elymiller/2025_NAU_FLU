import sys
import pandas as pd

def replace_zero_values(csv_path: str):
    # Load the CSV into a DataFrame
    df = pd.read_csv(csv_path)
    
    # Replace 0.0 with 1.0 in the 'value' column
    df.loc[df['value'] == 0.0, 'value'] = 1.0
    
    # Save back to the same file (no index column)
    df.to_csv(csv_path, index=False)
    print(f"Replaced zeros and saved to {csv_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python replace_values.py <path/to/your.csv>")
        sys.exit(1)
    replace_zero_values(sys.argv[1])
