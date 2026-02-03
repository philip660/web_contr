#!/usr/bin/env python3
"""
GPIO Controller Module
Handles all GPIO pin operations for light control
Supports both Raspberry Pi hardware and simulation mode for development
"""

import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class GPIOController:
    """GPIO Controller for managing light control pins"""
    
    def __init__(self, simulation_mode: bool = None):
        """
        Initialize GPIO Controller
        
        Args:
            simulation_mode: If True, run in simulation mode. If None, auto-detect.
        """
        self.pins: Dict[int, bool] = {}  # pin -> state mapping
        self.pwm_pins: Dict[int, any] = {}  # pin -> PWM object mapping
        self.pwm_values: Dict[int, float] = {}  # pin -> PWM duty cycle (0-100)
        self.simulation_mode = simulation_mode
        
        if simulation_mode is None:
            # Auto-detect if we're on a Raspberry Pi
            try:
                import RPi.GPIO as GPIO
                self.simulation_mode = False
                self.GPIO = GPIO
                logger.info("Raspberry Pi GPIO detected - using hardware mode")
            except ImportError:
                self.simulation_mode = True
                self.GPIO = None
                logger.info("RPi.GPIO not available - using simulation mode")
        
        if not self.simulation_mode:
            # Initialize GPIO for Raspberry Pi
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setwarnings(False)
            logger.info("GPIO initialized in BCM mode")
        else:
            # Simulation mode for development/testing
            logger.info("GPIO controller running in simulation mode")
    
    def setup_pin(self, pin: int, initial_state: bool = False) -> None:
        """
        Setup a GPIO pin for output
        
        Args:
            pin: GPIO pin number (BCM numbering)
            initial_state: Initial state of the pin (True = HIGH/ON, False = LOW/OFF)
        """
        try:
            if not self.simulation_mode:
                self.GPIO.setup(pin, self.GPIO.OUT, initial=self.GPIO.HIGH if initial_state else self.GPIO.LOW)
                logger.info(f"Pin {pin} configured as output, initial state: {'HIGH' if initial_state else 'LOW'}")
            else:
                logger.info(f"[SIMULATION] Pin {pin} configured as output, initial state: {'HIGH' if initial_state else 'LOW'}")
            
            self.pins[pin] = initial_state
            
        except Exception as e:
            logger.error(f"Error setting up pin {pin}: {str(e)}")
            raise
    
    def setup_pwm_pin(self, pin: int, frequency: float = 1000, initial_duty: float = 0) -> None:
        """
        Setup a GPIO pin for PWM output
        
        Args:
            pin: GPIO pin number (BCM numbering)
            frequency: PWM frequency in Hz (default 1000Hz)
            initial_duty: Initial duty cycle percentage (0-100)
        """
        try:
            if not self.simulation_mode:
                self.GPIO.setup(pin, self.GPIO.OUT)
                pwm_obj = self.GPIO.PWM(pin, frequency)
                pwm_obj.start(initial_duty)
                self.pwm_pins[pin] = pwm_obj
                logger.info(f"Pin {pin} configured for PWM output at {frequency}Hz, initial duty: {initial_duty}%")
            else:
                logger.info(f"[SIMULATION] Pin {pin} configured for PWM output at {frequency}Hz, initial duty: {initial_duty}%")
                self.pwm_pins[pin] = {'frequency': frequency, 'duty_cycle': initial_duty}
            
            self.pwm_values[pin] = initial_duty
            
        except Exception as e:
            logger.error(f"Error setting up PWM pin {pin}: {str(e)}")
            raise
    
    def set_pin(self, pin: int, state: bool) -> None:
        """
        Set a GPIO pin to HIGH or LOW
        
        Args:
            pin: GPIO pin number
            state: True for HIGH/ON, False for LOW/OFF
        """
        if pin not in self.pins:
            raise ValueError(f"Pin {pin} not configured. Call setup_pin() first.")
        
        try:
            if not self.simulation_mode:
                self.GPIO.output(pin, self.GPIO.HIGH if state else self.GPIO.LOW)
                logger.debug(f"Pin {pin} set to {'HIGH' if state else 'LOW'}")
            else:
                logger.debug(f"[SIMULATION] Pin {pin} set to {'HIGH' if state else 'LOW'}")
            
            self.pins[pin] = state
            
        except Exception as e:
            logger.error(f"Error setting pin {pin} to {'HIGH' if state else 'LOW'}: {str(e)}")
            raise
    
    def set_pwm_duty_cycle(self, pin: int, duty_cycle: float) -> None:
        """
        Set PWM duty cycle for a pin
        
        Args:
            pin: GPIO pin number
            duty_cycle: Duty cycle percentage (0-100)
        """
        if pin not in self.pwm_pins:
            raise ValueError(f"Pin {pin} not configured for PWM. Call setup_pwm_pin() first.")
        
        # Clamp duty cycle to valid range
        duty_cycle = max(0.0, min(100.0, duty_cycle))
        
        try:
            if not self.simulation_mode:
                self.pwm_pins[pin].ChangeDutyCycle(duty_cycle)
                logger.debug(f"PWM pin {pin} duty cycle set to {duty_cycle}%")
            else:
                self.pwm_pins[pin]['duty_cycle'] = duty_cycle
                logger.debug(f"[SIMULATION] PWM pin {pin} duty cycle set to {duty_cycle}%")
            
            self.pwm_values[pin] = duty_cycle
            
        except Exception as e:
            logger.error(f"Error setting PWM duty cycle for pin {pin}: {str(e)}")
            raise
    
    def get_pwm_duty_cycle(self, pin: int) -> float:
        """
        Get the current PWM duty cycle for a pin
        
        Args:
            pin: GPIO pin number
            
        Returns:
            Current duty cycle percentage (0-100)
        """
        if pin not in self.pwm_pins:
            raise ValueError(f"Pin {pin} not configured for PWM. Call setup_pwm_pin() first.")
        
        return self.pwm_values[pin]
    
    def set_brightness(self, pin: int, brightness: float) -> None:
        """
        Set LED brightness (convenience method for PWM duty cycle)
        
        Args:
            pin: GPIO pin number
            brightness: Brightness percentage (0-100)
        """
        self.set_pwm_duty_cycle(pin, brightness)
    
    def get_brightness(self, pin: int) -> float:
        """
        Get LED brightness (convenience method for PWM duty cycle)
        
        Args:
            pin: GPIO pin number
            
        Returns:
            Current brightness percentage (0-100)
        """
        return self.get_pwm_duty_cycle(pin)
    
    def get_pin_state(self, pin: int) -> bool:
        """
        Get the current state of a GPIO pin
        
        Args:
            pin: GPIO pin number
            
        Returns:
            Current state (True = HIGH/ON, False = LOW/OFF)
        """
        if pin not in self.pins:
            raise ValueError(f"Pin {pin} not configured. Call setup_pin() first.")
        
        return self.pins[pin]
    
    def toggle_pin(self, pin: int) -> bool:
        """
        Toggle a GPIO pin state
        
        Args:
            pin: GPIO pin number
            
        Returns:
            New state after toggle
        """
        if pin not in self.pins:
            raise ValueError(f"Pin {pin} not configured. Call setup_pin() first.")
        
        new_state = not self.pins[pin]
        self.set_pin(pin, new_state)
        return new_state
    
    def get_all_states(self) -> Dict[int, bool]:
        """
        Get states of all configured pins
        
        Returns:
            Dictionary mapping pin numbers to their states
        """
        return self.pins.copy()
    
    def turn_all_on(self) -> None:
        """Turn all configured pins ON (HIGH)"""
        for pin in self.pins.keys():
            self.set_pin(pin, True)
        logger.info("All pins turned ON")
    
    def turn_all_off(self) -> None:
        """Turn all configured pins OFF (LOW)"""
        for pin in self.pins.keys():
            self.set_pin(pin, False)
        logger.info("All pins turned OFF")
    
    def get_configured_pins(self) -> List[int]:
        """Get list of all configured pin numbers"""
        return list(self.pins.keys())
    
    def get_mode(self) -> str:
        """Get the current GPIO mode"""
        return "simulation" if self.simulation_mode else "hardware"
    
    def cleanup(self) -> None:
        """Clean up GPIO resources"""
        try:
            if not self.simulation_mode and self.GPIO:
                # Stop all PWM pins
                for pin, pwm_obj in self.pwm_pins.items():
                    try:
                        pwm_obj.stop()
                    except:
                        pass  # Ignore errors during cleanup
                
                # Turn off all digital pins before cleanup
                for pin in self.pins.keys():
                    try:
                        self.GPIO.output(pin, self.GPIO.LOW)
                    except:
                        pass  # Ignore errors during cleanup
                
                self.GPIO.cleanup()
                logger.info("GPIO cleanup completed")
            else:
                logger.info("[SIMULATION] GPIO cleanup completed")
                
        except Exception as e:
            logger.error(f"Error during GPIO cleanup: {str(e)}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()

# Test functions for development
def test_gpio_controller():
    """Test the GPIO controller functionality"""
    print("Testing GPIO Controller...")
    
    controller = GPIOController(simulation_mode=True)
    
    # Test pin setup
    test_pins = [18, 19, 20, 21]
    for pin in test_pins:
        controller.setup_pin(pin)
    
    print(f"Configured pins: {controller.get_configured_pins()}")
    print(f"Mode: {controller.get_mode()}")
    
    # Test individual pin control
    for pin in test_pins:
        print(f"\nTesting pin {pin}:")
        print(f"  Initial state: {controller.get_pin_state(pin)}")
        
        controller.set_pin(pin, True)
        print(f"  After setting ON: {controller.get_pin_state(pin)}")
        
        controller.toggle_pin(pin)
        print(f"  After toggle: {controller.get_pin_state(pin)}")
        
        controller.toggle_pin(pin)
        print(f"  After second toggle: {controller.get_pin_state(pin)}")
    
    # Test all pins control
    print(f"\nAll states before turn_all_on: {controller.get_all_states()}")
    controller.turn_all_on()
    print(f"All states after turn_all_on: {controller.get_all_states()}")
    
    controller.turn_all_off()
    print(f"All states after turn_all_off: {controller.get_all_states()}")
    
    controller.cleanup()
    print("\nTest completed!")

if __name__ == "__main__":
    test_gpio_controller()