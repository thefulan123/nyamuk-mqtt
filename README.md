# 🦟 Nyamuk v2.0

> **MQTT Broker Factory** - Create your MQTT broker in 30 seconds, zero coding required.

No-code MQTT broker configurator for VPS that lets non-technical users create, configure, and manage Mosquitto MQTT brokers with TUI and Web dashboard interfaces, plus ESP32 provisioning.

## ✨ What is Nyamuk?

```
┌─────────────────────────────────────────────────────────┐
│                    NYAMUK v2.0                           │
│                                                         │
│  User creates broker ──→ Nyamuk configures ──→ Ready   │
│       (3 clicks)            (automatic)         (30s)   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Nyamuk** is a "broker factory" - you click, configure, and your broker is ready. No coding required. Accessible to ordinary people.

## 🎯 Philosophy

```
Broker = "Dumb Router" (cuma teruskan pesan)
Topics = Dikonfigurasi di CLIENT (ESP32, Node-RED)
Nyamuk = Configures broker (port, auth, ACL)
User = Creates broker in 30 seconds, ZERO coding
```

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **30-Second Setup** | Create MQTT broker with 3 clicks |
| **Auto Port Detection** | Automatically finds free ports (1883-1900) |
| **ESP32 Provisioning** | One-click config generation for Arduino |
| **TUI Dashboard** | Terminal UI for SSH access |
| **Web Dashboard** | Browser-based monitoring & management |
| **CLI Interface** | Command-line for automation |
| **User Management** | Add/delete MQTT users |
| **ACL Management** | Topic-based access control |
| **Real-time Monitoring** | Live broker stats & logs |

## 📦 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/thefulan123/nyamuk-mqtt.git
cd nyamuk-mqtt

# Install as package
pip install -e .

# Or install dependencies
pip install -r requirements.txt
```

### Create Your First Broker

```bash
# Method 1: Interactive CLI (Recommended)
nyamuk create

# Follow the prompts:
# Broker name: my_broker
# Port: 1883 (auto-detected)
# Password: **** (auto-generated if empty)

# Start the broker
nyamuk start
```

### Get Connection Info

```bash
# View status and connection info
nyamuk status

# Output:
# 🦟 Nyamuk MQTT Broker Status:
#   Name: my_broker
#   Status: 🟢 Running
#   Port: 1883
#
# 📡 Connection Info:
#   Broker: 192.168.1.100:1883
#   Username: nyamuk
#   Password: abc123xyz
#   Topic: nyamuk/#
```

### ESP32 Configuration

```bash
# Generate ESP32 config snippet
nyamuk esp32

# Copy output to your Arduino sketch
```

## 🖥️ Interfaces

### 1. CLI (Command Line)

```bash
# Broker lifecycle
nyamuk create          # Create broker
nyamuk start           # Start broker
nyamuk stop            # Stop broker
nyamuk restart         # Restart broker
nyamuk delete          # Delete broker (with confirmation)

# User management
nyamuk user list       # List all users
nyamuk user add <user> # Add user (prompts for password)
nyamuk user delete <user> # Delete user

# ACL management
nyamuk acl list        # List ACL rules
nyamuk acl add <user> <topic> --access readwrite

# ESP32 provisioning
nyamuk esp32           # Generate config snippet

# Status
nyamuk status          # Show broker status & connection info
```

### 2. TUI Dashboard (Terminal UI)

```bash
# Launch TUI
nyamuk tui
```

**Pages:**
- 🏠 **Home** - Status, connection info, ESP32 config snippet
- ➕ **Create** - Create new broker (3-click wizard)
- 👥 **Users** - User management
- 🔒 **ACL** - Access control rules
- ⚙️ **Config** - Configuration editor
- 📋 **Logs** - Real-time log viewer

### 3. Web Dashboard (Browser)

```bash
# Launch Web Dashboard
nyamuk web --port 8080

# Open browser: http://your-vps:8080
```

**Features:**
- Real-time status updates
- One-click start/stop/restart
- ESP32 config with copy button
- User & ACL management
- Log viewer

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Web Dashboard
WEB_HOST=0.0.0.0
WEB_PORT=8080
WEB_SECRET_KEY=your-secret-key-here
WEB_ADMIN_USER=admin
WEB_ADMIN_PASS=your-secure-password

# Debug mode
NYAMUK_DEBUG=false
```

### Mosquitto Configuration

Nyamuk generates `mosquitto.conf` automatically. Advanced users can edit:

```bash
# Edit via TUI
nyamuk tui → Config page

# Or manually edit
/opt/mosquitto/config/mosquitto.conf
```

## 📁 Project Structure

```
nyamuk-mqtt/
├── nyamuk/
│   ├── core/               # Core modules
│   │   ├── broker_manager.py    # Broker lifecycle
│   │   ├── config_generator.py  # Config generation
│   │   ├── port_scanner.py      # Port detection
│   │   ├── provisioning.py      # ESP32 provisioning
│   │   ├── user_manager.py      # User CRUD
│   │   ├── acl_manager.py       # ACL rules
│   │   ├── mosquitto.py         # Config parser
│   │   ├── docker_manager.py    # Docker control
│   │   └── log_parser.py        # Log parsing
│   ├── tui/                # Terminal UI (Textual)
│   │   ├── __init__.py
│   │   └── pages/          # TUI pages
│   ├── web/                # Web Dashboard (Flask)
│   │   ├── __init__.py
│   │   ├── templates/
│   │   └── static/
│   └── cli.py              # CLI interface (Click)
├── examples/               # ESP32 templates
│   ├── basic/              # Basic sensor
│   ├── dht22/              # DHT22 sensor
│   ├── bmp280/             # BMP280 sensor
│   └── advanced/           # With OTA updates
├── docs/                   # Documentation
├── tests/                  # Unit tests
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Full stack
├── requirements.txt        # Dependencies
└── pyproject.toml          # Package config
```

## 🛠️ Prerequisites

- Python 3.8+
- Docker (for Mosquitto)
- SSH access to VPS

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Configuration Reference](docs/CONFIGURATION.md)
- [CLI Reference](docs/CLI_REFERENCE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Changelog](docs/CHANGELOG.md)

## 🔐 Security

- Passwords stored in hashed format
- ACL-based topic access control
- Configurable web dashboard authentication
- No hardcoded secrets

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Mosquitto](https://mosquitto.org/) - MQTT Broker
- [Textual](https://textual.textualize.io/) - TUI Framework
- [Flask](https://flask.palletsprojects.com/) - Web Framework
- [Click](https://click.palletsprojects.com/) - CLI Framework

---

**Made with ❤️ for IoT community** | **[GitHub](https://github.com/thefulan123/nyamuk-mqtt)** | **Issues & Feedback**
