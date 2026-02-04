# GPIO Light Control Web Service

A Flask-based web service to control GPIO pins for light on/off functionality on Raspberry Pi.

## Features

- **Web Interface**: Modern, responsive web interface for controlling lights
- **REST API**: Complete API for programmatic control
- **GPIO Control**: Support for Raspberry Pi GPIO pins with automatic fallback to simulation mode
- **Multiple Lights**: Configure multiple lights with custom names and pin assignments
- **Real-time Status**: Live status updates and control feedback
- **Safety Features**: Proper GPIO cleanup and error handling

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- Relay modules or LED circuits connected to GPIO pins
- Optional: Physical lights connected through relays

## Pin Configuration

Default GPIO pin assignments (BCM numbering):
- **Pin 18**: Living Room Light
- **Pin 19**: Kitchen Light  
- **Pin 20**: Bedroom Light
- **Pin 21**: Bathroom Light


## Installation

### 1. Clone or Download Files
```bash
cd /home/manh/web_contr
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# On Raspberry Pi, you might need:
sudo apt update
sudo apt install python3-pip python3-venv
```

### 3. Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## Configuration

### GPIO Pin Setup
Edit the `CONFIG` dictionary in `app.py` to customize your lights:

```python
CONFIG = {
    'lights': [
        {'id': 1, 'name': 'Living Room', 'pin': 18, 'state': False},
        {'id': 2, 'name': 'Kitchen', 'pin': 19, 'state': False},
        {'id': 3, 'name': 'Bedroom', 'pin': 20, 'state': False},
        {'id': 4, 'name': 'Bathroom', 'pin': 21, 'state': False}
    ]
}
```

### Simulation Mode
The application automatically detects if it's running on a Raspberry Pi. If `RPi.GPIO` is not available, it runs in simulation mode for development and testing.

## Usage

### Start the Web Service
```bash
# Development mode
python app.py

# Or with explicit Python version
python3 app.py

# Production mode (modify app.py to set debug=False)
```

### Access the Web Interface
Open your browser and navigate to:
- **Local**: http://localhost:5000
- **Network**: http://[raspberry-pi-ip]:5000

### Web Interface Features
- **Individual Light Control**: Toggle each light on/off
- **Master Controls**: Turn all lights on/off at once
- **Real-time Status**: See current state of all lights
- **System Information**: View GPIO mode and system status
- **Responsive Design**: Works on desktop and mobile devices

## API Endpoints

### GET /api/lights
Get status of all lights
```json
{
    "success": true,
    "lights": [
        {"id": 1, "name": "Living Room", "pin": 18, "state": false}
    ]
}
```

### GET /api/lights/{id}
Get status of specific light
```json
{
    "success": true,
    "light": {"id": 1, "name": "Living Room", "pin": 18, "state": false}
}
```

### POST /api/lights/{id}/toggle
Toggle a specific light on/off
```json
{
    "success": true,
    "light": {"id": 1, "name": "Living Room", "pin": 18, "state": true},
    "message": "Light Living Room turned ON"
}
```

### POST /api/lights/{id}/set
Set specific light state
```json
// Request body
{"state": true}

// Response
{
    "success": true,
    "light": {"id": 1, "name": "Living Room", "pin": 18, "state": true},
    "message": "Light Living Room turned ON"
}
```

### POST /api/lights/all/on
Turn all lights on
```json
{
    "success": true,
    "lights": [...],
    "message": "All lights turned ON"
}
```

### POST /api/lights/all/off
Turn all lights off
```json
{
    "success": true,
    "lights": [...],
    "message": "All lights turned OFF"
}
```

### GET /api/status
Get system status
```json
{
    "success": true,
    "status": "running",
    "timestamp": "2026-01-25T10:30:00",
    "gpio_mode": "hardware",
    "total_lights": 4
}
```

## Testing

### Test GPIO Controller
```bash
python gpio_controller.py
```

### Test API with curl
```bash
# Get all lights
curl http://localhost:5000/api/lights

# Toggle light 1
curl -X POST http://localhost:5000/api/lights/1/toggle

# Turn all lights on
curl -X POST http://localhost:5000/api/lights/all/on

# Set light 2 to OFF
curl -X POST -H "Content-Type: application/json" \
     -d '{"state": false}' \
     http://localhost:5000/api/lights/2/set
```

## File Structure

```
web_contr/
├── app.py                 # Main Flask application
├── gpio_controller.py     # GPIO control module
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── templates/
    └── index.html        # Web interface
```

## Hardware Wiring Example

For controlling actual lights through relays:

```
Raspberry Pi GPIO → Relay Module → Light Circuit

GPIO Pin 18 → IN1 (Relay 1) → Living Room Light
GPIO Pin 19 → IN2 (Relay 2) → Kitchen Light  
GPIO Pin 20 → IN3 (Relay 3) → Bedroom Light
GPIO Pin 21 → IN4 (Relay 4) → Bathroom Light

Common connections:
- 5V → VCC (Relay Module)
- GND → GND (Relay Module)
```

## Security Notes

- The service runs on all interfaces (0.0.0.0) for network access
- Consider adding authentication for production use
- Use HTTPS in production environments
- Implement rate limiting for API endpoints

## Troubleshooting

### GPIO Permission Issues
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
# Then logout and login again
```

### Port Already in Use
```bash
# Find process using port 5000
sudo netstat -tulpn | grep :5000
# Kill the process if needed
sudo kill <process-id>
```

### Module Import Errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

## Development

### Adding New Features
1. Modify `gpio_controller.py` for GPIO functionality
2. Add API endpoints in `app.py`
3. Update the web interface in `templates/index.html`

### Running in Development Mode
Set `debug=True` in the `app.run()` call in `app.py` for auto-reload and detailed error messages.

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the console/browser logs for errors
3. Test the GPIO controller separately with `python gpio_controller.py`# web_contr
# web_contr
