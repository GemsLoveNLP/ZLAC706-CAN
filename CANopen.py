import can

class ZLAC8015D:
    def __init__(self, can_interface="can0", node_id=1, bitrate=500000):
        self.can_interface = can_interface
        self.node_id = node_id
        self.bitrate = bitrate
        self.bus = can.interface.Bus(channel=can_interface, bustype="socketcan", bitrate=bitrate)

        # Basic Configuration
        self.OPR_MODE = 0x6060
        self.CONTROL_REG = 0x6040
        self.STATUS_REG = 0x6041
        self.HEARTBEAT = 0x1017
        self.TARGET_VELOCITY = 0x60FF
        self.ACTUAL_VELOCITY = 0x606C
        self.TARGET_POSITION = 0x607A
        self.MAX_SPEED = 0x6081
        self.EMERGENCY_STOP = 0x02

    def send_message(self, cob_id, data):
        """
        Sends a CANopen message.
        """
        message = can.Message(arbitration_id=cob_id, data=data, is_extended_id=False)
        self.bus.send(message)

    def set_mode(self, mode):
        """
        Set operating mode (velocity, position, torque).
        """
        cob_id = 0x600 + self.node_id
        data = [0x2F, 0x60, 0x60, 0x00, mode, 0x00, 0x00, 0x00]
        self.send_message(cob_id, data)

    def enable_motor(self):
        """
        Enables the motor driver.
        """
        cob_id = 0x600 + self.node_id
        data = [0x2B, 0x40, 0x60, 0x00, 0x0F, 0x00, 0x00, 0x00]
        self.send_message(cob_id, data)

    def disable_motor(self):
        """
        Disables the motor driver.
        """
        cob_id = 0x600 + self.node_id
        data = [0x2B, 0x40, 0x60, 0x00, 0x07, 0x00, 0x00, 0x00]
        self.send_message(cob_id, data)

    def set_velocity(self, left_rpm, right_rpm):
        """
        Sets target velocities for the left and right motors.
        """
        cob_id = 0x600 + self.node_id
        left_bytes = left_rpm.to_bytes(4, byteorder="little", signed=True)
        right_bytes = right_rpm.to_bytes(4, byteorder="little", signed=True)
        data = [0x23, 0xFF, 0x60, 0x03] + list(left_bytes) + list(right_bytes)
        self.send_message(cob_id, data)

    def get_velocity(self):
        """
        Reads actual velocities of the left and right motors.
        """
        cob_id = 0x580 + self.node_id
        self.send_message(0x600 + self.node_id, [0x40, 0x6C, 0x60, 0x03])
        message = self.bus.recv(timeout=1)
        if message and message.arbitration_id == cob_id:
            left_rpm = int.from_bytes(message.data[:4], "little", signed=True)
            right_rpm = int.from_bytes(message.data[4:], "little", signed=True)
            return left_rpm, right_rpm
        return None, None

    def set_position(self, left_position, right_position):
        """
        Sets target positions for the motors.
        """
        cob_id = 0x600 + self.node_id
        left_bytes = left_position.to_bytes(4, byteorder="little", signed=True)
        right_bytes = right_position.to_bytes(4, byteorder="little", signed=True)
        data = [0x23, 0x7A, 0x60, 0x01] + list(left_bytes) + list(right_bytes)
        self.send_message(cob_id, data)

    def start_position_motion(self):
        """
        Starts motion to the target position.
        """
        cob_id = 0x600 + self.node_id
        data = [0x2B, 0x40, 0x60, 0x00, 0x0F, 0x00, 0x00, 0x00]
        self.send_message(cob_id, data)

    def set_heartbeat(self, interval_ms=1000):
        """
        Sets the heartbeat message interval.
        """
        cob_id = 0x600 + self.node_id
        interval_bytes = interval_ms.to_bytes(2, "little")
        data = [0x2B, 0x17, 0x10, 0x00] + list(interval_bytes) + [0x00, 0x00]
        self.send_message(cob_id, data)

    def read_heartbeat_status(self):
        """
        Reads the status of the heartbeat.
        """
        cob_id = 0x700 + self.node_id
        message = self.bus.recv(timeout=1)
        if message and message.arbitration_id == cob_id:
            return message.data[0]
        return None

    def read_status(self):
        """
        Reads the status word and interprets bits.
        """
        cob_id = 0x580 + self.node_id
        self.send_message(0x600 + self.node_id, [0x40, 0x41, 0x60, 0x00])
        message = self.bus.recv(timeout=1)
        if message and message.arbitration_id == cob_id:
            status_word = int.from_bytes(message.data[:2], "little")
            return {
                "ready_to_switch_on": bool(status_word & 0x01),
                "switched_on": bool(status_word & 0x02),
                "operation_enabled": bool(status_word & 0x04),
                "fault": bool(status_word & 0x08),
                "voltage_enabled": bool(status_word & 0x10),
                "quick_stop": bool(status_word & 0x20),
                "switch_on_disabled": bool(status_word & 0x40),
                "warning": bool(status_word & 0x80),
            }
        return None

    def get_fault_code(self):
        """
        Reads and interprets the fault code.
        """
        cob_id = 0x600 + self.node_id
        self.send_message(cob_id, [0x40, 0x3F, 0x60, 0x00])
        message = self.bus.recv(timeout=1)
        if message and message.arbitration_id == (0x580 + self.node_id):
            fault_code = int.from_bytes(message.data[:4], "little")
            return fault_code
        return None

    def close(self):
        """
        Shuts down the CAN bus.
        """
        self.bus.shutdown()
