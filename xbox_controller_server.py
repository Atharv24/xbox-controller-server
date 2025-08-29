#!/usr/bin/env python3
"""
Xbox Controller Input Server
Reads Xbox controller input and sends it via UDP to a single client.
"""

import json
import pygame
import socket
import sys
import threading
import time


class XboxControllerServer:
    def __init__(self, client_ip, client_port, server_port):
        self.client_ip = client_ip
        self.client_port = client_port
        self.server_port = server_port
        self.running = False
        self.controller_state = {
            'left_stick': {
                'x': 0
            },
            'triggers': {
                'left': 0,
                'right': 0
            },
        }

        self.lock = threading.Lock()

        # Initialize controller input method
        self.init_pygame()

        # Initialize UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.server_port))

        print(f"Xbox Controller Server started on port {self.server_port}")
        print(f"Sending data to client at {self.client_ip}:{self.client_port}")

    def start(self):
        """Start the server"""
        self.running = True

        # self.reader_thread = threading.Thread(
        #     target=self.read_controller_state_in_loop, daemon=True)
        self.sender_thread = threading.Thread(
            target=self.send_controller_state_in_loop, daemon=True)

        self.sender_thread.start()

        self.read_controller_state_in_loop()

    def stop(self):
        """Stops the threads and closes the socket."""
        self.running = False

        self.sock.close()
        pygame.quit()

    def init_pygame(self):
        """Initialize using pygame"""
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            raise Exception("No controllers found")

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print(f"Controller Name: {self.joystick.get_name()}")
        print(f"Number of Axes: {self.joystick.get_numaxes()}")
        print(f"Number of Buttons: {self.joystick.get_numbuttons()}")

    def read_controller_state_in_loop(self):
        """Read controller input using pygame"""
        try:
            while self.running:
                pygame.event.pump()
                new_controller_state = {
                    'left_stick': {
                        'x': round(self.joystick.get_axis(0), 3)
                    },
                    'triggers': {
                        'left': round((self.joystick.get_axis(4)+1)/2, 3),
                        'right': round((self.joystick.get_axis(5)+1)/2, 3)
                    }
                }

                # Acquire the lock to update the shared state safely.
                with self.lock:
                    self.controller_state = new_controller_state

                # Add a small sleep to prevent the loop from consuming too much CPU.
                time.sleep(0.01)
        except Exception as e:
            print(f"Error in send thread: {e}")
        except KeyboardInterrupt:
            print("Closing....")
        finally:
            self.stop()

    def send_controller_state_in_loop(self):
        """Send controller data to the client"""
        try:
            while self.running:
                # Prepare data to send
                controller_state = None

                # Acquire the lock to read the shared state safely.
                with self.lock:
                    # Get a copy of the current controller state.
                    controller_state = self.controller_state.copy()

                # Prepare data for transmission
                data = {
                    'timestamp': time.time(),
                    'controller_data': controller_state
                }

                # Send to client
                message = json.dumps(data).encode('utf-8')
                try:
                    self.sock.sendto(
                        message, (self.client_ip, self.client_port))
                except Exception as e:
                    print(
                        f"Error sending to {self.client_ip}:{self.client_port}: {e}")

                # Control update rate (60 FPS)
                time.sleep(1/60)

        except Exception as e:
            print(f"Error in send thread: {e}")
        except KeyboardInterrupt:
            print("Closing....")
        finally:
            self.stop()


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Xbox Controller Input Server')
    parser.add_argument('--client-ip', default='10.0.0.36',
                        help='Client IP address (default: 10.0.0.36)')
    parser.add_argument('--client-port', type=int,
                        default=5001, help='Client port (default: 5001)')
    parser.add_argument('--server-port', type=int,
                        default=5000, help='Server port (default: 5000)')

    args = parser.parse_args()

    try:
        server = XboxControllerServer(
            args.client_ip, args.client_port, args.server_port)
        server.start()
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
