# API Reference

## REST API Endpoints

### Health Check

```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Broker Status

```
GET /api/status
```

**Response:**
```json
{
  "status": {
    "name": "mosquitto",
    "status": "running",
    "image": "eclipse-mosquitto:2",
    "started_at": "2024-01-15T10:00:00"
  },
  "stats": {
    "cpu_percent": 2.5,
    "memory_percent": 15.3,
    "memory_usage": 52428800,
    "memory_limit": 343597383680
  }
}
```

### Configuration

#### Get Configuration

```
GET /api/config
```

**Response:**
```json
{
  "listener": 1883,
  "allow_anonymous": true,
  "persistence": true,
  "persistence_location": "/mosquitto/data/",
  "log_dest": "file /mosquitto/log/mosquitto.log"
}
```

#### Set Configuration

```
POST /api/config
Content-Type: application/json

{
  "listener": 1883,
  "allow_anonymous": false,
  "persistence": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration saved"
}
```

### Users

#### List Users

```
GET /api/users
```

**Response:**
```json
{
  "users": ["esp32_sensor", "admin", "gateway"]
}
```

#### Add User

```
POST /api/users
Content-Type: application/json

{
  "username": "esp32_new",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User 'esp32_new' added successfully"
}
```

#### Delete User

```
DELETE /api/users/esp32_new
```

**Response:**
```json
{
  "success": true,
  "message": "User 'esp32_new' deleted successfully"
}
```

### ACL Rules

#### List Rules

```
GET /api/acl
```

**Response:**
```json
{
  "rules": [
    {
      "username": "esp32_sensor",
      "topic": "nyamuk/esp32/#",
      "access": "readwrite"
    }
  ]
}
```

#### Add Rule

```
POST /api/acl
Content-Type: application/json

{
  "username": "esp32_sensor",
  "topic": "nyamuk/esp32/sensor",
  "access": "readwrite"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Rule added: esp32_sensor -> nyamuk/esp32/sensor (readwrite)"
}
```

### Logs

#### Get Logs

```
GET /api/logs
```

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "level": "info",
      "message": "Client connected",
      "client_id": "ESP32-001"
    }
  ]
}
```

## WebSocket Events

### Connection

```javascript
const socket = io();

socket.on('connect', function() {
    console.log('Connected to Nyamuk');
});
```

### Status Updates

```javascript
// Request status
socket.emit('request_status');

// Receive status
socket.on('status_update', function(data) {
    console.log(data.status);
    console.log(data.stats);
});
```

### Real-time Messages

```javascript
// Receive messages
socket.on('message_received', function(data) {
    console.log(data.topic);
    console.log(data.payload);
    console.log(data.timestamp);
});
```

## Authentication

Web dashboard requires authentication:

```
POST /login
Content-Type: application/x-www-form-urlencoded

username=admin&password=nyamuk123
```

Session cookies are used for subsequent requests.

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "message": "Error description"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `500` - Internal Server Error
