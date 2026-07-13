# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- Multi-broker support
- Plugin system
- Custom themes
- Mobile app
- Backup/restore functionality
- Scheduled tasks
- Notifications
- Multi-language support
