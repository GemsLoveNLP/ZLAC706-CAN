import can

# Initialize the CAN bus with the specific CAN interface for ZLAC706-CAN
can_interface = 'can0'  # Replace with the actual interface like 'can1' or 'vcan0' as per your system
bus = can.interface.Bus(can_interface, bustype='socketcan')

# Function to send a CAN frame
def send_can_frame(bus, can_id, data):
    message = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
    try:
        bus.send(message)
        print(f"Message sent on {bus.channel_info}: {message}")
    except can.CanError:
        print("Message NOT sent")

# Example: Command to set the speed of a motor
# According to the ZLAC706-CAN manual, the command format to set motor speed is as follows:
# CAN ID (0x141): Send command to control motor 1
motor_can_id = 0x1  # Replace with the specific CAN ID for the motor controller

# Data bytes to set speed (example format: 0x31 for speed command, followed by 4 bytes for speed value)
speed_command_data = [0x31, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00]  # Command to set speed to 100 (0x0064)

# Send the speed command to the motor
send_can_frame(bus, motor_can_id, speed_command_data)

# Close the CAN bus connection after sending the command
bus.shutdown()