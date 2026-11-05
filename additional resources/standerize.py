from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "data" / "original" / "attacks"
OUTPUT_DIR = BASE_DIR / "data" / "standardized"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

columns = [
    "Timestamp", "CAN_ID", "DLC",
    "DATA0", "DATA1", "DATA2", "DATA3",
    "DATA4", "DATA5", "DATA6", "DATA7",
    "Label"
]

for file in INPUT_DIR.glob("*.csv"):

    rows = []

    with open(file, "r") as f:
        for line_number, line in enumerate(f, start=1):

            parts = line.strip().split(",")

            if not line.strip():
                continue

            try:
                timestamp = parts[0]
                can_id = parts[1].zfill(4)
                dlc = int(parts[2])

                # Extract only the actual payload bytes
                payload = parts[3:3 + dlc]

                # Extract the final normal/attack label
                label = parts[3 + dlc]

                # Add NaN for unused payload positions
                payload += ["NaN"] * (8 - dlc)

                rows.append([
                    timestamp,
                    can_id,
                    dlc,
                    *payload,
                    label
                ])

            except (IndexError, ValueError) as e:
                print(f"Skipping {file.name}, line {line_number}: {e}")

    df = pd.DataFrame(rows, columns=columns)

    output_file = OUTPUT_DIR / file.name

    df.to_csv(output_file, index=False, na_rep="NaN")

    print(f"Standardized: {file.name}")

print("Finished standardizing datasets!")