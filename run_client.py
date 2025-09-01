#!/usr/bin/env python3
"""
Launcher script for the Xbox Controller Client
Run this script from the project root to start the client.
"""
import sys

from client.client import XboxControllerClient

if __name__ == "__main__":
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
