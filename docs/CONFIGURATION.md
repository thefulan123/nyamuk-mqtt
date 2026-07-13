# Configuration Reference

## Configuration Files

### config.json

Main application configuration:

```json
{
  "mqtt_broker": "localhost",
  "mqtt_port": 1883,
  "topic_prefix": "nyamuk",
  "web_port": 8080,
  "web_admin_user": "admin",
  "web_admin_pass": "nyamuk123"
}
```

### .env

Environment variables:

```bash
MQTT_BROKER=localhost
MQTT_PORT=1883
WEB_PORT=8080
WEB_SECRET_KEY=change-me-in-production
WEB_ADMIN_USER=admin
WEB_ADMIN_PASS=nyamuk123
```

## Mosquitto Configuration

Nyamuk manages `mosquitto.conf` file:

```bash
# View current config
nyamuk config show

# Set configuration value
nyamuk config set listener 1883
nyamuk config set allow_anonymous false

# Validate configuration
nyamuk config validate
```

## User Management

```bash
# List users
nyamuk user list

# Add user
nyamuk user add esp32_sensor

# Delete user
nyamuk user delete old_device

# Change password
nyamuk user password esp32_sensor
```

## ACL Management

```bash
# List rules
nyamuk acl list

# Add rule
nyamuk acl add esp32_sensor "nyamuk/esp32/#" --access readwrite

# Delete rule
nyamuk acl delete esp32_sensor "nyamuk/esp32/#"
```

## Topic Structure

Default topic prefix: `nyamuk`

```
nyamuk/{device_id}/sensor    # Sensor data (publish)
nyamuk/{device_id}/command   # Commands (subscribe)
nyamuk/{device_id}/status    # Device status (publish)
nyamuk/{device_id}/alert     # Alerts (publish)
```

## TLS Configuration

Enable TLS in `mosquitto.conf`:

```
listener 8883
cafile /mosquitto/certs/ca.crt
certfile /mosquitto/certs/server.crt
keyfile /mosquitto/certs/server.key
```
