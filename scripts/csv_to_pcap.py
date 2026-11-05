from pathlib import Path
import csv
import struct

#project directories
BASE_DIR = Path(__file__).resolve().parent.parent

input_DIR = BASE_DIR / "data" / "samples" / "random_sample"
output_DIR = BASE_DIR / "captures"

output_DIR.mkdir(parents=True, exist_ok=True)

#SocketCAN pcap link

LINKTYPE_CAN_SOCKETCAN = 227

CAN_FRAME_FORMAT = "<IB3x8s"  

#converts Timestamp into seconds and microseconds for pcap file
def convert_Timestamp(timestamp):
    
    total_microseconds = round(float(timestamp)*1_000_000)
    seconds = total_microseconds // 1_000_000
    microseconds = total_microseconds % 1_000_000
    return seconds, microseconds

#converts CAN ID to SocketCAN id
def convert_can_id(Can_id):

    can_id = int(str(Can_id).strip(), 16)
    
    if can_id < 0 or can_id > 0x1FFFFFFF:
        raise ValueError(f"Invalid CAN ID: {Can_id}")
    
    if can_id > 0x7FF:
        can_id |= 0x80000000  
    
    return can_id

def convert_payload(row,dlc):
    
    payload = bytearray(8)
    
    for i in range(dlc):
        value = row[f"DATA{i}"].strip()
        
        if value.lower() == "nan" or value == "":
            raise ValueError(f"Invalid payload value: {value}")
        
        byte_value = int(value, 16)
        
        if not 0 <= byte_value <= 255:
            raise ValueError(f"Invalid payload byte value: {value}")
        
        payload[i] = byte_value
        
    return bytes(payload)
    
def convert_csv_to_pcap(input_file, output_file):
    with open(input_file, 'r', newline="") as csv_file, \
        open(output_file, 'wb') as pcapfile:
            
        reader = csv.DictReader(csv_file)

        required_columns = ["Timestamp", "CAN_ID", "DLC", "DATA0",
                            "DATA1", "DATA2", "DATA3", "DATA4", "DATA5", "DATA6", "DATA7"]
        
        if not reader.fieldnames or not  all(
            column in reader.fieldnames for column in required_columns  
        ):
            raise ValueError(f"CSV file {input_file} is missing required columns.")
        
        pcapfile.write(
            struct.pack(
                "<IHHIIII",
                0xa1b2c3d4,  
                2,  
                4,  
                0,  
                0,  
                65535,  
                LINKTYPE_CAN_SOCKETCAN
            )
        )
        packet_count = 0
        
        for row in reader:
            timestamp = float(row["Timestamp"])
            can_id = convert_can_id(row["CAN_ID"])
            dlc = int(row["DLC"])
            
            if not 0 <= dlc <= 8:
                raise ValueError(f"Invalid DLC value: {dlc}")
            
            payload = convert_payload(row,dlc)
            
            frame = struct.pack(
                CAN_FRAME_FORMAT,
                can_id,
                dlc,
                payload
            )
            seconds, microseconds = convert_Timestamp(timestamp)
            
            pcapfile.write(
                struct.pack(
                    "<IIII",
                    seconds,
                    microseconds,
                    len(frame),
                    len(frame)
                )
            )
            pcapfile.write(frame)
            
            packet_count += 1
            
    print(f"converted: {input_file.name}")
    print (f"packets written: {packet_count}")
    print(f"Output: {output_file.name}")

for input_file in input_DIR.glob("*csv"):
    
    output_file = output_DIR / f"{input_file.stem}.pcap"
    
    convert_csv_to_pcap(input_file, output_file)
    
print("\n Conversion Complete")