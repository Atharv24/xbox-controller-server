#!/usr/bin/env python3
"""
Network Server Module
Handles UDP communication with clients.
"""

import json
import socket
import threading
import time


class NetworkServer:
    """
    Class to handle UDP network communication with clients.
    Provides thread-safe data transmission.
    """

    def __init__(self, client_ip, client_port, server_port):
        """Initialize the network server"""
        self.client_ip = client_ip
        self.client_port = client_port
        self.server_port = server_port
        self.running = False
        self.sock = None
        self.sender_thread = None

    def start(self):
        """Start the network server"""
        if self.running:
            return

        try:
            # Initialize UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', self.server_port))

            self.running = True
            self.sender_thread = threading.Thread(
                target=self._send_loop, daemon=True)
            self.sender_thread.start()

            print(f"Network server started on port {self.server_port}")
            print(
                f"Sending data to client at {self.client_ip}:{self.client_port}")

        except Exception as e:
            print(f"Error starting network server: {e}")
            raise

    def stop(self):
        """Stop the network server"""
        self.running = False

        if self.sender_thread:
            self.sender_thread.join(timeout=1.0)

        if self.sock:
            self.sock.close()
            self.sock = None

        print("Network server stopped")

    def _send_loop(self):
        """Send data loop - this will be overridden by the main server"""
        pass

    def send_data(self, data):
        """Send data to the client"""
        if not self.running or not self.sock:
            return False

        try:
            message = json.dumps(data).encode('utf-8')
            self.sock.sendto(message, (self.client_ip, self.client_port))
            return True
        except Exception as e:
            print(f"Error sending to {self.client_ip}:{self.client_port}: {e}")
            return False

    def is_running(self):
        """Check if the server is running"""
        return self.running


if __name__ == "__main__":
    # Test the network server
    import time

    try:
        server = NetworkServer('127.0.0.1', 5001, 5000)
        server.start()

        print("Testing network server...")
        print("Sending test data every second")

        test_data = {
            'timestamp': time.time(),
            'test': True,
            'message': 'Hello from network server'
        }

        while True:
            server.send_data(test_data)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping network server test...")
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if 'server' in locals():
            server.stop()
