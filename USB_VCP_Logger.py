import serial
import struct
import matplotlib.pyplot as plt
import csv
 
# Open the serial port (adjust COM port and baudrate as per your setup)
ser = serial.Serial('COM8', 115200, timeout=1)
 
# To store parsed data
dataA_list = []
dataB_list = []
dataC_list = []
dataD_list = []
 
# Open CSV file for writing
with open('sensor_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write CSV header
    writer.writerow(['DataA', 'DataB', 'DataC', 'DataD'])
    def parse_packet(packet):
        """
        Parse the packet and extract 20-bit data for A, B, C, D
        """
        if packet[:2] == b'\xde\xad' and packet[-2:] == b'\xbe\xef':
            dataA = (packet[2] << 16) | (packet[3] << 8) | packet[4]
            dataB = (packet[5] << 16) | (packet[6] << 8) | packet[7]
            dataC = (packet[8] << 16) | (packet[9] << 8) | packet[10]
            dataD = (packet[11] << 16) | (packet[12] << 8) | packet[13]
            # Handle signed 20-bit values (2's complement)
            dataA = struct.unpack('i', struct.pack('I', dataA << 12)[:4])[0] >> 12
            dataB = struct.unpack('i', struct.pack('I', dataB << 12)[:4])[0] >> 12
            dataC = struct.unpack('i', struct.pack('I', dataC << 12)[:4])[0] >> 12
            dataD = struct.unpack('i', struct.pack('I', dataD << 12)[:4])[0] >> 12
            return dataA, dataB, dataC, dataD
        return None
    def find_packet_start(buffer):
        """
        Look for the start sequence (0xDE 0xAD) in the buffer.
        Returns the index where the packet starts or -1 if not found.
        """
        for i in range(len(buffer) - 1):
            if buffer[i] == 0xDE and buffer[i+1] == 0xAD:
                return i
        return -1
    # Main reading and parsing loop
    buffer = b''
    try:
        while True:
            # Read small chunks from the serial buffer
            buffer += ser.read(16)
            # Ensure we have enough bytes to check for a packet
            if len(buffer) >= 16:
                start_idx = find_packet_start(buffer)
                if start_idx != -1 and len(buffer) >= start_idx + 16:
                    # Extract the potential packet
                    packet = buffer[start_idx:start_idx + 16]
                    # Parse the packet
                    result = parse_packet(packet)
                    if result:
                        dataA, dataB, dataC, dataD = result
                        dataA_list.append(dataA)
                        dataB_list.append(dataB)
                        dataC_list.append(dataC)
                        dataD_list.append(dataD)
                        # Write data to the CSV file
                        writer.writerow([dataA, dataB, dataC, dataD])
                        # Plot the data every 100 packets
                        if len(dataA_list) % 100 == 0:
                            plt.figure(figsize=(10, 8))
                            plt.subplot(4, 1, 1)
                            plt.plot(dataA_list, label='Data A', color='blue')
                            plt.legend()
                            plt.subplot(4, 1, 2)
                            plt.plot(dataB_list, label='Data B', color='green')
                            plt.legend()
                            plt.subplot(4, 1, 3)
                            plt.plot(dataC_list, label='Data C', color='red')
                            plt.legend()
                            plt.subplot(4, 1, 4)
                            plt.plot(dataD_list, label='Data D', color='purple')
                            plt.legend()
                            plt.tight_layout()
                            plt.show()
                    # Remove processed packet from buffer
                    buffer = buffer[start_idx + 16:]
                else:
                    # If no valid start or full packet, keep reading
                    buffer = buffer[-16:]
    except KeyboardInterrupt:
        print("Terminated by user")
    finally:
        ser.close()
