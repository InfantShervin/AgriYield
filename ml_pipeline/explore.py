import pandas as pd
import os

print("--- EXAMINING DATASETS ---")
base_dir = "Dataset"

def check_csv(filename):
    path = os.path.join(base_dir, filename)
    if os.path.exists(path):
        df = pd.read_csv(path, nrows=3)
        print(f"\n[{filename}] Columns:")
        for col in df.columns:
            print(f"  - {col}")
    else:
        print(f"\n[{filename}] Not found.")

check_csv("crop_yield.csv")
check_csv("Fertilizer.csv")
check_csv("Final_Dataset_after_temperature.csv")
check_csv("final_rainfall.csv")
check_csv("final_temperature.csv")
