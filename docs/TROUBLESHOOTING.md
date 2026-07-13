# Troubleshooting

## Common Issues

### Docker Issues

**Problem:** Cannot connect to Docker daemon

```
Error: Cannot connect to Docker daemon. Is Docker running?
```

**Solution:**
```bash
# Start Docker
sudo systemctl start docker

# Or add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**Problem:** Container not found

```
Error: Container 'mosquitto' not found
```

**Solution:**
```bash
# Pull and create container
docker pull eclipse-mosquitto:2
docker-compose up -d
```

### MQTT Connection Issues

**Problem:** Connection refused

```
Error: Connection refused
```

**Solution:**
1. Check if Mosquitto is running: `nyamuk status`
2. Check port: `nyamuk config show`
3. Check authentication settings

**Problem:** Anonymous access denied

```
Error: Authentication required
```

**Solution:**
```bash
# Enable anonymous access temporarily
nyamuk config set allow_anonymous true
nyamuk restart

# Or create user
nyamuk user add myuser
```

### Permission Issues

**Problem:** Cannot read/write config file

```
Error: Permission denied
```

**Solution:**
```bash
# Fix permissions
sudo chown -R $USER:$USER /opt/mosquitto
sudo chmod -R 755 /opt/mosquitto
```

### Web Dashboard Issues

**Problem:** Cannot access web dashboard

```
ERR_CONNECTION_REFUSED
```

**Solution:**
1. Check if web server is running
2. Check firewall: `sudo ufw allow 8080`
3. Check port binding: `nyamuk web --port 8080`

**Problem:** Login fails

```
Invalid credentials
```

**Solution:**
1. Check `.env` file credentials
2. Default: `admin` / `nyamuk123`
3. Restart application after changing

### TUI Issues

**Problem:** TUI display corrupted

**Solution:**
```bash
# Reset terminal
reset

# Or use different terminal
TERM=xterm-256color nyamuk tui
```

## Logs

### View Application Logs

```bash
# Docker logs
docker logs mosquitto

# Nyamuk logs
nyamuk logs --tail 50
```

### Debug Mode

```bash
# Enable debug logging
nyamuk web --debug

# Or set environment variable
export NYAMUK_DEBUG=true
nyamuk web
```

## Getting Help

1. Check this troubleshooting guide
2. Run `nyamuk --help`
3. Check GitHub Issues: https://github.com/thefulan123/nyamuk-mqtt/issues
4. Create new issue with:
   - Error message
   - Steps to reproduce
   - Operating system
   - Python version
   - Nyamuk version
