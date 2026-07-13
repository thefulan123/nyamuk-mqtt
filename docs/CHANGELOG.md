# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-07-13

### MAJOR: Single Broker Focus

**BREAKING CHANGES:**
- Focus on single broker (removed multi-instance complexity)
- Simplified UI/UX for non-technical users
- Zero-coding broker creation workflow

**New Philosophy:**
```
Broker = "Dumb Router" (just forwards messages)
Topics = Configured by CLIENT (ESP32, Node-RED)
Nyamuk = Configures broker (port, auth, ACL)
User = Creates broker in 30 seconds, ZERO coding
```

### Added

- **broker_manager.py** - Single broker lifecycle management
  - Create broker with name, port, password
  - Auto-detect free ports (1883-1900)
  - Start, stop, restart broker
  - Delete broker with confirmation
  - Get status and connection info

- **port_scanner.py** - Auto-detect free ports
  - Scan ports 1883-1900
  - Check port availability
  - Suggest next available port

- **config_generator.py** - Generate mosquitto.conf
  - Generate config with auth, ACL, persistence
  - Support custom ports and settings
  - Backup old config before overwriting

- **provisioning.py** - ESP32 Config Generator (Level 4)
  - Generate Arduino code snippets
  - Generate platformio.ini
  - Support basic, DHT22, BMP280 sensors
  - One-click copy to clipboard

- **TUI Pages:**
  - **Home** - Status, connection info, ESP32 config snippet
  - **Create** - 3-click broker creation wizard
  - **Users** - User management
  - **ACL** - Access control rules
  - **Config** - Configuration editor
  - **Logs** - Real-time log viewer

- **Web Dashboard:**
  - Simple, clean interface with cards layout
  - Real-time status updates via WebSocket
  - One-click start/stop/restart buttons
  - ESP32 config with copy button
  - User & ACL management

- **CLI Commands:**
  - `nyamuk create` - Create broker interactively
  - `nyamuk start/stop/restart/delete` - Broker lifecycle
  - `nyamuk status` - Show connection info
  - `nyamuk esp32` - Generate ESP32 config snippet
  - `nyamuk user list/add/delete` - User management
  - `nyamuk acl list/add` - ACL rules

### Changed

- Simplified UI/UX for non-technical users
- Focus on single broker instead of multi-instance
- Updated documentation for v2.0 philosophy

### Removed

- Multi-broker management (deferred to v3.0 if demand exists)
- Complex configuration options (simplified for v2.0)

### Security

- Passwords stored in hashed format
- ACL-based topic access control
- Configurable web dashboard authentication

## [1.0.0] - 2024-01-15

### Added

- TUI Dashboard with terminal-based UI
- Web Dashboard with real-time monitoring
- CLI interface for all operations
- User management (CRUD)
- ACL management (topic-based access control)
- Real-time MQTT monitoring
- Log viewer and parser
- Configuration management
- Docker container management
- ESP32 templates (Basic, DHT22, BMP280, Advanced)
- Cross-platform support (Linux, macOS, Windows)
- REST API for external integrations
- WebSocket for real-time updates
- Comprehensive documentation
- Unit tests

### Features

- Parse and modify `mosquitto.conf`
- Add/delete MQTT users via `mosquitto_passwd`
- Manage ACL rules
- Monitor broker status, CPU, memory usage
- View real-time logs
- Export/import configuration
- OTA update support for ESP32

### ESP32 Templates

- Basic sensor template
- DHT22 temperature/humidity sensor
- BMP280 temperature/pressure/altitude sensor
- Advanced template with OTA, deep sleep, watchdog

## [0.1.0] - Unreleased

### Planned

- Plugin system
- Custom themes
- Mobile app
- Backup/restore functionality
- Scheduled tasks
- Notifications
- Multi-language support
