import serial
import struct
import matplotlib.pyplot as plt
import csv

# Open the serial port (adjust COM port and baudrate as per your setup)
ser = serial.Serial('COM8', 115200, timeout=1)

# To store parsed data (rolling window with max 2000 samples)
dataA_list = []
dataB_list = []
dataC_list = []
dataD_list = []

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

# Set up the live plot
plt.ion()  # Enable interactive mode
fig, axes = plt.subplots(4, 1, figsize=(10, 8))

# Initialize empty plots for each data stream
lineA, = axes[0].plot([], [], label='Data A', color='blue')
lineB, = axes[1].plot([], [], label='Data B', color='green')
lineC, = axes[2].plot([], [], label='Data C', color='red')
lineD, = axes[3].plot([], [], label='Data D', color='purple')

for ax in axes:
    ax.set_xlim(0, 2000)  # Start with a default x-axis limit of 2000 samples
    ax.legend()

# Main reading and parsing loop
buffer = b''
update_interval = 100  # Update the plot every 30 samples
sample_counter = 0
max_samples = 2000  # Maximum number of samples to display on x-axis

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

                    sample_counter += 1  # Increment sample counter
                    
                    # If we have more than 2000 samples, remove the oldest ones
                    if len(dataA_list) > max_samples:
                        dataA_list = dataA_list[-max_samples:]
                        dataB_list = dataB_list[-max_samples:]
                        dataC_list = dataC_list[-max_samples:]
                        dataD_list = dataD_list[-max_samples:]

                    # Only update plot every `update_interval` samples
                    if sample_counter % update_interval == 0:
                        # Update the plot data with the last 2000 samples
                        lineA.set_data(range(len(dataA_list)), dataA_list)
                        lineB.set_data(range(len(dataB_list)), dataB_list)
                        lineC.set_data(range(len(dataC_list)), dataC_list)
                        lineD.set_data(range(len(dataD_list)), dataD_list)

                        # Adjust x-axis limits to always display the last 2000 samples
                        for ax in axes:
                            ax.set_xlim(0, max_samples)

                        # Autoscale the y-axis based on the data
                        for ax in axes:
                            ax.relim()  # Recalculate limits based on new data
                            ax.autoscale_view()  # Autoscale the view based on recalculated limits

                        # Redraw the plot
                        plt.pause(0.001)  # Small pause to allow for the plot update

                # Remove processed packet from buffer
                buffer = buffer[start_idx + 16:]
            else:
                # If no valid start or full packet, keep reading
                buffer = buffer[-16:]

except KeyboardInterrupt:
    print("Terminated by user")

finally:
    ser.close()
    plt.ioff()  # Disable interactive mode
    plt.show()  # Show the final plot when done
