# AI-Powered CAN Network Traffic Analysis

## Overview

This project explores the use of an AI agent to analyze Controller Area Network (CAN) traffic from connected vehicles and 
identifies potentially suspicious network activity.

For this project the HCRL car-hacking dataset was used to exam the CAN traffic utilizing extra programs to organize the data,
this dataset focuses on simulated attack traffic including Denial of Service (DoS), Fuzzing, RPM spoofing, and gear Spoofing.

The AI agent uses Python-based analysis tools and Wireshark/TShark to examine traffic patterns, investigate unusual CAN messages, and explain its findings.

## Objectives

- Analyze normal and potentially malicious CAN network traffic.
- Use an AI agent with custom instructions to investigate network activity.
- Identify unusual message frequencies, CAN IDs, payloads, and timing patterns.
- Use Wireshark/TShark for packet-level traffic inspection.
- Evaluate the agent's ability to recognize and explain different attack behaviors.

## Technologies Used

- Python
- Pandas
- Wireshark
- TShark
- GitHub Copilot Agent
- HCRL Car-Hacking Dataset

## Supported Attack Types

| Attack Type | Description |
|---|---|
| DoS | Floods the CAN network with messages to disrupt normal communication. |
| Fuzzy | Injects random or unexpected CAN IDs and payload values. |
| RPM Spoofing | Manipulates engine RPM-related CAN messages. |
| Gear Spoofing | Manipulates the engine Gears CAN messages. |

## Project Structure

project/
├── .github/
│   └── skills/
│       └── can-analysis/
│           └── SKILL.md
├── additional resources/
│   ├── convert_txt_csv.py
│   ├── standardize.py
│   └── tester.py
│
├── captures/
│
├── data/
│   ├── analysis/
│   ├── original/
│   │   ├── attacks/
│   │   │   └── DoS_dataset.csv
│   │   │   └── Fuzzy_dataset.csv
│   │   │   └── gear_dataset.csv
│   │   │   └── RPM_dataset.csv 
│   │   └── normal_run_data/
│   │   │   └── normal_run_data.txt
│   ├── samples/
│   │   └── evaluation/
│   │   └── random_sample/
│   ├── standardized/
│   │   └── DoS_dataset.csv
│   │   └── Fuzzy_dataset.csv
│   │   └── gear_dataset.csv
│   │   └── RPM_dataset.csv 
│   │   └── normal_run_data.csv 
├── scripts/
│   ├── analyze_can.py
│   ├── csv_to_pcap.py
│   └── random_sampler.py
│
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10 or later
- Wireshark and TShark
- Git
- GitHub Copilot with agent and custom skill support

## Installation

1. Clone the repository:

   ```bash
   git clone REPOSITORY_URL
   ```

2. Navigate to the project directory:

   ```bash
   cd PROJECT_DIRECTORY
   ```

3. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Install Wireshark and ensure TShark is accessible through your system PATH.

5. Verify the installation:

   ```bash
   tshark --version
   ```

## Usage

### 1. Prepare Traffic Samples

Run the random sampler:

```bash
python scripts/random_sampler.py
```

Select the attack dataset to sample:

- `dos`
- `fuzzy`
- `rpm`
- `gear`

The script generates a fixed normal reference sample and randomly selected attack samples using the configured sampling duration.

### 2. Convert Samples to PCAP

Run the CSV-to-PCAP conversion script:

```bash
python scripts/csv_to_pcap.py
```

The generated PCAP files can be inspected using Wireshark or TShark.

### 3. AI Agent Investigation

Use the custom `can-analysis` skill with GitHub Copilot Agent.

The agent uses the generated statistical results and packet captures to:

- Examine normal and unknown traffic patterns.
- Compare traffic statistics.
- Investigate unusual CAN IDs and payloads.
- Identify potentially suspicious message timing and frequency.
- Explain findings and possible attack behaviors.

## Dataset

This project uses the HCRL Car-Hacking Dataset.

The dataset contains normal CAN traffic and simulated attack traffic, including DoS, Fuzzy, and RPM spoofing.

Dataset source: [HCRL Car-Hacking Dataset](https://ocslab.hksecurity.net/Datasets/car-hacking-dataset)

## Evaluation

The agent's findings are evaluated against the original dataset labels.

Evaluation measurements may include:

- Accuracy
- Precision
- Recall
- F1-score
- True Positives
- True Negatives
- False Positives
- False Negatives

Ground-truth labels are kept separate from the agent's input data to prevent the agent from using the expected classifications during its investigation.

## Disclaimer

This project is intended for educational and research purposes. It focuses on analyzing recorded CAN traffic and does not interact with or modify live vehicle networks.