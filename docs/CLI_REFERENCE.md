# CLI Reference

## Commands

### TUI Dashboard

```bash
nyamuk tui
```

Launch terminal-based dashboard with keyboard navigation.

**Keyboard Shortcuts:**
- `d` - Dashboard
- `c` - Configuration
- `u` - Users
- `a` - ACL
- `l` - Logs
- `s` - Settings
- `q` - Quit

### Web Dashboard

```bash
nyamuk web [OPTIONS]
```

**Options:**
- `--host TEXT` - Host to bind (default: 0.0.0.0)
- `--port INTEGER` - Port to use (default: 8080)
- `--debug` - Enable debug mode

**Example:**
```bash
nyamuk web --port 9090 --debug
```

### Status

```bash
nyamuk status
```

Show broker status, CPU and memory usage.

### Logs

```bash
nyamuk logs [OPTIONS]
```

**Options:**
- `--tail INTEGER` - Number of lines (default: 100)

**Example:**
```bash
nyamuk logs --tail 50
```

### Restart

```bash
nyamuk restart
```

Restart Mosquitto broker container.

## Configuration Commands

### Show Config

```bash
nyamuk config show
```

Display current Mosquitto configuration.

### Set Config

```bash
nyamuk config set KEY VALUE
```

**Examples:**
```bash
nyamuk config set listener 1883
nyamuk config set allow_anonymous false
nyamuk config set persistence true
```

### Validate Config

```bash
nyamuk config validate
```

Validate configuration file.

## User Commands

### List Users

```bash
nyamuk user list
```

### Add User

```bash
nyamuk user add USERNAME
```

Prompts for password.

### Delete User

```bash
nyamuk user delete USERNAME
```

### Change Password

```bash
nyamuk user password USERNAME
```

Prompts for new password.

## ACL Commands

### List Rules

```bash
nyamuk acl list
```

### Add Rule

```bash
nyamuk acl add USERNAME TOPIC [OPTIONS]
```

**Options:**
- `--access [read|write|readwrite]` - Access type (default: readwrite)

**Example:**
```bash
nyamuk acl add esp32 "nyamuk/esp32/#" --access readwrite
```

### Delete Rule

```bash
nyamuk acl delete USERNAME TOPIC
```

## Export/Import

### Export Configuration

```bash
nyamuk export [OUTPUT_FILE]
```

### Import Configuration

```bash
nyamuk import INPUT_FILE
```
