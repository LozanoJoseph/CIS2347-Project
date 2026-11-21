
from pathlib import Path
import json
import shutil
import pandas as pd


# Project directories

BASE_DIR = Path(__file__).resolve().parent.parent

SAMPLE_DIR = (
    BASE_DIR / "data" / "samples" / "random_sample"
)

ANALYSIS_DIR = (
    BASE_DIR / "data" / "analysis"
)

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


# Dataset settings

DATA_COLUMNS = [
    "DATA0", "DATA1", "DATA2", "DATA3",
    "DATA4", "DATA5", "DATA6", "DATA7"
]

REQUIRED_COLUMNS = [
    "Timestamp",
    "CAN_ID",
    "DLC",
    *DATA_COLUMNS
]

# Load and prepare dataset

def load_dataset(input_file):

    df = pd.read_csv(
        input_file,
        dtype={"CAN_ID": str}
    )

    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
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

    df["DLC"] = pd.to_numeric(
        df["DLC"],
        errors="coerce"
    )

    # Remove rows without essential information
    df = df.dropna(
        subset=["Timestamp", "CAN_ID", "DLC"]
    ).copy()

    # Normalize CAN IDs
    df["CAN_ID"] = (
        df["CAN_ID"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Sort messages chronologically
    df = df.sort_values(
        "Timestamp"
    ).reset_index(drop=True)

    if df.empty:
        raise ValueError(
            f"{input_file.name} contains no valid messages."
        )

    # Build payload from the eight data bytes
    df["Payload"] = df[DATA_COLUMNS].fillna("").apply(
        lambda row: " ".join(
            str(value).strip().upper()
            for value in row
            if str(value).strip()
        ),
        axis=1
    )

    return df

# General statistics

def calculate_general_statistics(df):

    timestamps = df["Timestamp"]

    total_messages = len(df)

    start_time = timestamps.min()
    end_time = timestamps.max()

    observed_span = end_time - start_time

    messages_per_second = (
        total_messages / observed_span
        if observed_span > 0 else 0
    )

    inter_arrival = (
        timestamps.diff().dropna() * 1000
    )

    can_id_frequency = (
        df["CAN_ID"].value_counts()
    )

    dlc_distribution = (
        df["DLC"].value_counts().sort_index()
    )

    return {

        "total_messages": int(total_messages),

        "start_timestamp": float(start_time),

        "end_timestamp": float(end_time),

        "observed_duration_seconds": round(
            float(observed_span), 6
        ),

        "messages_per_second": round(
            float(messages_per_second), 3
        ),

        "unique_can_ids": int(
            df["CAN_ID"].nunique()
        ),

        "can_id_frequency": {
            str(key): int(value)
            for key, value in can_id_frequency.items()
        },

        "unique_payloads": int(
            df["Payload"].nunique()
        ),

        "average_inter_arrival_ms": (
            round(float(inter_arrival.mean()), 6)
            if not inter_arrival.empty else 0
        ),

        "minimum_inter_arrival_ms": (
            round(float(inter_arrival.min()), 6)
            if not inter_arrival.empty else 0
        ),

        "maximum_inter_arrival_ms": (
            round(float(inter_arrival.max()), 6)
            if not inter_arrival.empty else 0
        ),

        "std_inter_arrival_ms": (
            round(float(inter_arrival.std()), 6)
            if len(inter_arrival) > 1 else 0
        ),

        "dlc_distribution": {
            str(int(key)): int(value)
            for key, value in dlc_distribution.items()
        }

    }

# Per-second statistics

def calculate_per_second_statistics(df):

    data = df.copy()

    # Create elapsed-second bins
    data["Elapsed_Second"] = (
        data["Timestamp"] - data["Timestamp"].min()
    ).apply(lambda value: int(value))

    results = []

    for second, group in data.groupby("Elapsed_Second"):

        can_id_frequency = (
            group["CAN_ID"].value_counts().to_dict()
        )

        unique_payloads_by_id = (
            group.groupby("CAN_ID")["Payload"]
            .nunique()
            .to_dict()
        )

        dlc_distribution = (
            group["DLC"].value_counts().sort_index()
        )

        byte_diversity = {}

        for column in DATA_COLUMNS:

            byte_diversity[column] = int(
                group[column]
                .dropna()
                .astype(str)
                .nunique()
            )

        results.append({

            "second": int(second),

            "message_count": int(len(group)),

            "unique_can_ids": int(
                group["CAN_ID"].nunique()
            ),

            "unique_payloads": int(
                group["Payload"].nunique()
            ),

            "can_id_frequency": {
                str(key): int(value)
                for key, value in can_id_frequency.items()
            },

            "unique_payloads_by_can_id": {
                str(key): int(value)
                for key, value in unique_payloads_by_id.items()
            },

            "dlc_distribution": {
                str(int(key)): int(value)
                for key, value in dlc_distribution.items()
            },

            "byte_value_diversity": byte_diversity

        })

    return results

# Per-CAN-ID statistics

def calculate_can_id_statistics(df):

    results = []

    for can_id, group in df.groupby("CAN_ID"):

        timestamps = group["Timestamp"]

        inter_arrival = (
            timestamps.diff().dropna() * 1000
        )

        payload_frequency = (
            group["Payload"].value_counts()
        )

        dlc_distribution = (
            group["DLC"].value_counts().sort_index()
        )

        results.append({

            "CAN_ID": str(can_id),

            "message_count": int(len(group)),

            "percentage_of_traffic": round(
                len(group) / len(df) * 100, 4
            ),

            "average_inter_arrival_ms": (
                round(float(inter_arrival.mean()), 6)
                if not inter_arrival.empty else 0
            ),

            "minimum_inter_arrival_ms": (
                round(float(inter_arrival.min()), 6)
                if not inter_arrival.empty else 0
            ),

            "maximum_inter_arrival_ms": (
                round(float(inter_arrival.max()), 6)
                if not inter_arrival.empty else 0
            ),

            "std_inter_arrival_ms": (
                round(float(inter_arrival.std()), 6)
                if len(inter_arrival) > 1 else 0
            ),

            "unique_payloads": int(
                group["Payload"].nunique()
            ),

            "most_frequent_payload": (
                str(payload_frequency.index[0])
                if not payload_frequency.empty else None
            ),

            "most_frequent_payload_count": (
                int(payload_frequency.iloc[0])
                if not payload_frequency.empty else 0
            ),

            "most_frequent_payload_percentage": (
                round(
                    payload_frequency.iloc[0] / len(group) * 100,
                    4
                )
                if not payload_frequency.empty else 0
            ),

            "dlc_distribution": json.dumps({
                str(int(key)): int(value)
                for key, value in dlc_distribution.items()
            })

        })

    return pd.DataFrame(results)


# Analyze one dataset

def analyze_dataset(input_file):

    print(f"\nAnalyzing {input_file.name}...")

    df = load_dataset(input_file)

    general_statistics = (
        calculate_general_statistics(df)
    )

    per_second_statistics = (
        calculate_per_second_statistics(df)
    )

    can_id_statistics = (
        calculate_can_id_statistics(df)
    )

    return {

        "file": input_file.name,

        "general": general_statistics,

        "per_second": per_second_statistics,

        "per_can_id": can_id_statistics

    }

# Save analysis results

def save_analysis_results(results, output_dir):

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save general and per-second statistics
    json_results = {
        "file": results["file"],
        "general": results["general"],
        "per_second": results["per_second"]
    }

    json_file = output_dir / "statistics.json"

    with open(
        json_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            json_results,
            file,
            indent=4
        )

    # Save per-CAN-ID statistics
    csv_file = output_dir / "can_id_statistics.csv"

    results["per_can_id"].to_csv(
        csv_file,
        index=False
    )

# Main execution

try:

    # Locate normal reference
    normal_file = SAMPLE_DIR / "normal_sample.csv"

    if not normal_file.exists():

        raise FileNotFoundError(
            "normal_sample.csv was not found. "
            "Run random_sampler.py first."
        )

    # Locate attack samples
    attack_files = sorted(
        SAMPLE_DIR.glob("sample_*.csv")
    )

    if not attack_files:

        raise FileNotFoundError(
            "No attack samples were found. "
            "Run random_sampler.py first."
        )

    # Clear previous analysis results
    for folder in ANALYSIS_DIR.iterdir():

        if folder.is_dir() and (
            folder.name == "normal_sample"
            or folder.name.startswith("sample_")
        ):

            shutil.rmtree(folder)

    # Analyze normal reference

    print("\n========== NORMAL REFERENCE ==========")

    normal_results = analyze_dataset(
        normal_file
    )

    save_analysis_results(
        normal_results,
        ANALYSIS_DIR / "normal_sample"
    )

    print("Normal reference analysis completed.")

    # Analyze attack samples

    for attack_file in attack_files:

        print(
            f"\n========== {attack_file.name} =========="
        )

        attack_results = analyze_dataset(
            attack_file
        )

        output_DIR = (
            ANALYSIS_DIR / attack_file.stem
        )

        save_analysis_results(
            attack_results,
            output_DIR
        )

        print(
            f"Analysis completed for {attack_file.name}."
        )

    # Completion

    print("\n======================================")
    print("CAN traffic analysis completed.")
    print("Normal reference: analyzed")
    print(f"Attack samples analyzed: {len(attack_files)}")
    print(f"Results saved to: {ANALYSIS_DIR}")
    print("======================================")

except Exception as error:

    print(f"\nAnalysis error: {error}")
