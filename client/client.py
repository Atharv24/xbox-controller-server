#!/usr/bin/env python3
"""
Xbox Controller Client
Receives and displays controller data from the server and controls motors.
"""

import socket
import json
import time
import sys

from .motor_controller import MotorController


class XboxControllerClient:
    def __init__(self, server_ip='127.0.0.1', server_port=5000, client_port=5001):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_port = client_port
        self.running = False
        self.last_message_timestamp = 0

        self.delay_rolling_average = 0
        self.total_packets = 0

        # Initialize motor controller
        self.motor_controller = MotorController()

        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1.0)

        # Bind to specified port
        self.sock.bind(('0.0.0.0', self.client_port))

        print(f"Client started on port {self.client_port}")
        print(f"Waiting for data from server at {server_ip}:{server_port}")

    def receive_controller_data(self):
        """Receive and display controller data"""
        try:
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(4096)
                    controller_data = json.loads(data.decode('utf-8'))

                    # Display the data
                    self.display_controller_data(controller_data)

                except socket.timeout:
                    continue
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                except Exception as e:
                    print(f"Error receiving data: {e}")

        except Exception as e:
            print(f"Error in receive thread: {e}")
        except KeyboardInterrupt:
            print("\nStopping client...")
        finally:
            self.stop()

    def display_controller_data(self, data):
        """Display controller data in a formatted way"""
        # Clear screen (works on most terminals)
        print("\033[2J\033[H", end="")

        timestamp = data.get('timestamp')

        # delay = timestamp - time.time()
        # self.delay_rolling_average = (self.delay_rolling_average * (self.total_packets) + delay )/(self.total_packets+1)
        # self.total_packets += 1
        # print(self.delay_rolling_average)

        if timestamp < self.last_message_timestamp:
            return
        self.last_message_timestamp = timestamp

        controller_data = data.get('controller_data', {})

        print("=" * 60)
        print(f"Xbox Controller State")
        print("=" * 60)

        # Display sticks
        left_stick = controller_data.get('left_stick', {})
        right_stick = controller_data.get('right_stick', {})

        print(
            f"Left Stick:  X={left_stick.get('x', 0):6.3f} Y={left_stick.get('y', 0):6.3f}")
        if left_stick.get('x', 0) > 0:
            self.motor_controller.right(left_stick.get('x', 0) * 100)
        else:
            self.motor_controller.left(left_stick.get('x', 0) * 100 * -1)

        print(
            f"Right Stick: X={right_stick.get('x', 0):6.3f} Y={right_stick.get('y', 0):6.3f}")

        # Display triggers
        triggers = controller_data.get('triggers', {})
        print(
            f"Triggers:    L={triggers.get('left', 0):6.3f} R={triggers.get('right', 0):6.3f}")
        right_trigger_mag = triggers.get('right', 0) * 100
        left_trigger_mag = triggers.get('left', 0) * 100

        print("RIGHT TRIGGER", right_trigger_mag)
        print("LEFT TRIGGER", left_trigger_mag)

        if right_trigger_mag > 0:
            self.motor_controller.forward(right_trigger_mag)
        else:
            self.motor_controller.backward(left_trigger_mag)

        buttons = controller_data.get('buttons', {})
        print(buttons)

        print("\n" + "=" * 60)

    def start(self):
        """Start the client"""
        self.running = True
        print("Receiving controller data...")

        self.receive_controller_data()

        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping client...")
            self.stop()

    def stop(self):
        """Stop the client"""
        self.running = False
        if hasattr(self, 'sock'):
            self.sock.close()
        if hasattr(self, 'motor_controller'):
            self.motor_controller.cleanup()


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Xbox Controller Client')
    parser.add_argument('--server-ip', default='10.0.0.131',
                        help='Server IP address (default: 127.0.0.1)')
    parser.add_argument('--server-port', type=int,
                        default=5000, help='Server port (default: 5000)')
    parser.add_argument('--client-port', type=int,
                        default=5001, help='Client port (default: 5001)')

    args = parser.parse_args()

    try:
        client = XboxControllerClient(
            args.server_ip, args.server_port, args.client_port)
        client.start()
    except Exception as e:
        print(f"Error starting client: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
