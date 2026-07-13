# 🦟 Nyamuk

> The friendly mosquito for your MQTT broker

Mosquitto MQTT Manager with TUI & Web Dashboard - configure, monitor, and manage your IoT infrastructure without coding.

## Features

- **TUI Dashboard** - Terminal-based UI for SSH access
- **Web Dashboard** - Browser-based monitoring
- **CLI Interface** - Command-line management
- **User Management** - Add/delete MQTT users
- **ACL Management** - Topic-based access control
- **Real-time Monitoring** - Live broker stats
- **ESP32 Templates** - Ready-to-use Arduino sketches

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/thefulan123/nyamuk-mqtt.git
cd nyamuk-mqtt

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### Usage

```bash
# Launch TUI Dashboard
nyamuk tui

# Launch Web Dashboard
nyamuk web --port 8080

# CLI commands
nyamuk status
nyamuk user list
nyamuk config show
```

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Configuration Reference](docs/CONFIGURATION.md)
- [CLI Reference](docs/CLI_REFERENCE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Contributing](docs/CONTRIBUTING.md)

## Examples

Check the [examples](examples/) directory for ESP32 templates:
- Basic sensor template
- DHT22 temperature/humidity
- BMP280 temperature/pressure/altitude
- Advanced with OTA updates

## License

MIT License - see [LICENSE](LICENSE) for details.
