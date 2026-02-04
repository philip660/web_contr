# Timer Feature Documentation

## Overview
The GPIO Light Control Web Service now includes a comprehensive timer feature that allows you to schedule lights to turn on/off or set brightness at specific times.

## Features

### Timer Actions
- **Turn ON**: Schedule a light to turn on at a specific time
- **Turn OFF**: Schedule a light to turn off at a specific time
- **Set Brightness**: Schedule a PWM light to change to a specific brightness level (0-100%)

### Repeat Options
- **Once**: Timer executes only once at the specified time
- **Daily**: Timer repeats every day at the same time
- **Weekdays**: Timer repeats Monday through Friday
- **Weekends**: Timer repeats Saturday and Sunday

### Timer Management
- **Add Timer**: Create a new scheduled timer
- **Toggle Timer**: Pause/resume a timer without deleting it
- **Delete Timer**: Permanently remove a timer
- **View All Timers**: See all scheduled timers with their status

## API Endpoints

### Get All Timers
```
GET /api/timers
```
Returns a list of all timers with their configuration.

### Create Timer
```
POST /api/timers
Content-Type: application/json

{
  "light_id": 1,
  "action": "on",           // "on", "off", or "brightness"
  "time": "18:30",          // HH:MM format
  "brightness": 50,         // Optional, only for "brightness" action
  "repeat": "daily"         // "once", "daily", "weekdays", "weekends"
}
```

### Delete Timer
```
DELETE /api/timers/{timer_id}
```
Permanently removes a timer.

### Toggle Timer
```
POST /api/timers/{timer_id}/toggle
```
Activates or deactivates a timer without deleting it.

## How It Works

1. **Timer Worker Thread**: A background thread runs continuously, checking for timers that need to be executed every 10 seconds.

2. **Timer Execution**: When a timer's scheduled time arrives, the timer worker:
   - Executes the specified action (on/off/brightness)
   - Updates the light state
   - Logs the execution
   - For repeating timers, calculates and sets the next execution time
   - For one-time timers, removes the timer after execution

3. **Repeat Logic**:
   - **Daily**: Adds 24 hours to the next execution time
   - **Weekdays**: Schedules for the next weekday (skips weekends)
   - **Weekends**: Schedules for the next weekend day (skips weekdays)

## User Interface

### Timer Section
- Located at the bottom of the main page
- Shows all active and inactive timers
- Displays timer details: light name, action, schedule
- Color-coded indicators for active/inactive status

### Adding a Timer
1. Click the "➕ Add Timer" button
2. Select the light to control
3. Choose the action (On/Off/Brightness)
4. Set the time (HH:MM format)
5. Select repeat option
6. Click "Create Timer"

### Managing Timers
- **Pause/Resume**: Click the ⏸/▶️ button to toggle timer active state
- **Delete**: Click the 🗑️ button to permanently remove the timer

## Examples

### Example 1: Turn on Living Room light at 6:30 PM daily
```json
{
  "light_id": 1,
  "action": "on",
  "time": "18:30",
  "repeat": "daily"
}
```

### Example 2: Dim Bedroom light to 25% at 10 PM on weekdays
```json
{
  "light_id": 3,
  "action": "brightness",
  "brightness": 25,
  "time": "22:00",
  "repeat": "weekdays"
}
```

### Example 3: Turn off all lights at midnight once
```json
{
  "light_id": 1,
  "action": "off",
  "time": "00:00",
  "repeat": "once"
}
```

## Technical Details

### Data Structure
Each timer contains:
- `id`: Unique UUID
- `light_id`: ID of the light to control
- `light_name`: Name of the light (for display)
- `action`: "on", "off", or "brightness"
- `brightness`: Target brightness (0-100) for brightness action
- `time`: ISO format timestamp of next execution
- `repeat`: "once", "daily", "weekdays", or "weekends"
- `active`: Boolean indicating if timer is active
- `created_at`: ISO format timestamp of creation

### Thread Safety
- Timer operations use a threading lock (`timer_lock`) to ensure thread-safe access
- The timer worker thread runs independently without blocking the main Flask application

### Persistence
⚠️ **Note**: Timers are currently stored in memory and will be lost when the application restarts. For production use, consider implementing persistent storage (e.g., SQLite, JSON file, or database).

## Future Enhancements
- Persistent timer storage (database or file)
- More complex scheduling (specific days of week, date ranges)
- Timer groups (turn multiple lights on/off together)
- Sunrise/sunset based timers
- Random offset for security (simulate presence)
- Timer history and logs
