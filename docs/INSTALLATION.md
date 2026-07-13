# Installation Guide

## Prerequisites

- Python 3.8+
- Docker (for Mosquitto broker)
- pip or poetry

## Installation Methods

### Method 1: pip (Recommended)

```bash
# Install from source
git clone https://github.com/thefulan123/nyamuk-mqtt.git
cd nyamuk-mqtt
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

### Method 2: Docker

```bash
# Build Docker image
docker build -t nyamuk:latest .

# Run with docker-compose
docker-compose up -d
```

### Method 3: Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Verification

```bash
# Check installation
nyamuk --version

# Test TUI
nyamuk tui

# Test Web Dashboard
nyamuk web --port 8080
```

## Next Steps

1. [Configuration](CONFIGURATION.md) - Configure Nyamuk
2. [CLI Reference](CLI_REFERENCE.md) - Learn CLI commands
3. [ESP32 Setup](../examples/) - Connect your devices
