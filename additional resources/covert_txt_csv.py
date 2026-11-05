import pandas as pd
import numpy as np

input_file = "C:\\School\\CIS2347\\Project\\9) Car-Hacking Dataset\\normal_run_data\\normal_run_data.txt"
rows = []

with open(input_file, "r") as f:
    for line in f:
        part = line.split()
        if not part:
            continue
        
        timestamp = part[1]
        can_id = part[3]
        extra = part[4]
        dlc = int(part[6])
        data = [np.nan] * 8
        
        for i, byte in enumerate(part[7:7 + dlc]):
            if byte:
                data[i] = byte.zfill(2)
        rows.append((timestamp, can_id, extra, dlc, *data))
        
columns = ["timestamp", "CAN_ID", "extra", "DLC", "Data_0", "Data_1", "Data_2", "Data_3", "Data_4", "Data_5", "Data_6", "Data_7"]
df = pd.DataFrame(rows, columns=columns)
df.to_csv("C:\\School\\CIS2347\\Project\\9) Car-Hacking Dataset\\normal_run_data\\normal_run_data.csv", index=False, na_rep="NaN")
print("Conversion completed successfully.")
print(df.head())