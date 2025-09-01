#!/usr/bin/env python3
"""
Xbox Controller Server
Main server module that combines controller input and network communication.
"""

import time
import threading

from .controller_input import ControllerInput
from .network_server import NetworkServer


class XboxControllerServer:
    """
    Main Xbox controller server that reads controller input and sends it to clients.
    """

    def __init__(self, client_ip, client_port, server_port):
        """Initialize the Xbox controller server"""
        self.client_ip = client_ip
        self.client_port = client_port
        self.server_port = server_port
        self.running = False

        # Initialize components
        self.controller_input = ControllerInput()
        self.network_server = NetworkServer(
            client_ip, client_port, server_port)

    def start(self):
        """Start the server"""
        if self.running:
            return

        try:
            # Initialize controller input
            self.controller_input.init_pygame()
            self.controller_input.start()

            # Start network server
            self.network_server.start()

            # Override the send loop to send controller data
            self.network_server._send_loop = self._send_controller_data_loop
            self.network_server.sender_thread = threading.Thread(
                target=self._send_controller_data_loop, daemon=True)
            self.network_server.sender_thread.start()

            self.running = True
            print("Xbox Controller Server started successfully")

            # Keep the main thread alive
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nShutting down server...")
                self.stop()

        except Exception as e:
            print(f"Error starting server: {e}")
            self.stop()
            raise

    def stop(self):
        """Stop the server"""
        self.running = False

        # Stop components
        if hasattr(self, 'controller_input'):
            self.controller_input.stop()

        if hasattr(self, 'network_server'):
            self.network_server.stop()

        print("Xbox Controller Server stopped")

    def _send_controller_data_loop(self):
        """Send controller data to clients at 60 FPS"""
        try:
            print("Sending controller data loop started")
            while self.running:
                print("Sending controller data loop running")
                # Get current controller state
                controller_state = self.controller_input.get_controller_state()

                # Prepare data for transmission
                data = {
                    'timestamp': time.time(),
                    'controller_data': controller_state
                }

                print(data)

                # Send to client
                self.network_server.send_data(data)

                # Control update rate (60 FPS)
                time.sleep(1/60)

        except Exception as e:
            print(f"Error in send loop: {e}")
        finally:
            self.running = False

    def is_running(self):
        """Check if the server is running"""
        return self.running and self.controller_input.is_connected()
