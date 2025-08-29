#!/usr/bin/env python3
"""
Xbox Controller Input Server
Reads Xbox controller input and sends it via UDP to a single client.
"""

import inputs
import json
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
        self.controller_data = {
            'left_stick': {'x': 0, 'y': 0},
            'right_stick': {'x': 0, 'y': 0},
            'triggers': {'left': 0, 'right': 0},
            'buttons': {
                'A': False, 'B': False, 'X': False, 'Y': False,
                'LB': False, 'RB': False, 'LT': False, 'RT': False,
                'start': False, 'back': False, 'guide': False,
                'left_stick_click': False, 'right_stick_click': False,
                'dpad_up': False, 'dpad_down': False, 'dpad_left': False, 'dpad_right': False
            }
        }
        
        # Initialize controller input method
        self.init_inputs()
        
        # Initialize UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.server_port))
        
        print(f"Xbox Controller Server started on port {self.server_port}")
        print(f"Sending data to client at {self.client_ip}:{self.client_port}")
    
    def init_inputs(self):
        """Initialize using the 'inputs' library"""
        try:
            # Get the first Xbox controller
            devices = inputs.devices.gamepads
            if not devices:
                raise Exception("No Xbox controller found")
            print(f"Found Xbox controller: {devices[0].name}")
        except Exception as e:
            print(f"Error initializing controller with 'inputs': {e}")
    
    def read_controller_inputs(self):
        """Read controller input using the available method"""
        return self.read_inputs_library()
    
    def read_inputs_library(self):
        """Read controller input using 'inputs' library"""
        try:
            events = inputs.get_gamepad()
            for event in events:
                self.process_inputs_event(event)
        except Exception as e:
            print(f"Error reading controller input: {e}")
    
    def process_inputs_event(self, event):
        """Process events from the 'inputs' library"""
        if event.ev_type == 'Absolute':
            match event.code:
                case 'ABS_X':
                    self.controller_data['left_stick']['x'] = round(event.state / 32768.0, 3)
                case 'ABS_Y':
                    self.controller_data['left_stick']['y'] = round(event.state / 32768.0, 3)
                case 'ABS_RX':
                    self.controller_data['right_stick']['x'] = round(event.state / 32768.0, 3)
                case 'ABS_RY':
                    self.controller_data['right_stick']['y'] = round(event.state / 32768.0, 3)
                case 'ABS_Z':
                    self.controller_data['triggers']['left'] = round(event.state / 255.0, 3)
                case 'ABS_RZ':
                    self.controller_data['triggers']['right'] = round(event.state / 255.0, 3)
                case 'ABS_HAT0X':
                    self.controller_data['buttons']['dpad_left'] = event.state == -1
                    self.controller_data['buttons']['dpad_right'] = event.state == 1
                case 'ABS_HAT0Y':
                    self.controller_data['buttons']['dpad_up'] = event.state == -1
                    self.controller_data['buttons']['dpad_down'] = event.state == 1
        
        elif event.ev_type == 'Key':
            button_mapping = {
                'BTN_SOUTH': 'A',
                'BTN_EAST': 'B',
                'BTN_NORTH': 'X',
                'BTN_WEST': 'Y',
                'BTN_TL': 'LB',
                'BTN_TR': 'RB',
                'BTN_START': 'start',
                'BTN_SELECT': 'back',
                'BTN_MODE': 'guide',
                'BTN_THUMBL': 'left_stick_click',
                'BTN_THUMBR': 'right_stick_click'
            }
            
            if event.code in button_mapping:
                self.controller_data['buttons'][button_mapping[event.code]] = bool(event.state)
    
    def send_controller_data(self):
        """Send controller data to the client"""
        try:
            while self.running:
                # Read controller input
                self.read_controller_inputs()
                
                # Prepare data for transmission
                data = {
                    'timestamp': time.time(),
                    'controller_data': self.controller_data
                }
                
                # Send to client
                message = json.dumps(data).encode('utf-8')
                try:
                    self.sock.sendto(message, (self.client_ip, self.client_port))
                except Exception as e:
                    print(f"Error sending to {self.client_ip}:{self.client_port}: {e}")
                
                # Control update rate (60 FPS)
                time.sleep(1/60)
        
        except Exception as e:
            print(f"Error in send thread: {e}")
    
    def start(self):
        """Start the server"""
        self.running = True
        
        # Start send thread
        send_thread = threading.Thread(target=self.send_controller_data, daemon=True)
        send_thread.start()
        
        print("Server is running. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.stop()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if hasattr(self, 'sock'):
            self.sock.close()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Xbox Controller Input Server')
    parser.add_argument('--client-ip', default='10.0.0.36', help='Client IP address (default: 10.0.0.36)')
    parser.add_argument('--client-port', type=int, default=5001, help='Client port (default: 5001)')
    parser.add_argument('--server-port', type=int, default=5000, help='Server port (default: 5000)')
    
    args = parser.parse_args()
    
    try:
        server = XboxControllerServer(args.client_ip, args.client_port, args.server_port)
        server.start()
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
