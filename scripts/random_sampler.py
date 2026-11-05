from pathlib import Path
import random
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

name_path = {
    "normal": "normal_run_data.csv",
    "dos": "DoS_dataset.csv",
    "fuzzy": "Fuzzy_dataset.csv",
    "rpm": "RPM_dataset.csv"
}

while True:
    name = input("Enter the name of the CSV file to sample (normal/dos/fuzzy/rpm): ")
    if name in ["normal", "dos", "fuzzy", "rpm"]:
        break
    else:
        print("Invalid file name. Please enter a valid file name.")
        


input_file = BASE_DIR / "data" / "standardized" / f"{name_path[name]}"

agent_DIR = BASE_DIR / "data" / "samples" / "random_sample"

evaluation_DIR = BASE_DIR / "data" / "samples" / "evaluation"

agent_DIR.mkdir(parents=True, exist_ok=True)
evaluation_DIR.mkdir(parents=True, exist_ok=True)

#sample settings

sample_duration = 10
sample_amount = 3
random_seed = 42
max_attempt = 5000

rng = random.Random(random_seed)

df = pd.read_csv(
    input_file,
    dtype ={"CAN_ID": str}
)

required_columns = ["Timestamp", "CAN_ID","DLC", "Label"]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(f"Missing columns in the DataFrame: {missing}")

#convert Timestamps to numbers then sorts
df["Timestamp"] = pd.to_numeric(df["Timestamp"], errors="coerce")
df = df.dropna(subset=["Timestamp"])
df = df.sort_values("Timestamp").reset_index(drop=True)

if df.empty:
    raise ValueError("The DataFrame contains no data.")

#finds the range of Timestamps
first_timestamp = df["Timestamp"].min()
last_timestamp = df["Timestamp"].max()

latest_start = last_timestamp - sample_duration

if latest_start < first_timestamp:
    raise ValueError("The requested sample duration is too long for the available data.")

selected_windows = []
successful_samples = 0
attempts = 0

#choose a random starting sample
while successful_samples < sample_amount and attempts < max_attempt:
    attempts += 1
    start = rng.uniform(first_timestamp, latest_start)
    end = start + sample_duration
    
    #prevent overlap
    overlaps = any(
        start < previous_end and end > previous_start
        for previous_start, previous_end in selected_windows
    )
    
    if overlaps:
        continue
    
    sample = df[
        (df["Timestamp"] >= start) & (df["Timestamp"] < end)
    ].copy()
    
    if sample.empty:
        continue
    
    successful_samples +=1
    selected_windows.append((start, end))
    
    sample_id = f"sample_{successful_samples:03d}"
    
    # saves evaluation sample with flag labels
    evaluation_file = evaluation_DIR / f"{name}_{sample_id}.csv"
    sample.to_csv(evaluation_file, index=False, na_rep="NaN")
    
    agent_sample = sample.drop(columns=["Label"])
    agent_file = agent_DIR / f"{name}_{sample_id}.csv"
    agent_sample.to_csv(agent_file, index=False, na_rep="NaN")
    
    print(
            f"{sample_id}: "
            f"{len(sample)} messages | "
            f"{start:.6f} to {end:.6f}"         
          
          )

print("\n sampling completed.")
print(f"samples generated: {successful_samples}/{sample_amount}")
print(f"Random seed used: {random_seed}")

if successful_samples < sample_amount:
    print(f"Only {successful_samples} out of {sample_amount} requested samples were generated.")
