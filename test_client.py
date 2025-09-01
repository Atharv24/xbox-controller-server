#!/usr/bin/env python3
"""
Test Client for Xbox Controller Server
Receives and displays controller data from the server.
"""

import socket
import json
import time
import threading
import sys

import RPi.GPIO as GPIO

# Set the GPIO mode to BCM. This refers to the GPIO numbering scheme,
# not the physical pin numbers.
# BCM pin numbers:
# GPIO 17 (physical pin 11)
# GPIO 27 (physical pin 13)
# GPIO 18 (physical pin 12)
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins connected to the L298N driver's input pins
# IN1 (Input 1) -> GPIO 17
# IN2 (Input 2) -> GPIO 27
# ENA (Enable A) -> GPIO 18 (or a PWM pin for speed control)
PIN_IN1 = 17
PIN_IN2 = 27
PIN_ENA = 18

PIN_IN3 = 16
PIN_IN4 = 26
PIN_ENB = 19

# Set up the defined GPIO pins as output pins
GPIO.setup(PIN_IN1, GPIO.OUT)
GPIO.setup(PIN_IN2, GPIO.OUT)
GPIO.setup(PIN_ENA, GPIO.OUT)

GPIO.setup(PIN_IN3, GPIO.OUT)
GPIO.setup(PIN_IN4, GPIO.OUT)
GPIO.setup(PIN_ENB, GPIO.OUT)

# Create a PWM object for the enable pin to control motor speed
# A frequency of 100 Hz is a good starting point
pwm_left = GPIO.PWM(PIN_ENA, 100)
pwm_right = GPIO.PWM(PIN_ENB, 100)

# Start the PWM with a duty cycle of 0 (motor is off initially)
pwm_left.start(0)
pwm_right.start(0)

def forward(speed=100):
    """
    Drives the motor in the forward direction.

    Args:
        speed (int): The PWM duty cycle from 0 to 100.
    """
    print("Moving motor forward...")
    GPIO.output(PIN_IN1, GPIO.HIGH)
    GPIO.output(PIN_IN2, GPIO.LOW)
    
    GPIO.output(PIN_IN3, GPIO.LOW)
    GPIO.output(PIN_IN4, GPIO.HIGH)

    pwm_left.ChangeDutyCycle(speed)
    pwm_right.ChangeDutyCycle(speed)

def backward(speed=100):
    """
    Drives the motor in the backward direction.

    Args:
        speed (int): The PWM duty cycle from 0 to 100.
    """
    print("Moving motor backward...")
    GPIO.output(PIN_IN1, GPIO.LOW)
    GPIO.output(PIN_IN2, GPIO.HIGH)
    
    GPIO.output(PIN_IN3, GPIO.HIGH)
    GPIO.output(PIN_IN4, GPIO.LOW)

    pwm_left.ChangeDutyCycle(speed)
    pwm_right.ChangeDutyCycle(speed)

def stop():
    """
    Stops the motor by setting the enable pin to LOW.
    """
    print("Stopping motor...")
    pwm_left.ChangeDutyCycle(0)
    pwm_right.ChangeDutyCycle(0)

class XboxControllerClient:
    def __init__(self, server_ip='127.0.0.1', server_port=5000, client_port=5001):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_port = client_port
        self.running = False
        self.last_message_timestamp = 0

        self.delay_rolling_average = 0
        self.total_packets = 0

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
        print(
            f"Right Stick: X={right_stick.get('x', 0):6.3f} Y={right_stick.get('y', 0):6.3f}")

        # Display triggers
        triggers = controller_data.get('triggers', {})
        print(
            f"Triggers:    L={triggers.get('left', 0):6.3f} R={triggers.get('right', 0):6.3f}")
        right_trigger_mag = triggers.get('right', 0) * 100
        
        print("RIGHT TRIGGER", right_trigger_mag)
        forward(right_trigger_mag)

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


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Xbox Controller Test Client')
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
