input_file = "additional resources/../data/standardized/DoS_dataset.csv"

with open(input_file, "r") as f:
    lines = f.readlines()[:100]
    for line in lines:
        print(line)