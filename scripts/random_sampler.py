
from pathlib import Path
import random
import pandas as pd

# Project directories

BASE_DIR = Path(__file__).resolve().parent.parent

name_path = {
    "normal": "normal_run_data.csv",
    "dos": "DoS_dataset.csv",
    "fuzzy": "Fuzzy_dataset.csv",
    "rpm": "RPM_dataset.csv"
}

# Select attack dataset

while True:

    name = input(
        "Enter dataset to sample (dos/fuzzy/rpm): "
    ).lower().strip()

    if name in ["dos", "fuzzy", "rpm"]:
        break

    print("Invalid selection. Enter dos, fuzzy, or rpm.")


# Input files

attack_file = (
    BASE_DIR / "data" / "standardized" / name_path[name]
)

normal_file = (
    BASE_DIR / "data" / "standardized" / name_path["normal"]
)


# Output directories


agent_DIR = (
    BASE_DIR / "data" / "samples" / "random_sample"
)

evaluation_DIR = (
    BASE_DIR / "data" / "samples" / "evaluation"
)

evaluation_attack_DIR = evaluation_DIR / name

agent_DIR.mkdir(parents=True, exist_ok=True)
evaluation_DIR.mkdir(parents=True, exist_ok=True)
evaluation_attack_DIR.mkdir(parents=True, exist_ok=True)


# Sampling settings

sample_duration = 5
sample_amount = 1
random_seed = 42
max_attempt = 5000


rng = random.Random(random_seed)


# Load and prepare datasets

def load_dataset(input_file, is_attack=False):

    df = pd.read_csv(
        input_file,
        dtype={"CAN_ID": str}
    )

    required_columns = [
        "Timestamp",
        "CAN_ID",
        "DLC",
        "DATA0", "DATA1", "DATA2", "DATA3",
        "DATA4", "DATA5", "DATA6", "DATA7"
    ]

    if is_attack:
        required_columns.append("Label")

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns in {input_file.name}: {missing}"
        )

    # Convert timestamps to numeric values
    df["Timestamp"] = pd.to_numeric(
        df["Timestamp"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Timestamp", "CAN_ID", "DLC"]
    )

    # Sort messages chronologically
    df = df.sort_values(
        "Timestamp"
    ).reset_index(drop=True)

    if df.empty:
        raise ValueError(
            f"{input_file.name} contains no valid data."
        )

    # Add normal labels if missing
    if not is_attack and "Label" not in df.columns:
        df["Label"] = "R"

    return df

# Clear previous attack samples

def clear_old_samples(folder):

    removed = 0

    for file in folder.glob("sample_*.csv"):

        if file.is_file():
            file.unlink()
            removed += 1

    print(
        f"Cleared {removed} previous sample file(s) "
        f"from {folder.name}."
    )

# Generate random attack samples

def generate_samples(df, dataset_name):

    first_timestamp = df["Timestamp"].min()
    last_timestamp = df["Timestamp"].max()

    latest_start = last_timestamp - sample_duration

    if latest_start < first_timestamp:
        raise ValueError(
            f"{dataset_name} dataset is too short "
            f"for a {sample_duration}-second sample."
        )

    selected_windows = []
    samples = []

    attempts = 0

    while (
        len(samples) < sample_amount
        and attempts < max_attempt
    ):

        attempts += 1

        start = rng.uniform(
            first_timestamp,
            latest_start
        )

        end = start + sample_duration

        # Prevent overlapping sample windows
        overlaps = any(
            start < previous_end
            and end > previous_start
            for previous_start, previous_end
            in selected_windows
        )

        if overlaps:
            continue

        sample = df[
            (df["Timestamp"] >= start)
            & (df["Timestamp"] < end)
        ].copy()

        if sample.empty:
            continue

        selected_windows.append((start, end))

        samples.append({
            "data": sample,
            "start": start,
            "end": end
        })

    if len(samples) < sample_amount:
        raise RuntimeError(
            f"Only generated {len(samples)} of "
            f"{sample_amount} requested samples."
        )

    return samples

# Generate fixed normal reference

def generate_normal_reference(df):

    normal_agent_file = (
        agent_DIR / "normal_sample.csv"
    )

    normal_evaluation_file = (
        evaluation_DIR / "normal_sample.csv"
    )

    # Reuse existing reference if both copies exist
    if (
        normal_agent_file.exists()
        and normal_evaluation_file.exists()
    ):

        print("\nUsing existing normal reference sample.")
        return

    first_timestamp = df["Timestamp"].min()
    last_timestamp = df["Timestamp"].max()

    end_timestamp = first_timestamp + sample_duration

    if end_timestamp > last_timestamp:
        raise ValueError(
            f"Normal dataset is too short for a "
            f"{sample_duration}-second sample."
        )

    # Select the first time window
    normal_sample = df[
        (df["Timestamp"] >= first_timestamp)
        & (df["Timestamp"] < end_timestamp)
    ].copy()

    if normal_sample.empty:
        raise ValueError(
            "Could not generate a normal reference sample."
        )

    # Save evaluation copy with labels
    normal_sample.to_csv(
        normal_evaluation_file,
        index=False,
        na_rep="NaN"
    )

    # Save agent copy without labels
    normal_sample.drop(
        columns=["Label"]
    ).to_csv(
        normal_agent_file,
        index=False,
        na_rep="NaN"
    )

    print(
        f"\nCreated normal reference with "
        f"{len(normal_sample)} messages over "
        f"{sample_duration} seconds."
    )

# Save attack samples

def save_attack_samples(samples, dataset_name):

    # Clear previous attack samples before saving new ones
    clear_old_samples(agent_DIR)
    clear_old_samples(evaluation_attack_DIR)

    for i, sample_info in enumerate(samples):

        sample = sample_info["data"]

        sample_file = f"sample_{i + 1:03d}.csv"

        # Agent copy without labels
        agent_sample = sample.drop(
            columns=["Label"]
        )

        agent_file = agent_DIR / sample_file

        agent_sample.to_csv(
            agent_file,
            index=False,
            na_rep="NaN"
        )

        # Evaluation copy with labels
        evaluation_file = (
            evaluation_attack_DIR / sample_file
        )

        sample.to_csv(
            evaluation_file,
            index=False,
            na_rep="NaN"
        )

        print(
            f"{sample_file}: "
            f"{len(sample)} messages | "
            f"{sample_info['start']:.6f} to "
            f"{sample_info['end']:.6f}"
        )

# Main execution

try:

    # Validate sampling settings
    if sample_duration <= 0:
        raise ValueError(
            "Sample duration must be greater than zero."
        )

    if sample_amount < 1:
        raise ValueError(
            "Sample amount must be at least 1."
        )

    # Load datasets
    attack_df = load_dataset(
        attack_file,
        is_attack=True
    )

    normal_df = load_dataset(
        normal_file
    )

    # Generate or reuse normal reference
    generate_normal_reference(normal_df)

    # Generate random attack samples
    attack_samples = generate_samples(
        attack_df,
        name
    )

    # Clear old samples and save new ones
    save_attack_samples(
        attack_samples,
        name
    )

    print("\nSampling completed.")
    print(f"Attack dataset: {name}")
    print(f"Attack samples generated: {len(attack_samples)}")
    print(f"Normal reference duration: {sample_duration} seconds")
    print(f"Attack sample duration: {sample_duration} seconds")
    print(f"Random seed: {random_seed}")

except Exception as error:

    print(f"\nSampling error: {error}")
