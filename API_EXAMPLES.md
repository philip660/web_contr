# API Examples for GPIO Light Control Web Service

This file contains example API calls using curl and Python requests.

## Using curl

### Get all lights status
```bash
curl -X GET http://localhost:5000/api/lights
```

### Get specific light status
```bash
curl -X GET http://localhost:5000/api/lights/1
```

### Toggle a light
```bash
curl -X POST http://localhost:5000/api/lights/1/toggle
```

### Set a light to ON
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"state": true}' \
     http://localhost:5000/api/lights/1/set
```

### Set a light to OFF
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"state": false}' \
     http://localhost:5000/api/lights/1/set
```

### Turn all lights ON
```bash
curl -X POST http://localhost:5000/api/lights/all/on
```

### Turn all lights OFF
```bash
curl -X POST http://localhost:5000/api/lights/all/off
```

### Get system status
```bash
curl -X GET http://localhost:5000/api/status
```

## Using Python requests

```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

# Get all lights
response = requests.get(f"{BASE_URL}/lights")
print(json.dumps(response.json(), indent=2))

# Toggle light 1
response = requests.post(f"{BASE_URL}/lights/1/toggle")
print(json.dumps(response.json(), indent=2))

# Set light 2 to ON
response = requests.post(
    f"{BASE_URL}/lights/2/set",
    json={"state": True}
)
print(json.dumps(response.json(), indent=2))

# Turn all lights OFF
response = requests.post(f"{BASE_URL}/lights/all/off")
print(json.dumps(response.json(), indent=2))
```

## Using JavaScript (fetch)

```javascript
const BASE_URL = '/api';

// Get all lights
fetch(`${BASE_URL}/lights`)
    .then(response => response.json())
    .then(data => console.log(data));

// Toggle light 1
fetch(`${BASE_URL}/lights/1/toggle`, {
    method: 'POST'
})
    .then(response => response.json())
    .then(data => console.log(data));

// Set light 2 to ON
fetch(`${BASE_URL}/lights/2/set`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({state: true})
})
    .then(response => response.json())
    .then(data => console.log(data));
```