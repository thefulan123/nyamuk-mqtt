"""CLI interface for Nyamuk MQTT Manager."""

import click
import json
import sys
from pathlib import Path
from typing import Optional


@click.group()
@click.version_option(version="1.0.0", prog_name="nyamuk")
def main():
    """🦟 Nyamuk - Mosquitto MQTT Manager

    A lightweight MQTT broker manager with TUI & Web Dashboard.
    """
    pass


@main.command()
def tui():
    """Launch TUI Dashboard"""
    from nyamuk.tui import NyamukTUI
    app = NyamukTUI()
    app.run()


@main.command()
@click.option("--host", default="0.0.0.0", help="Web dashboard host")
@click.option("--port", default=8080, help="Web dashboard port")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def web(host: str, port: int, debug: bool):
    """Launch Web Dashboard"""
    from nyamuk.web import create_app
    app, socketio = create_app()

    import os
    os.environ["NYAMUK_DEBUG"] = "true" if debug else "false"

    click.echo(f"🦟 Nyamuk Web Dashboard starting on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


@main.group()
def config():
    """Configuration management"""
    pass


@config.command("show")
def config_show():
    """Show current configuration"""
    from nyamuk.core.mosquitto import MosquittoManager
    manager = MosquittoManager()
    cfg = manager.read()
    click.echo(json.dumps(cfg, indent=2))


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set configuration value"""
    from nyamuk.core.mosquitto import MosquittoManager
    manager = MosquittoManager()

    # Try to parse value as appropriate type
    parsed_value = value
    if value.lower() == "true":
        parsed_value = True
    elif value.lower() == "false":
        parsed_value = False
    else:
        try:
            parsed_value = int(value)
        except ValueError:
            try:
                parsed_value = float(value)
            except ValueError:
                pass

    if manager.update(key, parsed_value):
        click.echo(f"✅ Set {key} = {parsed_value}")
    else:
        click.echo(f"❌ Failed to set {key}", err=True)
        sys.exit(1)


@config.command("validate")
def config_validate():
    """Validate configuration"""
    from nyamuk.core.mosquitto import MosquittoManager
    manager = MosquittoManager()
    is_valid, errors = manager.validate()

    if is_valid:
        click.echo("✅ Configuration is valid")
    else:
        click.echo("⚠️  Configuration issues:")
        for error in errors:
            click.echo(f"  - {error}")


@main.group()
def user():
    """User management"""
    pass


@user.command("list")
def user_list():
    """List all MQTT users"""
    from nyamuk.core.user_manager import UserManager
    manager = UserManager()
    users = manager.list_users()

    if users:
        click.echo("MQTT Users:")
        for u in users:
            click.echo(f"  - {u}")
    else:
        click.echo("No users found")


@user.command("add")
@click.argument("username")
@click.password_option()
def user_add(username: str, password: str):
    """Add a new MQTT user"""
    from nyamuk.core.user_manager import UserManager
    manager = UserManager()

    success, message = manager.add_user(username, password)
    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@user.command("delete")
@click.argument("username")
@click.confirmation_option(prompt="Are you sure you want to delete this user?")
def user_delete(username: str):
    """Delete an MQTT user"""
    from nyamuk.core.user_manager import UserManager
    manager = UserManager()

    success, message = manager.delete_user(username)
    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@user.command("password")
@click.argument("username")
@click.password_option()
def user_password(username: str, password: str):
    """Change user password"""
    from nyamuk.core.user_manager import UserManager
    manager = UserManager()

    success, message = manager.change_password(username, password)
    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@main.group()
def acl():
    """ACL management"""
    pass


@acl.command("list")
def acl_list():
    """List ACL rules"""
    from nyamuk.core.acl_manager import ACLManager
    manager = ACLManager()
    rules = manager.read_rules()

    if rules:
        click.echo("ACL Rules:")
        for rule in rules:
            click.echo(f"  {rule.username} -> {rule.topic} ({rule.access})")
    else:
        click.echo("No ACL rules found")


@acl.command("add")
@click.argument("username")
@click.argument("topic")
@click.option("--access", type=click.Choice(["read", "write", "readwrite"]), default="readwrite")
def acl_add(username: str, topic: str, access: str):
    """Add ACL rule"""
    from nyamuk.core.acl_manager import ACLManager
    manager = ACLManager()

    success, message = manager.add_rule(username, topic, access)
    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@acl.command("delete")
@click.argument("username")
@click.argument("topic")
def acl_delete(username: str, topic: str):
    """Delete ACL rule"""
    from nyamuk.core.acl_manager import ACLManager
    manager = ACLManager()

    success, message = manager.delete_rule(username, topic)
    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@main.command()
def status():
    """Show broker status"""
    from nyamuk.core.docker_manager import DockerManager
    manager = DockerManager()

    status = manager.get_status()
    stats = manager.get_stats()

    click.echo("🦟 Mosquitto Broker Status:")
    click.echo(f"  Status: {status.get('status', 'unknown')}")
    click.echo(f"  Image: {status.get('image', 'unknown')}")

    if "error" not in stats:
        click.echo(f"  CPU: {stats.get('cpu_percent', 0)}%")
        click.echo(f"  Memory: {stats.get('memory_percent', 0)}%")


@main.command()
@click.option("--tail", default=100, help="Number of log lines to show")
def logs(tail: int):
    """View broker logs"""
    from nyamuk.core.docker_manager import DockerManager
    manager = DockerManager()

    log_output = manager.get_logs(tail=tail)
    click.echo(log_output)


@main.command()
def restart():
    """Restart broker"""
    from nyamuk.core.docker_manager import DockerManager
    manager = DockerManager()

    click.echo("Restarting Mosquitto broker...")
    if manager.restart():
        click.echo("✅ Broker restarted successfully")
    else:
        click.echo("❌ Failed to restart broker", err=True)
        sys.exit(1)


@main.command()
@click.argument("output_file", default="nyamuk_export.json")
def export(output_file: str):
    """Export configuration"""
    from nyamuk.core.mosquitto import MosquittoManager
    from nyamuk.core.user_manager import UserManager
    from nyamuk.core.acl_manager import ACLManager

    mosquitto = MosquittoManager()
    users = UserManager()
    acl = ACLManager()

    data = {
        "config": mosquitto.read(),
        "users": users.list_users(),
        "acl": [r.to_dict() for r in acl.read_rules()],
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    click.echo(f"✅ Configuration exported to {output_file}")


@main.command()
@click.argument("input_file")
def import_config(input_file: str):
    """Import configuration"""
    from nyamuk.core.mosquitto import MosquittoManager

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    mosquitto = MosquittoManager()
    if "config" in data:
        if mosquitto.write(data["config"]):
            click.echo("✅ Configuration imported successfully")
        else:
            click.echo("❌ Failed to import configuration", err=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
