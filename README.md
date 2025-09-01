# Xbox Controller Input Server

A Python application that reads Xbox controller input and sends it via UDP to a single client in real-time.

## Features

- **Real-time Input Reading**: Reads Xbox controller input at 60 FPS
- **UDP Communication**: Sends controller data to a single client
- **Multiple Input Libraries**: Supports both `inputs` and `pygame` libraries
- **Pre-configured Client**: Simple setup with known IP addresses
- **Cross-platform**: Works on Windows, macOS, and Linux
- **JSON Data Format**: Easy to parse controller data

## Supported Controller Inputs

- **Analog Sticks**: Left and right stick X/Y coordinates (-1.0 to 1.0)
- **Triggers**: Left and right trigger values (0.0 to 1.0)
- **Buttons**: All standard Xbox controller buttons (A, B, X, Y, LB, RB, etc.)
- **D-pad**: Directional pad inputs
- **System Buttons**: Start, Back, Guide buttons

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install inputs pygame
   ```

3. **Connect your Xbox controller** to your computer via USB or wireless

## Usage

### Starting the Server

1. **Run the server** (defaults to localhost):
   ```bash
   python run_server.py
   ```
   
   Or run directly from the server directory:
   ```bash
   python server/server.py
   ```

2. **Optional command-line arguments**:
   ```bash
   python run_server.py --client-ip 192.168.1.100 --client-port 5001 --server-port 5000
   ```

   - `--client-ip`: IP address of the client (default: 127.0.0.1)
   - `--client-port`: Port the client is listening on (default: 5001)
   - `--server-port`: Port the server binds to (default: 5000)

### Running the Client

1. **In a separate terminal, run the client**:
   ```bash
   python run_client.py
   ```
   
   Or run directly from the client directory:
   ```bash
   python client/client.py
   ```

2. **Optional client arguments**:
   ```bash
   python run_client.py --server-ip 192.168.1.50 --server-port 5000 --client-port 5001
   ```

3. **Move your controller** and watch the real-time data display

### Network Setup

For communication between different computers:

1. **Server computer**: Run the server with the client's IP address
   ```bash
   python run_server.py --client-ip 192.168.1.100
   ```

2. **Client computer**: Run the client with the server's IP address
   ```bash
   python run_client.py --server-ip 192.168.1.50
   ```

## Data Format

The server sends JSON data with the following structure:

```json
{
  "timestamp": 1640995200.123,
  "controller_data": {
    "left_stick": {"x": 0.5, "y": -0.3},
    "right_stick": {"x": 0.0, "y": 0.0},
    "triggers": {"left": 0.0, "right": 0.0},
    "buttons": {
      "A": false,
      "B": false,
      "X": false,
      "Y": false,
      "LB": false,
      "RB": false,
      "start": false,
      "back": false,
      "guide": false,
      "left_stick_click": false,
      "right_stick_click": false,
      "dpad_up": false,
      "dpad_down": false,
      "dpad_left": false,
      "dpad_right": false
    }
  }
}
```

## Project Structure

```
controller-server/
├── client/                    # Client package
│   ├── __init__.py           # Package initialization
│   ├── client.py             # Xbox controller client
│   └── motor_controller.py   # Motor control module
├── server/                    # Server package
│   ├── __init__.py           # Package initialization
│   ├── server.py             # Main server
│   ├── controller_input.py   # Controller input module
│   └── network_server.py     # Network communication module
├── run_client.py             # Client launcher script
├── run_server.py             # Server launcher script
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Creating Your Own Client

Here's a simple example of how to create a custom client:

```python
import socket
import json

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 5001))  # Bind to client port

# Receive controller data
while True:
    data, addr = sock.recvfrom(4096)
    controller_data = json.loads(data.decode('utf-8'))
    
    # Process the controller data
    left_stick = controller_data['controller_data']['left_stick']
    print(f"Left stick: {left_stick}")
```

### Using the Motor Controller

The client package includes a `MotorController` class for controlling motors via GPIO:

```python
from client.motor_controller import MotorController

# Initialize motor controller
motor = MotorController()

# Control motors
motor.forward(50)  # 50% speed forward
motor.backward(75) # 75% speed backward
motor.stop()       # Stop motors

# Cleanup (automatically handled on exit)
motor.cleanup()
```

### Using the Server Components

The server package includes modular components that can be used independently:

```python
from server.controller_input import ControllerInput
from server.network_server import NetworkServer

# Use controller input independently
controller = ControllerInput()
controller.init_pygame()
controller.start()

# Get controller state
state = controller.get_controller_state()
print(f"Left stick: {state['left_stick']}")

# Use network server independently
network = NetworkServer('127.0.0.1', 5001, 5000)
network.start()

# Send custom data
network.send_data({'custom': 'data'})
```

## Troubleshooting

### Controller Not Detected

1. **Check controller connection**: Ensure your Xbox controller is properly connected
2. **Install drivers**: Make sure you have the latest Xbox controller drivers
3. **Try different input library**: The server will automatically fall back from `inputs` to `pygame`

### Connection Issues

1. **Check firewall**: Ensure the specified ports are not blocked
2. **Verify network**: Make sure client and server are on the same network
3. **Check IP addresses**: Verify the correct IP addresses are being used
4. **Port conflicts**: Make sure the ports aren't being used by other applications

### Performance Issues

1. **Reduce update rate**: Modify the `time.sleep(1/60)` in the send loop
2. **Check network**: Ensure stable network connection between server and client
3. **Monitor CPU usage**: High CPU usage might indicate input library issues

## Requirements

- Python 3.6 or higher
- Xbox controller (wired or wireless)
- Network connection (for client-server communication)

## Dependencies

- `inputs` (recommended) or `pygame` (fallback)
- Standard Python libraries: `socket`, `json`, `threading`, `time`

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this project.
