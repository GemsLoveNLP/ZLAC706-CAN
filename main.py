import sys
import termios
import tty
from CANOpen import ZLAC8015D  # Assuming your class is in a file named zlac8015d.py

def get_key():
    """
    Reads a single key press from standard input.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

def main():
    # Setup the driver
    node_id = 1
    can_interface = "can0"  # Adjust this to match your setup
    zlac = ZLAC8015D(can_interface=can_interface, node_id=node_id)

    # Initialize the driver
    zlac.clear_alarm()
    zlac.set_mode(zlac.VEL_CONTROL)
    zlac.enable_motor()

    print("WASD Control:\n"
          "W - Forward\n"
          "S - Backward\n"
          "A - Left Spin\n"
          "D - Right Spin\n"
          "Ctrl+C to quit.")

    try:
        while True:
            key = get_key()

            if key.lower() == 'w':  # Forward
                print("Driving forward")
                zlac.set_rpm(100, 100)  # Adjust RPM as needed
            elif key.lower() == 's':  # Backward
                print("Driving backward")
                zlac.set_rpm(-100, -100)
            elif key.lower() == 'a':  # Left spin
                print("Spinning left")
                zlac.set_rpm(100, -100)
            elif key.lower() == 'd':  # Right spin
                print("Spinning right")
                zlac.set_rpm(-100, 100)
            elif key.lower() == 'q':  # Quit
                print("Quitting...")
                break
            else:
                # Stop motors for unknown input
                print("Stopping")
                zlac.set_rpm(0, 0)

            # Get and print RPM feedback
            left_rpm, right_rpm = zlac.get_rpm()
            print(f"Feedback RPM - Left: {left_rpm}, Right: {right_rpm}")

    except KeyboardInterrupt:
        print("\nExiting on user interrupt.")
    finally:
        # Stop the motors and disable the driver on exit
        zlac.set_rpm(0, 0)
        zlac.disable_motor()
        zlac.close()

if __name__ == "__main__":
    main()
