#!/usr/bin/env python3
"""
Test script for Timer API endpoints
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

def test_get_timers():
    """Test getting all timers"""
    print("\n1. Testing GET /api/timers...")
    response = requests.get(f"{BASE_URL}/timers")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_create_timer():
    """Test creating a timer"""
    print("\n2. Testing POST /api/timers...")
    
    # Create a timer for 5 minutes from now
    future_time = (datetime.now() + timedelta(minutes=5)).strftime("%H:%M")
    
    timer_data = {
        "light_id": 1,
        "action": "on",
        "time": future_time,
        "repeat": "once"
    }
    
    response = requests.post(f"{BASE_URL}/timers", json=timer_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json().get('timer', {}).get('id')
    return None

def test_create_brightness_timer():
    """Test creating a brightness timer"""
    print("\n3. Testing POST /api/timers (brightness)...")
    
    future_time = (datetime.now() + timedelta(minutes=10)).strftime("%H:%M")
    
    timer_data = {
        "light_id": 2,
        "action": "brightness",
        "brightness": 50,
        "time": future_time,
        "repeat": "daily"
    }
    
    response = requests.post(f"{BASE_URL}/timers", json=timer_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json().get('timer', {}).get('id')
    return None

def test_toggle_timer(timer_id):
    """Test toggling a timer"""
    if not timer_id:
        print("\n4. Skipping toggle test (no timer ID)")
        return
    
    print(f"\n4. Testing POST /api/timers/{timer_id}/toggle...")
    response = requests.post(f"{BASE_URL}/timers/{timer_id}/toggle")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_delete_timer(timer_id):
    """Test deleting a timer"""
    if not timer_id:
        print("\n5. Skipping delete test (no timer ID)")
        return
    
    print(f"\n5. Testing DELETE /api/timers/{timer_id}...")
    response = requests.delete(f"{BASE_URL}/timers/{timer_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_status():
    """Test status endpoint"""
    print("\n6. Testing GET /api/status...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("=" * 60)
    print("GPIO Light Control - Timer API Test Suite")
    print("=" * 60)
    print("\nMake sure the Flask app is running on localhost:5000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    try:
        # Run tests
        test_get_timers()
        
        timer_id_1 = test_create_timer()
        timer_id_2 = test_create_brightness_timer()
        
        test_get_timers()
        
        test_toggle_timer(timer_id_1)
        test_delete_timer(timer_id_2)
        
        test_get_timers()
        test_status()
        
        print("\n" + "=" * 60)
        print("Test suite completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the Flask app is running on localhost:5000")
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
