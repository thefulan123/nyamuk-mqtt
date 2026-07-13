"""CLI interface for Nyamuk MQTT Manager - v2.0."""

import click
import json
import sys
from pathlib import Path
from typing import Optional


@click.group()
@click.version_option(version="2.0.0", prog_name="nyamuk")
def main():
    """Nyamuk - MQTT Broker Factory

    Create your MQTT broker in 30 seconds - zero coding required.
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

    click.echo(f"Nyamuk Web Dashboard starting on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


@main.command()
def create():
    """Create a new MQTT broker"""
    from nyamuk.core.broker_manager import BrokerManager
    from nyamuk.core.port_scanner import PortScanner

    manager = BrokerManager()
    scanner = PortScanner()

    # Check if broker already exists
    if manager.get_broker_config():
        click.echo("[ERROR] Broker already exists. Delete it first with: nyamuk delete")
        sys.exit(1)

    # Get broker name
    name = click.prompt("Broker name", default="my_broker")

    # Auto-detect port
    suggested_port = scanner.suggest_port()
    port = click.prompt("Port", default=suggested_port, type=int)

    # Check port
    if not scanner.is_port_free(port):
        click.echo(f"[ERROR] Port {port} is already in use")
        sys.exit(1)

    # Get password
    password = click.prompt("Password (leave empty for auto-generate)", default="", hide_input=True)

    # Create broker
    success, message = manager.create_broker(
        name=name,
        port=port,
        password=password if password else None,
    )

    if success:
        click.echo(f"[OK] {message}")
        click.echo("\nNext steps:")
        click.echo(f"  1. Start broker: nyamuk start")
        click.echo(f"  2. View connection info: nyamuk status")
    else:
        click.echo(f"[ERROR] {message}")
        sys.exit(1)


@main.command()
def start():
    """Start the MQTT broker"""
    from nyamuk.core.broker_manager import BrokerManager
    manager = BrokerManager()

    success, message = manager.start_broker()
    if success:
        click.echo(f"[OK] {message}")
    else:
        click.echo(f"[ERROR] {message}")
        sys.exit(1)


@main.command()
def stop():
    """Stop the MQTT broker"""
    from nyamuk.core.broker_manager import BrokerManager
    manager = BrokerManager()

    success, message = manager.stop_broker()
    if success:
        click.echo(f"[OK] {message}")
    else:
        click.echo(f"[ERROR] {message}")
        sys.exit(1)


@main.command()
def restart():
    """Restart the MQTT broker"""
    from nyamuk.core.broker_manager import BrokerManager
    manager = BrokerManager()

    success, message = manager.restart_broker()
    if success:
        click.echo(f"[OK] {message}")
    else:
        click.echo(f"[ERROR] {message}")
        sys.exit(1)


@main.command()
@click.confirmation_option(prompt="Are you sure you want to delete the broker?")
def delete():
    """Delete the MQTT broker"""
    from nyamuk.core.broker_manager import BrokerManager
    manager = BrokerManager()

    success, message = manager.delete_broker()
    if success:
        click.echo(f"[OK] {message}")
    else:
        click.echo(f"[ERROR] {message}")
        sys.exit(1)


@main.command()
def status():
    """Show broker status and connection info"""
    from nyamuk.core.broker_manager import BrokerManager
    manager = BrokerManager()

    config = manager.get_broker_config()
    if not config:
        click.echo("[WARNING] No broker configured. Run: nyamuk create")
        return

    status = manager.get_status()
    conn_info = manager.get_connection_info()

    click.echo("Nyamuk MQTT Broker Status:")
    click.echo(f"  Name: {status['name']}")
    click.echo(f"  Status: {'Running' if status['status'] == 'running' else 'Stopped'}")
    click.echo(f"  Port: {status['port']}")
    click.echo(f"  Created: {status['created_at'][:19]}")

    click.echo("\nConnection Info:")
    click.echo(f"  Broker: {conn_info['broker']}")
    click.echo(f"  Username: {conn_info['username']}")
    click.echo(f"  Password: {conn_info['password']}")
    click.echo(f"  Topic: {conn_info['topic_prefix']}/#")


@main.command()
def esp32():
    """Generate ESP32 configuration snippet"""
    from nyamuk.core.broker_manager import BrokerManager
    from nyamuk.core.provisioning import ESP32Provisioning

    manager = BrokerManager()
    config = manager.get_broker_config()

    if not config:
        click.echo("[WARNING] No broker configured. Run: nyamuk create")
        return

    conn_info = manager.get_connection_info()
    ip = conn_info['broker'].split(':')[0]

    provisioning = ESP32Provisioning(ip, int(conn_info['port']))
    snippet = provisioning.generate_arduino_snippet(
        device_id="esp32_001",
        username=conn_info['username'],
        password=conn_info['password']
    )

    click.echo("// Copy this to your Arduino sketch:")
    click.echo(snippet)


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
        click.echo(f"[OK] {message}")
    else:
        click.echo(f"[ERROR] {message}", err=True)
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
        click.echo(f"[OK] {message}")
    else:
        click.echo(f"[ERROR] {message}", err=True)
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
        click.echo(f"[OK] {message}")
    else:
        click.echo(f"[ERROR] {message}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
