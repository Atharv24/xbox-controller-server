#!/usr/bin/env python3
"""
Controller Input Module
Handles Xbox controller input reading using pygame.
"""

import pygame
import threading
import time


class ControllerInput:
    """
    Class to handle Xbox controller input reading.
    Provides thread-safe controller state management.
    """

    def __init__(self):
        """Initialize the controller input system"""
        self.joystick = None
        self.running = False
        self.controller_state = {
            'left_stick': {'x': 0, 'y': 0},
            'right_stick': {'x': 0, 'y': 0},
            'triggers': {'left': 0, 'right': 0},
            'buttons': {}
        }
        self.lock = threading.Lock()
        self.reader_thread = None

    def init_pygame(self):
        """Initialize pygame for controller input"""
        try:
            pygame.init()
            pygame.joystick.init()

            if pygame.joystick.get_count() == 0:
                raise Exception("No controllers found")

            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

            print(f"Controller Name: {self.joystick.get_name()}")
            print(f"Number of Axes: {self.joystick.get_numaxes()}")
            print(f"Number of Buttons: {self.joystick.get_numbuttons()}")

        except Exception as e:
            print(f"Error initializing pygame: {e}")
            raise

    def start(self):
        """Start reading controller input"""
        if self.running:
            return

        self.running = True
        self.reader_thread = threading.Thread(
            target=self._read_controller_loop, daemon=True)
        self.reader_thread.start()
        print("Controller input reading started")

    def stop(self):
        """Stop reading controller input"""
        self.running = False
        if self.reader_thread:
            self.reader_thread.join(timeout=1.0)
        pygame.quit()
        print("Controller input reading stopped")

    def _read_controller_loop(self):
        """Read controller input in a loop"""
        try:
            while self.running:
                pygame.event.pump()

                # Read analog sticks
                left_stick_x = round(self.joystick.get_axis(0), 3)
                left_stick_y = round(self.joystick.get_axis(1), 3)
                right_stick_x = round(self.joystick.get_axis(2), 3)
                right_stick_y = round(self.joystick.get_axis(3), 3)

                # Read triggers (convert from -1,1 to 0,1 range)
                left_trigger = round((self.joystick.get_axis(4) + 1) / 2, 3)
                right_trigger = round((self.joystick.get_axis(5) + 1) / 2, 3)

                # Read buttons
                buttons = {}
                for i in range(self.joystick.get_numbuttons()):
                    button_name = self._get_button_name(i)
                    if button_name:
                        buttons[button_name] = bool(
                            self.joystick.get_button(i))

                # Create new controller state
                new_controller_state = {
                    'left_stick': {'x': left_stick_x, 'y': left_stick_y},
                    'right_stick': {'x': right_stick_x, 'y': right_stick_y},
                    'triggers': {'left': left_trigger, 'right': right_trigger},
                    'buttons': buttons
                }

                # Update shared state safely
                with self.lock:
                    self.controller_state = new_controller_state

                # Small sleep to prevent excessive CPU usage
                time.sleep(0.01)

        except Exception as e:
            print(f"Error in controller input loop: {e}")
        finally:
            self.running = False

    def _get_button_name(self, button_index):
        """Map button index to button name"""
        button_names = {
            0: 'A',
            1: 'B',
            2: 'X',
            3: 'Y',
            4: 'LB',
            5: 'RB',
            6: 'back',
            7: 'start',
            8: 'guide',
            9: 'left_stick_click',
            10: 'right_stick_click'
        }
        return button_names.get(button_index)

    def get_controller_state(self):
        """Get a copy of the current controller state"""
        with self.lock:
            return self.controller_state.copy()

    def is_connected(self):
        """Check if controller is connected"""
        return self.joystick is not None and self.running


if __name__ == "__main__":
    # Test the controller input
    import time

    try:
        controller = ControllerInput()
        controller.init_pygame()
        controller.start()

        print("Testing controller input...")
        print("Move your controller and press buttons to see the output")
        print("Press Ctrl+C to stop")

        while True:
            state = controller.get_controller_state()
            print(f"\rLeft: ({state['left_stick']['x']:6.3f}, {state['left_stick']['y']:6.3f}) "
                  f"Right: ({state['right_stick']['x']:6.3f}, {state['right_stick']['y']:6.3f}) "
                  f"Triggers: L={state['triggers']['left']:5.3f} R={state['triggers']['right']:5.3f}", end="")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping controller input test...")
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if 'controller' in locals():
            controller.stop()
