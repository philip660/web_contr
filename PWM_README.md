# PWM LED Control Setup

This project provides complete **PWM (Pulse Width Modulation)** control for LEDs with both web interface and API access.

## ✨ Features

### 🎛️ PWM Control Capabilities
- **Smooth brightness control** (0-100%)
- **Fade effects** with customizable timing
- **Real-time web interface** with sliders
- **API endpoints** for programmatic control
- **Multiple light zones** with independent control

### 🔧 Hardware Support
- **Raspberry Pi GPIO** PWM pins
- **Simulation mode** for development/testing
- **1kHz PWM frequency** for smooth dimming
- **BCM pin numbering** (GPIO 18, 19, 20, 21)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Access Web Interface
Open your browser to: http://localhost:5000

## 🎮 PWM Control Interface

### Web Interface Features
- **Brightness sliders** for precise control (0-100%)
- **Quick preset buttons**: 25%, 50%, 75%, 100%
- **Toggle switches** for on/off control
- **Real-time status** indicators
- **Fade effects** with smooth transitions

### API Endpoints

#### Set Brightness
```bash
POST /api/lights/<id>/brightness
{
  "brightness": 75.0
}
```

#### Fade Effect
```bash
POST /api/lights/<id>/fade
{
  "brightness": 100.0,
  "fade_time": 2.0,
  "steps": 50
}
```

## 📊 Configuration

### Light Configuration (app.py)
```python
CONFIG = {
    'lights': [
        {
            'id': 1, 
            'name': 'Living Room', 
            'pin': 18, 
            'type': 'pwm',        # Enable PWM control
            'brightness': 0
        },
        # Add more lights...
    ]
}
```

### PWM Settings
- **Frequency**: 1000 Hz (configurable in gpio_controller.py)
- **Resolution**: 0-100% duty cycle
- **Update Rate**: Real-time response

## 🔌 Hardware Wiring

### Basic LED Connection
```
Raspberry Pi GPIO Pin → Current Limiting Resistor → LED Anode
                                                    LED Cathode → Ground
```

### PWM-Compatible Pins
- GPIO 18 (Pin 12) - Hardware PWM
- GPIO 19 (Pin 35) - Hardware PWM  
- GPIO 20 (Pin 38) - Software PWM
- GPIO 21 (Pin 40) - Software PWM

### Recommended Resistor Values
- **Red LED**: 220Ω - 1kΩ
- **Blue/White LED**: 470Ω - 1kΩ
- **High-Power LEDs**: Use MOSFET/transistor driver

## 🧪 Demo Script

Run the PWM demo to see all features:
```bash
python pwm_demo.py
```

### Demo Features
- ✨ Brightness control (25%, 50%, 75%, 100%)
- 🌅 Fade effects with different timings
- 💨 Breathing effect (smooth oscillation)
- 📊 Status monitoring

## 🔧 Advanced Usage

### Custom Fade Effects
```python
# Sunrise effect
fade_light(light_id=1, target_brightness=100, fade_time=10.0)

# Sunset effect  
fade_light(light_id=1, target_brightness=0, fade_time=15.0)

# Quick flash
set_brightness(light_id=1, brightness=100)
time.sleep(0.1)
set_brightness(light_id=1, brightness=0)
```

### Multiple Light Synchronization
```python
# Sync all lights to same brightness
for light in CONFIG['lights']:
    set_brightness(light['id'], 75)
```

## 🛠️ Troubleshooting

### Common Issues

1. **No PWM output**
   - Check GPIO pin configuration
   - Verify hardware connections
   - Ensure sufficient power supply

2. **Flickering LEDs**
   - Increase PWM frequency (gpio_controller.py)
   - Check for loose connections
   - Use appropriate resistor values

3. **Slow response**
   - Reduce fade steps for faster transitions
   - Check network latency for web interface

### Debug Mode
Enable detailed logging in app.py:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance

- **Response Time**: < 50ms for brightness changes
- **Fade Resolution**: 50 steps (customizable)
- **PWM Frequency**: 1000 Hz (flicker-free)
- **Web Interface**: Real-time updates (< 1s refresh)

## 🔄 Service Setup

For automatic startup, install as systemd service:
```bash
sudo cp gpio-lights.service /etc/systemd/system/
sudo systemctl enable gpio-lights
sudo systemctl start gpio-lights
```

## 🎯 Use Cases

- **Home automation** with smooth lighting
- **Mood lighting** with color temperature simulation  
- **Photography** with adjustable studio lighting
- **Plant growing** with sunrise/sunset cycles
- **Security lighting** with motion-triggered fading
- **Entertainment** synchronized with music/movies

---

*For more details, see the full API documentation in API_EXAMPLES.md*