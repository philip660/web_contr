# Timer Feature - Quick Reference Card

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/timers` | Get all timers |
| POST | `/api/timers` | Create new timer |
| DELETE | `/api/timers/{id}` | Delete timer |
| POST | `/api/timers/{id}/toggle` | Pause/resume timer |

## Create Timer Request

```json
{
  "light_id": 1,              // Required: 1-4
  "action": "on",             // Required: "on", "off", "brightness"
  "time": "18:30",            // Required: HH:MM format
  "brightness": 50,           // Optional: 0-100 (for "brightness" action)
  "repeat": "daily"           // Required: "once", "daily", "weekdays", "weekends"
}
```

## Repeat Options

| Option | Description | Example |
|--------|-------------|---------|
| `once` | Execute once, then delete | One-time event |
| `daily` | Every day | Every day at 6:00 PM |
| `weekdays` | Monday-Friday | Workday mornings |
| `weekends` | Saturday-Sunday | Weekend sleep-in |

## Actions

| Action | Description | Brightness Field |
|--------|-------------|------------------|
| `on` | Turn light ON | Not used |
| `off` | Turn light OFF | Not used |
| `brightness` | Set brightness % | Required (0-100) |

## Timer States

| State | Visual | Description |
|-------|--------|-------------|
| Active | 🟢 Green border | Will execute |
| Inactive | ⚪ Gray border | Paused |

## UI Buttons

| Button | Function |
|--------|----------|
| ⏸ | Pause active timer |
| ▶️ | Resume inactive timer |
| 🗑️ | Delete timer |
| ➕ | Create new timer |

## cURL Examples

### Create Daily Timer
```bash
curl -X POST http://localhost:5000/api/timers \
  -H "Content-Type: application/json" \
  -d '{"light_id":1,"action":"on","time":"18:30","repeat":"daily"}'
```

### Create Brightness Timer
```bash
curl -X POST http://localhost:5000/api/timers \
  -H "Content-Type: application/json" \
  -d '{"light_id":2,"action":"brightness","brightness":50,"time":"22:00","repeat":"weekdays"}'
```

### Get All Timers
```bash
curl http://localhost:5000/api/timers
```

### Delete Timer
```bash
curl -X DELETE http://localhost:5000/api/timers/{timer_id}
```

### Toggle Timer
```bash
curl -X POST http://localhost:5000/api/timers/{timer_id}/toggle
```

## JavaScript Examples

### Create Timer
```javascript
fetch('/api/timers', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    light_id: 1,
    action: 'on',
    time: '18:30',
    repeat: 'daily'
  })
})
```

### Get Timers
```javascript
fetch('/api/timers')
  .then(res => res.json())
  .then(data => console.log(data.timers))
```

### Delete Timer
```javascript
fetch(`/api/timers/${timerId}`, {
  method: 'DELETE'
})
```

## Python Examples

### Create Timer
```python
import requests

response = requests.post('http://localhost:5000/api/timers', json={
    'light_id': 1,
    'action': 'on',
    'time': '18:30',
    'repeat': 'daily'
})
print(response.json())
```

### Get All Timers
```python
response = requests.get('http://localhost:5000/api/timers')
timers = response.json()['timers']
```

## Common Patterns

### Morning Automation
```json
{"light_id":2, "action":"on", "time":"06:00", "repeat":"weekdays"}
{"light_id":4, "action":"brightness", "brightness":50, "time":"06:00", "repeat":"weekdays"}
```

### Evening Automation
```json
{"light_id":1, "action":"on", "time":"18:00", "repeat":"daily"}
{"light_id":1, "action":"brightness", "brightness":30, "time":"22:00", "repeat":"daily"}
```

### Night Shutdown
```json
{"light_id":1, "action":"off", "time":"23:00", "repeat":"daily"}
{"light_id":2, "action":"off", "time":"23:00", "repeat":"daily"}
{"light_id":3, "action":"off", "time":"23:00", "repeat":"daily"}
{"light_id":4, "action":"off", "time":"23:00", "repeat":"daily"}
```

## Time Format

| Format | Example | Description |
|--------|---------|-------------|
| HH:MM | 06:00 | 6:00 AM |
| HH:MM | 18:30 | 6:30 PM |
| HH:MM | 23:59 | 11:59 PM |
| HH:MM | 00:00 | Midnight |

⚠️ **Always use 24-hour format**

## Validation Rules

| Field | Rule |
|-------|------|
| light_id | Must exist (1-4) |
| action | Must be "on", "off", or "brightness" |
| time | Must be HH:MM format |
| brightness | 0-100 (required for "brightness" action) |
| repeat | Must be "once", "daily", "weekdays", or "weekends" |

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (validation error) |
| 404 | Timer/Light not found |
| 500 | Server error |

## Error Handling

```javascript
try {
  const response = await fetch('/api/timers', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(timerData)
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    console.error('Error:', data.error);
  } else {
    console.log('Success:', data.message);
  }
} catch (error) {
  console.error('Network error:', error);
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Timer not executing | Check active status, verify time is future |
| 400 error | Validate all required fields |
| 404 error | Verify light_id exists |
| Timer disappeared | One-time timers delete after execution |
| Wrong time | Use 24-hour format, check server timezone |

## Files

| File | Purpose |
|------|---------|
| app.py | Backend implementation |
| templates/index.html | Frontend UI |
| test_timers.py | API tests |
| TIMER_FEATURE.md | Full documentation |
| TIMER_UI_GUIDE.md | UI guide |

---

**Need More Help?** Check the full documentation files for detailed information.
