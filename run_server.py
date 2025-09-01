#!/usr/bin/env python3
"""
Launcher script for the Xbox Controller Server
Run this script from the project root to start the server.
"""
import sys

from server.server import XboxControllerServer

if __name__ == "__main__":
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Xbox Controller Server')
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
        import sys
        sys.exit(1)
