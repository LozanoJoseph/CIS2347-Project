input_file = "additional resources/../data/samples/random_sample/DoS_dataset.csv_sample_001.csv"

with open(input_file, "r") as f:
    lines = f.readlines()[:100]
    for line in lines:
        print(line)