#!/usr/bin/env python3
"""
GPIO Light Control Web Service
A Flask web application to control GPIO pins for light on/off functionality
"""

import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
import threading
import time
import uuid

# Import GPIO control module
from gpio_controller import GPIOController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize GPIO controller
gpio_controller = GPIOController()

# Configuration
CONFIG = {
    'lights': [
        {'id': 1, 'name': 'Living Room', 'pin': 18, 'state': False, 'type': 'pwm', 'brightness': 0},
        {'id': 2, 'name': 'Kitchen', 'pin': 19, 'state': False, 'type': 'pwm', 'brightness': 0},
        {'id': 3, 'name': 'Bedroom', 'pin': 20, 'state': False, 'type': 'pwm', 'brightness': 0},
        {'id': 4, 'name': 'Bathroom', 'pin': 21, 'state': False, 'type': 'pwm', 'brightness': 0}
    ]
}

# Timer storage
TIMERS = []
timer_lock = threading.Lock()

# Initialize GPIO pins
for light in CONFIG['lights']:
    if light.get('type') == 'pwm':
        gpio_controller.setup_pwm_pin(light['pin'])
    else:
        gpio_controller.setup_pin(light['pin'])

@app.route('/')
def index():
    """Render the main control interface"""
    return render_template('index.html', lights=CONFIG['lights'])

@app.route('/api/lights', methods=['GET'])
def get_lights():
    """Get all lights status"""
    try:
        # Update current states from GPIO
        for light in CONFIG['lights']:
            if light.get('type') == 'pwm':
                brightness = gpio_controller.get_brightness(light['pin'])
                light['brightness'] = brightness
                light['state'] = brightness > 0
            else:
                light['state'] = gpio_controller.get_pin_state(light['pin'])
        
        return jsonify({
            'success': True,
            'lights': CONFIG['lights']
        })
    except Exception as e:
        logger.error(f"Error getting lights: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/<int:light_id>', methods=['GET'])
def get_light(light_id):
    """Get specific light status"""
    try:
        light = next((l for l in CONFIG['lights'] if l['id'] == light_id), None)
        if not light:
            return jsonify({'success': False, 'error': 'Light not found'}), 404
        
        # Update current state from GPIO
        if light.get('type') == 'pwm':
            brightness = gpio_controller.get_brightness(light['pin'])
            light['brightness'] = brightness
            light['state'] = brightness > 0
        else:
            light['state'] = gpio_controller.get_pin_state(light['pin'])
        
        return jsonify({
            'success': True,
            'light': light
        })
    except Exception as e:
        logger.error(f"Error getting light {light_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/<int:light_id>/toggle', methods=['POST'])
def toggle_light(light_id):
    """Toggle a specific light on/off"""
    try:
        light = next((l for l in CONFIG['lights'] if l['id'] == light_id), None)
        if not light:
            return jsonify({'success': False, 'error': 'Light not found'}), 404
        
        if light.get('type') == 'pwm':
            # For PWM lights, toggle between 0 and 100% brightness
            current_brightness = gpio_controller.get_brightness(light['pin'])
            new_brightness = 0.0 if current_brightness > 0 else 100.0
            gpio_controller.set_brightness(light['pin'], new_brightness)
            light['brightness'] = new_brightness
            light['state'] = new_brightness > 0
            new_state = light['state']
        else:
            # Toggle the light
            new_state = gpio_controller.toggle_pin(light['pin'])
            light['state'] = new_state
        
        logger.info(f"Light {light['name']} (pin {light['pin']}) toggled to {'ON' if new_state else 'OFF'}")
        
        return jsonify({
            'success': True,
            'light': light,
            'message': f"Light {light['name']} turned {'ON' if new_state else 'OFF'}"
        })
    except Exception as e:
        logger.error(f"Error toggling light {light_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/<int:light_id>/set', methods=['POST'])
def set_light(light_id):
    """Set a specific light to on/off state"""
    try:
        data = request.get_json()
        if not data or 'state' not in data:
            return jsonify({'success': False, 'error': 'State parameter required'}), 400
        
        light = next((l for l in CONFIG['lights'] if l['id'] == light_id), None)
        if not light:
            return jsonify({'success': False, 'error': 'Light not found'}), 404
        
        state = bool(data['state'])
        
        if light.get('type') == 'pwm':
            # For PWM lights, set brightness to full or off
            brightness = 100.0 if state else 0.0
            gpio_controller.set_brightness(light['pin'], brightness)
            light['brightness'] = brightness
            light['state'] = state
        else:
            gpio_controller.set_pin(light['pin'], state)
            light['state'] = state
        
        logger.info(f"Light {light['name']} (pin {light['pin']}) set to {'ON' if state else 'OFF'}")
        
        return jsonify({
            'success': True,
            'light': light,
            'message': f"Light {light['name']} turned {'ON' if state else 'OFF'}"
        })
    except Exception as e:
        logger.error(f"Error setting light {light_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/<int:light_id>/brightness', methods=['POST'])
def set_brightness(light_id):
    """Set LED brightness (PWM duty cycle)"""
    try:
        data = request.get_json()
        if not data or 'brightness' not in data:
            return jsonify({'success': False, 'error': 'Brightness parameter required'}), 400
        
        light = next((l for l in CONFIG['lights'] if l['id'] == light_id), None)
        if not light:
            return jsonify({'success': False, 'error': 'Light not found'}), 404
        
        if light.get('type') != 'pwm':
            return jsonify({'success': False, 'error': 'Light does not support brightness control'}), 400
        
        brightness = float(data['brightness'])
        if brightness < 0 or brightness > 100:
            return jsonify({'success': False, 'error': 'Brightness must be between 0 and 100'}), 400
        
        gpio_controller.set_brightness(light['pin'], brightness)
        light['brightness'] = brightness
        light['state'] = brightness > 0
        
        logger.info(f"Light {light['name']} (pin {light['pin']}) brightness set to {brightness}%")
        
        return jsonify({
            'success': True,
            'light': light,
            'message': f"Light {light['name']} brightness set to {brightness}%"
        })
    except Exception as e:
        logger.error(f"Error setting brightness for light {light_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/<int:light_id>/fade', methods=['POST'])
def fade_light(light_id):
    """Fade LED to specified brightness over time"""
    try:
        data = request.get_json()
        if not data or 'brightness' not in data:
            return jsonify({'success': False, 'error': 'Brightness parameter required'}), 400
        
        light = next((l for l in CONFIG['lights'] if l['id'] == light_id), None)
        if not light:
            return jsonify({'success': False, 'error': 'Light not found'}), 404
        
        if light.get('type') != 'pwm':
            return jsonify({'success': False, 'error': 'Light does not support brightness control'}), 400
        
        target_brightness = float(data['brightness'])
        fade_time = float(data.get('fade_time', 1.0))  # Default 1 second
        steps = int(data.get('steps', 50))  # Default 50 steps
        
        if target_brightness < 0 or target_brightness > 100:
            return jsonify({'success': False, 'error': 'Brightness must be between 0 and 100'}), 400
        
        if fade_time <= 0:
            return jsonify({'success': False, 'error': 'Fade time must be positive'}), 400
        
        # Get current brightness
        current_brightness = gpio_controller.get_brightness(light['pin'])
        
        # Calculate step size and delay
        brightness_diff = target_brightness - current_brightness
        step_size = brightness_diff / steps
        step_delay = fade_time / steps
        
        def fade_thread():
            try:
                for step in range(steps + 1):
                    new_brightness = current_brightness + (step_size * step)
                    gpio_controller.set_brightness(light['pin'], new_brightness)
                    time.sleep(step_delay)
                
                # Ensure final brightness is exactly the target
                gpio_controller.set_brightness(light['pin'], target_brightness)
                light['brightness'] = target_brightness
                light['state'] = target_brightness > 0
                
            except Exception as e:
                logger.error(f"Error during fade operation: {str(e)}")
        
        # Start fade in background thread
        threading.Thread(target=fade_thread, daemon=True).start()
        
        logger.info(f"Started fade for light {light['name']} (pin {light['pin']}) to {target_brightness}% over {fade_time}s")
        
        return jsonify({
            'success': True,
            'message': f"Fading light {light['name']} to {target_brightness}% over {fade_time}s"
        })
    except Exception as e:
        logger.error(f"Error starting fade for light {light_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/all/on', methods=['POST'])
def turn_all_lights_on():
    """Turn all lights on"""
    try:
        for light in CONFIG['lights']:
            if light.get('type') == 'pwm':
                gpio_controller.set_brightness(light['pin'], 100.0)
                light['brightness'] = 100.0
                light['state'] = True
            else:
                gpio_controller.set_pin(light['pin'], True)
                light['state'] = True
        
        logger.info("All lights turned ON")
        return jsonify({
            'success': True,
            'lights': CONFIG['lights'],
            'message': 'All lights turned ON'
        })
    except Exception as e:
        logger.error(f"Error turning all lights on: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/all/off', methods=['POST'])
def turn_all_lights_off():
    """Turn all lights off"""
    try:
        for light in CONFIG['lights']:
            if light.get('type') == 'pwm':
                gpio_controller.set_brightness(light['pin'], 0.0)
                light['brightness'] = 0.0
                light['state'] = False
            else:
                gpio_controller.set_pin(light['pin'], False)
                light['state'] = False
        
        logger.info("All lights turned OFF")
        return jsonify({
            'success': True,
            'lights': CONFIG['lights'],
            'message': 'All lights turned OFF'
        })
    except Exception as e:
        logger.error(f"Error turning all lights off: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        return jsonify({
            'success': True,
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'gpio_mode': gpio_controller.get_mode(),
            'total_lights': len(CONFIG['lights']),
            'active_timers': len([t for t in TIMERS if t.get('active', True)])
        })
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Timer Management Routes

@app.route('/api/timers', methods=['GET'])
def get_timers():
    """Get all timers"""
    try:
        with timer_lock:
            return jsonify({
                'success': True,
                'timers': TIMERS
            })
    except Exception as e:
        logger.error(f"Error getting timers: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/timers', methods=['POST'])
def create_timer():
    """Create a new timer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        required_fields = ['light_id', 'action', 'time']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        light_id = int(data['light_id'])
        action = data['action']  # 'on', 'off', or 'brightness'
        timer_time = data['time']  # ISO format or HH:MM
        brightness = data.get('brightness', 100)  # For brightness action
        repeat = data.get('repeat', 'once')  # 'once', 'daily', 'weekdays', 'weekends'
        
        # Validate light exists
        light = next((l for l in CONFIG['lights'] if l['id'] == light_id), None)
        if not light:
            return jsonify({'success': False, 'error': 'Light not found'}), 404
        
        # Validate action
        if action not in ['on', 'off', 'brightness']:
            return jsonify({'success': False, 'error': 'Invalid action. Must be on, off, or brightness'}), 400
        
        # Parse time
        try:
            if 'T' in timer_time:  # ISO format
                scheduled_time = datetime.fromisoformat(timer_time.replace('Z', '+00:00'))
            else:  # HH:MM format
                time_parts = timer_time.split(':')
                now = datetime.now()
                scheduled_time = now.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=0, microsecond=0)
                # If time has passed today, schedule for tomorrow (for repeating timers)
                if scheduled_time <= now and repeat != 'once':
                    scheduled_time += timedelta(days=1)
                elif scheduled_time <= now and repeat == 'once':
                    return jsonify({'success': False, 'error': 'Timer time must be in the future'}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': f'Invalid time format: {str(e)}'}), 400
        
        # Create timer
        timer_id = str(uuid.uuid4())
        timer = {
            'id': timer_id,
            'light_id': light_id,
            'light_name': light['name'],
            'action': action,
            'brightness': brightness if action == 'brightness' else None,
            'time': scheduled_time.isoformat(),
            'repeat': repeat,
            'active': True,
            'created_at': datetime.now().isoformat()
        }
        
        with timer_lock:
            TIMERS.append(timer)
        
        logger.info(f"Timer created: {timer_id} for {light['name']} at {scheduled_time}")
        
        return jsonify({
            'success': True,
            'timer': timer,
            'message': f"Timer set for {light['name']} to {action} at {scheduled_time.strftime('%H:%M')}"
        })
    except Exception as e:
        logger.error(f"Error creating timer: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/timers/<timer_id>', methods=['DELETE'])
def delete_timer(timer_id):
    """Delete a timer"""
    try:
        with timer_lock:
            timer = next((t for t in TIMERS if t['id'] == timer_id), None)
            if not timer:
                return jsonify({'success': False, 'error': 'Timer not found'}), 404
            
            TIMERS.remove(timer)
        
        logger.info(f"Timer deleted: {timer_id}")
        
        return jsonify({
            'success': True,
            'message': 'Timer deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting timer: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/timers/<timer_id>/toggle', methods=['POST'])
def toggle_timer(timer_id):
    """Toggle timer active state"""
    try:
        with timer_lock:
            timer = next((t for t in TIMERS if t['id'] == timer_id), None)
            if not timer:
                return jsonify({'success': False, 'error': 'Timer not found'}), 404
            
            timer['active'] = not timer.get('active', True)
        
        logger.info(f"Timer {timer_id} toggled to {'active' if timer['active'] else 'inactive'}")
        
        return jsonify({
            'success': True,
            'timer': timer,
            'message': f"Timer {'activated' if timer['active'] else 'deactivated'}"
        })
    except Exception as e:
        logger.error(f"Error toggling timer: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

def cleanup_gpio():
    """Clean up GPIO on app shutdown"""
    logger.info("Cleaning up GPIO...")
    gpio_controller.cleanup()

def timer_worker():
    """Background worker to check and execute timers"""
    logger.info("Timer worker started")
    
    while True:
        try:
            now = datetime.now()
            
            with timer_lock:
                timers_to_execute = []
                timers_to_remove = []
                
                for timer in TIMERS:
                    if not timer.get('active', True):
                        continue
                    
                    timer_time = datetime.fromisoformat(timer['time'])
                    
                    # Check if it's time to execute
                    if now >= timer_time:
                        timers_to_execute.append(timer)
                        
                        # Handle repeat logic
                        if timer['repeat'] == 'once':
                            timers_to_remove.append(timer)
                        elif timer['repeat'] == 'daily':
                            # Schedule for next day
                            next_time = timer_time + timedelta(days=1)
                            timer['time'] = next_time.isoformat()
                        elif timer['repeat'] == 'weekdays':
                            # Schedule for next weekday
                            next_time = timer_time + timedelta(days=1)
                            while next_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
                                next_time += timedelta(days=1)
                            timer['time'] = next_time.isoformat()
                        elif timer['repeat'] == 'weekends':
                            # Schedule for next weekend day
                            next_time = timer_time + timedelta(days=1)
                            while next_time.weekday() < 5:  # Monday-Friday = 0-4
                                next_time += timedelta(days=1)
                            timer['time'] = next_time.isoformat()
                
                # Remove one-time timers
                for timer in timers_to_remove:
                    TIMERS.remove(timer)
            
            # Execute timers (outside lock to avoid blocking)
            for timer in timers_to_execute:
                try:
                    light_id = timer['light_id']
                    action = timer['action']
                    light = next((l for l in CONFIG['lights'] if l['id'] == light_id), None)
                    
                    if not light:
                        logger.warning(f"Timer {timer['id']}: Light {light_id} not found")
                        continue
                    
                    if action == 'on':
                        if light.get('type') == 'pwm':
                            gpio_controller.set_brightness(light['pin'], 100.0)
                            light['brightness'] = 100.0
                            light['state'] = True
                        else:
                            gpio_controller.set_pin(light['pin'], True)
                            light['state'] = True
                        logger.info(f"Timer executed: {light['name']} turned ON")
                    
                    elif action == 'off':
                        if light.get('type') == 'pwm':
                            gpio_controller.set_brightness(light['pin'], 0.0)
                            light['brightness'] = 0.0
                            light['state'] = False
                        else:
                            gpio_controller.set_pin(light['pin'], False)
                            light['state'] = False
                        logger.info(f"Timer executed: {light['name']} turned OFF")
                    
                    elif action == 'brightness':
                        if light.get('type') == 'pwm':
                            brightness = timer['brightness']
                            gpio_controller.set_brightness(light['pin'], brightness)
                            light['brightness'] = brightness
                            light['state'] = brightness > 0
                            logger.info(f"Timer executed: {light['name']} brightness set to {brightness}%")
                        else:
                            logger.warning(f"Timer {timer['id']}: Light {light['name']} does not support brightness")
                
                except Exception as e:
                    logger.error(f"Error executing timer {timer.get('id', 'unknown')}: {str(e)}")
            
            # Check every 10 seconds
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"Error in timer worker: {str(e)}")
            time.sleep(10)

if __name__ == '__main__':
    try:
        # Register cleanup function
        import atexit
        atexit.register(cleanup_gpio)
        
        logger.info("Starting GPIO Light Control Web Service...")
        logger.info(f"Configured lights: {[light['name'] for light in CONFIG['lights']]}")
        
        # Start timer worker thread
        timer_thread = threading.Thread(target=timer_worker, daemon=True)
        timer_thread.start()
        logger.info("Timer worker thread started")
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',  # Allow external connections
            port=5000,
            debug=False,  # Set to True for development
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
    finally:
        cleanup_gpio()