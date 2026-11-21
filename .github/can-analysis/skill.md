---
name: can-analysis
description: Analyzes CAN network traffic using Python statistical analysis and Wireshark TShark packet inspection to identify suspicious behavior and possible vehicle network attacks.
---

---
# CAN Traffic Analysis

## Purpose

This skill enables the AI agent to investigate Controller Area Network (CAN) traffic using statistical analysis and packet-level inspection.

The objective is to identify unusual CAN traffic behavior, investigate suspicious messages, and determine whether the observed behavior resembles a known vehicle network attack.

The agent is responsible for interpreting the results, comparing samples, identifying suspicious behavior, and providing a final evaluation. Do not assume that a sample contains an attack. All conclusions must be supported by observed evidence.
---

## Files and Tools
- Analysis script: `scripts/analyze_can.py`
- Samples: 'data/samples/random_sample/'
- Statistical results: 'data/analysis/'
- PCAP captures: 'data/captures/'

## Investigation Workflow

Follow each stage in order. Do not skip stages unless a required file or tool is unavailable. If something is unavailable, explain the issue and continue only when doing so will not compromise the investigation.

### Stage 1: Generate Statistical Analysis

Run the provided Python analysis script:

```powershell
python scripts/analyze_can.py
```

The script analyzes:

- The normal reference sample.
- Every available attack sample.

### Stage 2: Observe the Statistical Results

Read the generated `statistics.json` and `can_id_statistics.csv` files for the normal reference and each attack sample.

Observe the evaluated statistics for the overall traffic, per-second behavior, and individual CAN ID statistics

At this stage, focus on understanding the measurements. Do not immediately classify any sample as malicious.

### Stage 3: Evaluate and Compare the Statistics

Compare each attack sample against the normal reference sample.

Identify differences that may indicate unusual CAN network behavior.

Consider the following areas:

- Traffic frequency
- CAN ID distribution
- Payload diversity
- Message timing
- inter-arrival time statistics
- DLC Distribution

Explain what the differences could indicate and whether they rquire further investigation. Do not assume that a difference indicates an attack. Some differences may be benign or expected and consider multiple mesurements together to determine whether the behavior is unusual.

### Stage 4: Identify Suspicious Samples

After comparing the statistical results, determine whether each sample deserves further investigation.

For every suspicious sample, identify:

1. The sample filename.
2. The unusual measurements.
3. How those measurements differ from normal traffic.
4. The affected CAN IDs, if applicable.
5. The specific time intervals that deserve further investigation.
6. Why the observed behavior may indicate suspicious activity.

Do not claim that an attack has been confirmed based only on statistical differences.

### Stage 5: Inspect Suspicious PCAP Files Using TShark

For each suspicious sample, locate and inspect its corresponding PCAP file inside the folder named captures using TShark.

Use the Statiscial findings to guide packet inpection.

Use TShark to display the packet summary:

```powershell
tshark -r captures/sample_001.pcap
```

Inspect individual frames using:

```powershell
tshark -r captures/sample_001.pcap -Y "frame.number == 25" -V
```
explain:
- which frames are suspicious.
- Their timestamps, CAN IDs, and payloads.
- Why the frames are suspicious.
- Whether the packet-level evidence supports the statistical findings.

Do not assume a frame is malicious without supporting evidence

### Stage 6: Final Evaluation and Attack Identification

After completing the statistical and packet-level investigation, determine what the observed behavior most closely resembles.

Consider the following attack types.

- Denial of Service (DoS)
- Fuzzy Attack
- RPM Spoofing
- Gear Spoofing

Possible indicators:

- Unusual payload changes associated with an existing CAN ID.
- Repeated or manipulated values that may represent altered engine RPM or Drive Gear information.
- Payload behavior that differs from the normal reference.

These indicators are not definitive rules. Similar behavior can have other explanations.

## Final Report Format

After investigating all available samples, provide a report using the following structure.

# Sample Findings

for each sample

- Sample filename.
- important statisical observation.
- suspicous behavior indentified, if any.
- relevent PCAP frame numbers and evidence.
- Assesment of possible attack type. 

# Overall evaluation

Summerize:

- Which samples were suspicious or normal
- Which possible attack types were identified
- The strongest evidence supporting the findings
- Any inconclusive results.

## Important Rules

1. Always run `analyze_can.py` before evaluating statistical results.
2. Use the normal reference sample as the baseline for comparisons.
3. The Python analysis script calculates statistics only. The AI agent is responsible for interpreting them.
4. Do not modify or invent statistical measurements.
5. Do not access ground-truth labels or evaluation files.
6. Do not assume every attack sample will contain obvious suspicious behavior.
7. Do not classify traffic based on a single measurement.
8. Use TShark to investigate suspicious samples at the packet level.
9. Support conclusions with specific measurements, CAN IDs, timestamps, and frame numbers whenever possible.
10. Clearly distinguish observed evidence from assumptions.
11. Do not force an attack classification when the evidence is insufficient.
12. Include the commands used during the investigation so the analysis can be reproduced.