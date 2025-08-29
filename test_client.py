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

class XboxControllerClient:
    def __init__(self, server_ip='127.0.0.1', server_port=5000, client_port=5001):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_port = client_port
        self.running = False
        
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
    
    def display_controller_data(self, data):
        """Display controller data in a formatted way"""
        # Clear screen (works on most terminals)
        print("\033[2J\033[H", end="")
        
        timestamp = data.get('timestamp', 0)
        controller_data = data.get('controller_data', {})
        
        print("=" * 60)
        print(f"Xbox Controller Data - {time.strftime('%H:%M:%S', time.localtime(timestamp))}")
        print("=" * 60)
        
        # Display sticks
        left_stick = controller_data.get('left_stick', {})
        right_stick = controller_data.get('right_stick', {})
        
        print(f"Left Stick:  X={left_stick.get('x', 0):6.3f} Y={left_stick.get('y', 0):6.3f}")
        print(f"Right Stick: X={right_stick.get('x', 0):6.3f} Y={right_stick.get('y', 0):6.3f}")
        
        # Display triggers
        triggers = controller_data.get('triggers', {})
        print(f"Triggers:    L={triggers.get('left', 0):6.3f} R={triggers.get('right', 0):6.3f}")
        
        # Display buttons
        buttons = controller_data.get('buttons', {})
        print("\nButtons:")
        
        # Main buttons
        main_buttons = ['A', 'B', 'X', 'Y']
        main_status = [buttons.get(btn, False) for btn in main_buttons]
        print(f"  Main:      {' '.join([f'{btn}:{("ON" if status else "OFF"):3}' for btn, status in zip(main_buttons, main_status)])}")
        
        # Shoulder buttons
        shoulder_buttons = ['LB', 'RB']
        shoulder_status = [buttons.get(btn, False) for btn in shoulder_buttons]
        print(f"  Shoulder:  {' '.join([f'{btn}:{("ON" if status else "OFF"):3}' for btn, status in zip(shoulder_buttons, shoulder_status)])}")
        
        # System buttons
        system_buttons = ['start', 'back', 'guide']
        system_status = [buttons.get(btn, False) for btn in system_buttons]
        print(f"  System:    {' '.join([f'{btn}:{("ON" if status else "OFF"):3}' for btn, status in zip(system_buttons, system_status)])}")
        
        # Stick clicks
        stick_buttons = ['left_stick_click', 'right_stick_click']
        stick_status = [buttons.get(btn, False) for btn in stick_buttons]
        print(f"  Stick:     {' '.join([f'{btn}:{("ON" if status else "OFF"):3}' for btn, status in zip(stick_buttons, stick_status)])}")
        
        # D-pad
        dpad_buttons = ['dpad_up', 'dpad_down', 'dpad_left', 'dpad_right']
        dpad_status = [buttons.get(btn, False) for btn in dpad_buttons]
        print(f"  D-pad:     {' '.join([f'{btn}:{("ON" if status else "OFF"):3}' for btn, status in zip(dpad_buttons, dpad_status)])}")
        
        print("\n" + "=" * 60)
        print("Press Ctrl+C to exit")
    
    def start(self):
        """Start the client"""
        self.running = True
        
        # Start receiving data
        receive_thread = threading.Thread(target=self.receive_controller_data, daemon=True)
        receive_thread.start()
        
        print("Receiving controller data...")
        
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
    parser.add_argument('--server-ip', default='127.0.0.1', help='Server IP address (default: 127.0.0.1)')
    parser.add_argument('--server-port', type=int, default=5000, help='Server port (default: 5000)')
    parser.add_argument('--client-port', type=int, default=5001, help='Client port (default: 5001)')
    
    args = parser.parse_args()
    
    try:
        client = XboxControllerClient(args.server_ip, args.server_port, args.client_port)
        client.start()
    except Exception as e:
        print(f"Error starting client: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
