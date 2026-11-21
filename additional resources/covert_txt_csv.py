
import pandas as pd
import numpy as np

input_file = "data\\original\\normal_run_data\\normal_run_data.txt"
output_file = "data\\standardized\\normal_run_data.csv"

rows = []

with open(input_file, "r") as f:
    for line in f:
        part = line.split()

        if not part:
            continue

        timestamp = part[1]
        can_id = part[3]
        dlc = int(part[6])

        data = [np.nan] * 8

        for i, byte in enumerate(part[7:7 + dlc]):
            if byte:
                data[i] = byte.zfill(2)

        rows.append((timestamp, can_id, dlc, *data))

columns = [
    "Timestamp", "CAN_ID", "DLC",
    "DATA0", "DATA1", "DATA2", "DATA3",
    "DATA4", "DATA5", "DATA6", "DATA7"
]

df = pd.DataFrame(rows, columns=columns)

df.to_csv(output_file, index=False, na_rep="NaN")

print("Conversion completed successfully.")
print(df.head())