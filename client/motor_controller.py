#!/usr/bin/env python3
"""
Motor Controller Module
Handles motor control using GPIO pins and PWM with proper cleanup.
"""

import atexit
import signal
import sys

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not available. Motor control will be simulated.")


class MotorController:
    """
    Class to handle motor control using GPIO pins and PWM.
    Provides proper initialization and cleanup of GPIO resources.
    """

    def __init__(self):
        """Initialize the motor controller with GPIO setup"""
        # Define the GPIO pins connected to the L298N driver's input pins
        # IN1 (Input 1) -> GPIO 17
        # IN2 (Input 2) -> GPIO 27
        # ENA (Enable A) -> GPIO 18 (or a PWM pin for speed control)
        self.LEFT_BACKWARD = 17
        self.LEFT_FORWARD = 27
        self.LEFT_ENABLE = 18

        self.RIGHT_BACKWARD = 16
        self.RIGHT_FORWARD = 26
        self.RIGHT_ENABLE = 19

        # PWM objects
        self.pwm_left = None
        self.pwm_right = None

        # Track if GPIO is initialized
        self._initialized = False

        # Initialize GPIO
        self._setup_gpio()

        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_gpio(self):
        """Set up GPIO pins and PWM"""
        if not GPIO_AVAILABLE:
            return

        try:
            GPIO.setmode(GPIO.BCM)

            # Set up the defined GPIO pins as output pins
            GPIO.setup(self.LEFT_BACKWARD, GPIO.OUT)
            GPIO.setup(self.LEFT_FORWARD, GPIO.OUT)
            GPIO.setup(self.LEFT_ENABLE, GPIO.OUT)

            GPIO.setup(self.RIGHT_BACKWARD, GPIO.OUT)
            GPIO.setup(self.RIGHT_FORWARD, GPIO.OUT)
            GPIO.setup(self.RIGHT_ENABLE, GPIO.OUT)

            # Create PWM objects for the enable pins to control motor speed
            # A frequency of 100 Hz is a good starting point
            self.pwm_left = GPIO.PWM(self.LEFT_ENABLE, 100)
            self.pwm_right = GPIO.PWM(self.RIGHT_ENABLE, 100)

            # Start the PWM with a duty cycle of 0 (motor is off initially)
            self.pwm_left.start(0)
            self.pwm_right.start(0)

            self._initialized = True
            print("Motor controller initialized successfully")

        except Exception as e:
            print(f"Error initializing motor controller: {e}")
            self.cleanup()
            raise

    def forward(self, speed=100):
        """
        Drives the motor in the forward direction.

        Args:
            speed (int): The PWM duty cycle from 0 to 100.
        """
        if not self._initialized or not GPIO_AVAILABLE:
            print("Motor controller not initialized")
            return

        print("Moving motor forward...")
        GPIO.output(self.LEFT_BACKWARD, GPIO.LOW)
        GPIO.output(self.LEFT_FORWARD, GPIO.HIGH)

        GPIO.output(self.RIGHT_BACKWARD, GPIO.LOW)
        GPIO.output(self.RIGHT_FORWARD, GPIO.HIGH)

        self.pwm_left.ChangeDutyCycle(speed)
        self.pwm_right.ChangeDutyCycle(speed)

    def backward(self, speed=100):
        """
        Drives the motor in the backward direction.

        Args:
            speed (int): The PWM duty cycle from 0 to 100.
        """
        if not self._initialized or not GPIO_AVAILABLE:
            print("Motor controller not initialized")
            return

        print("Moving motor backward...")
        GPIO.output(self.LEFT_BACKWARD, GPIO.HIGH)
        GPIO.output(self.LEFT_FORWARD, GPIO.LOW)

        GPIO.output(self.RIGHT_BACKWARD, GPIO.HIGH)
        GPIO.output(self.RIGHT_FORWARD, GPIO.LOW)

        self.pwm_left.ChangeDutyCycle(speed)
        self.pwm_right.ChangeDutyCycle(speed)

    def right(self, speed=100):
        """
        Drives the motor in the right direction.

        Args:
            speed (int): The PWM duty cycle from 0 to 100.
        """
        if not self._initialized or not GPIO_AVAILABLE:
            print("Motor controller not initialized")
            return

        print("Moving motor right...")
        GPIO.output(self.LEFT_BACKWARD, GPIO.LOW)
        GPIO.output(self.LEFT_FORWARD, GPIO.HIGH)

        GPIO.output(self.RIGHT_BACKWARD, GPIO.HIGH)
        GPIO.output(self.RIGHT_FORWARD, GPIO.LOW)

        self.pwm_left.ChangeDutyCycle(speed)
        self.pwm_right.ChangeDutyCycle(speed)

    def left(self, speed=100):
        """
        Drives the motor in the left direction.

        Args:
            speed (int): The PWM duty cycle from 0 to 100.
        """
        if not self._initialized or not GPIO_AVAILABLE:
            print("Motor controller not initialized")
            return

        print("Moving motor left...")
        GPIO.output(self.LEFT_BACKWARD, GPIO.HIGH)
        GPIO.output(self.LEFT_FORWARD, GPIO.LOW)

        GPIO.output(self.RIGHT_BACKWARD, GPIO.LOW)
        GPIO.output(self.RIGHT_FORWARD, GPIO.HIGH)

        self.pwm_left.ChangeDutyCycle(speed)
        self.pwm_right.ChangeDutyCycle(speed)

    def stop(self):
        """
        Stops the motor by setting the enable pin to LOW.
        """
        if not self._initialized or not GPIO_AVAILABLE:
            return

        print("Stopping motor...")
        self.pwm_left.ChangeDutyCycle(0)
        self.pwm_right.ChangeDutyCycle(0)

    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        print(f"\nReceived signal {signum}, cleaning up...")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Clean up GPIO resources"""
        if not self._initialized or not GPIO_AVAILABLE:
            return

        try:
            print("Cleaning up motor controller...")

            # Stop motors
            self.stop()

            # Stop PWM
            if self.pwm_left:
                self.pwm_left.stop()
            if self.pwm_right:
                self.pwm_right.stop()

            # Clean up GPIO
            GPIO.cleanup()

            self._initialized = False
            print("Motor controller cleanup completed")

        except Exception as e:
            print(f"Error during cleanup: {e}")


if __name__ == "__main__":
    # Test the motor controller
    import time

    try:
        controller = MotorController()
        print("Testing motor controller...")

        # Test forward movement
        controller.forward(50)
        time.sleep(2)

        # Test stop
        controller.stop()
        time.sleep(1)

        # Test backward movement
        controller.backward(50)
        time.sleep(2)

        # Test stop
        controller.stop()

        print("Motor controller test completed successfully")

    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if 'controller' in locals():
            controller.cleanup()
