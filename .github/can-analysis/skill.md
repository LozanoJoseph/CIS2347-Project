---
name: can-analysis
description: Investigate CAN bus PCAP captures using TShark. Identify unusual CAN message frequencies, identifiers, payload patterns, and timing behavior that may indicate DoS, fuzzy, or spoofing attacks.

---
Use the instructions in `.github/skills/can-analysis/SKILL.md` to inspect the PCAP file located in the `captures` folder.

Use TShark to examine the individual CAN frames. Identify any potentially suspicious packets and explain why they may be suspicious.

For every flagged packet, provide:
- Frame number
- Timestamp
- CAN ID
- DLC
- Payload
- Reason for flagging

Do not calculate message frequencies or other statistical measurements. Do not use the dataset's ground-truth labels. Verify the packet details against the original capture before reporting your findings.