"""Web Dashboard for Nyamuk MQTT Manager - v2.0."""

import json
import os
from datetime import datetime
from functools import wraps
from typing import Optional

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit

from nyamuk.core.acl_manager import ACLManager
from nyamuk.core.broker_manager import BrokerManager
from nyamuk.core.log_parser import LogParser
from nyamuk.core.mqtt_client import MQTTTestClient
from nyamuk.core.provisioning import ESP32Provisioning
from nyamuk.core.user_manager import UserManager


def create_app(config: Optional[dict] = None) -> tuple:
    """Create and configure Flask application."""
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Load config
    if config is None:
        config = {
            "secret_key": os.getenv("WEB_SECRET_KEY", "change-me-in-production"),
            "admin_user": os.getenv("WEB_ADMIN_USER", "admin"),
            "admin_pass": os.getenv("WEB_ADMIN_PASS", "nyamuk123"),
        }

    app.secret_key = config["secret_key"]
    app.config["ADMIN_USER"] = config["admin_user"]
    app.config["ADMIN_PASS"] = config["admin_pass"]

    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    # Initialize managers
    broker_manager = BrokerManager()
    user_manager = UserManager()
    acl_manager = ACLManager()
    log_parser = LogParser()
    test_client: Optional[MQTTTestClient] = None

    def login_required(f):
        """Login required decorator."""

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("logged_in"):
                return redirect(url_for("login"))
            return f(*args, **kwargs)

        return decorated_function

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Login page."""
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if username == app.config["ADMIN_USER"] and password == app.config["ADMIN_PASS"]:
                session["logged_in"] = True
                return redirect(url_for("dashboard"))
            return render_template("login.html", error="Invalid credentials")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        """Logout."""
        session.clear()
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def dashboard():
        """Main dashboard page."""
        return render_template("dashboard.html")

    @app.route("/users")
    @login_required
    def users_page():
        """Users management page."""
        return render_template("users.html")

    @app.route("/config")
    @login_required
    def config_page():
        """Configuration page."""
        return render_template("config.html")

    @app.route("/api/broker/start", methods=["POST"])
    @login_required
    def api_broker_start():
        """Start the broker."""
        success, message = broker_manager.start_broker()
        return jsonify({"success": success, "message": message})

    @app.route("/api/broker/stop", methods=["POST"])
    @login_required
    def api_broker_stop():
        """Stop the broker."""
        success, message = broker_manager.stop_broker()
        return jsonify({"success": success, "message": message})

    @app.route("/api/broker/restart", methods=["POST"])
    @login_required
    def api_broker_restart():
        """Restart the broker."""
        success, message = broker_manager.restart_broker()
        return jsonify({"success": success, "message": message})

    @app.route("/api/status")
    @login_required
    def api_status():
        """Get broker status."""
        status = broker_manager.get_status()
        conn_info = broker_manager.get_connection_info()
        return jsonify({"status": status, "connection": conn_info})

    @app.route("/api/esp32")
    @login_required
    def api_esp32():
        """Get ESP32 config snippet."""
        conn_info = broker_manager.get_connection_info()
        if not conn_info:
            return jsonify({"error": "No broker configured"}), 404

        ip = conn_info["broker"].split(":")[0]
        provisioning = ESP32Provisioning(ip, int(conn_info["port"]))
        snippet = provisioning.generate_arduino_snippet(
            device_id="esp32_001", username=conn_info["username"], password=conn_info["password"]
        )
        return jsonify({"snippet": snippet})

    @app.route("/api/users", methods=["GET"])
    @login_required
    def api_get_users():
        """Get all MQTT users."""
        users = user_manager.list_users()
        return jsonify({"users": users})

    @app.route("/api/users", methods=["POST"])
    @login_required
    def api_add_user():
        """Add a new MQTT user."""
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        success, message = user_manager.add_user(username, password)
        return jsonify({"success": success, "message": message})

    @app.route("/api/users/<username>", methods=["DELETE"])
    @login_required
    def api_delete_user(username):
        """Delete an MQTT user."""
        success, message = user_manager.delete_user(username)
        return jsonify({"success": success, "message": message})

    @app.route("/api/acl", methods=["GET"])
    @login_required
    def api_get_acl():
        """Get ACL rules."""
        rules = acl_manager.read_rules()
        return jsonify({"rules": [r.to_dict() for r in rules]})

    @app.route("/api/acl", methods=["POST"])
    @login_required
    def api_add_acl():
        """Add ACL rule."""
        data = request.get_json()
        username = data.get("username")
        topic = data.get("topic")
        access = data.get("access", "readwrite")
        success, message = acl_manager.add_rule(username, topic, access)
        return jsonify({"success": success, "message": message})

    @app.route("/api/logs")
    @login_required
    def api_get_logs():
        """Get recent logs."""
        logs = log_parser.read_logs(tail=100)
        return jsonify({"logs": [log.to_dict() for log in logs]})

    @app.route("/api/health")
    def api_health():
        """Health check endpoint."""
        return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

    @app.route("/tester")
    @login_required
    def tester_page():
        """MQTT tester page."""
        return render_template("tester.html")

    def _get_test_client():
        """Get or create test client."""
        nonlocal test_client
        if test_client is None or not test_client.is_connected:
            conn_info = broker_manager.get_connection_info()
            if not conn_info:
                return None
            host = conn_info.get("broker", "localhost").split(":")[0]
            port = int(conn_info.get("port", 1883))
            username = conn_info.get("username", "")
            password = conn_info.get("password", "")
            client = MQTTTestClient(
                broker=host,
                port=port,
                username=username,
                password=password,
                client_id="nyamuk_web_tester",
            )
            if not client.connect():
                return None
            client.on_message(lambda msg: socketio.emit("tester_message", msg))
            test_client = client
        return test_client

    @app.route("/api/tester/connect", methods=["POST"])
    @login_required
    def api_tester_connect():
        """Connect test client."""
        nonlocal test_client
        client = _get_test_client()
        if client:
            socketio.emit("tester_status", {"connected": True})
            return jsonify({"success": True, "message": "Connected to broker"})
        return jsonify({"success": False, "message": "Failed to connect"})

    @app.route("/api/tester/disconnect", methods=["POST"])
    @login_required
    def api_tester_disconnect():
        """Disconnect test client."""
        nonlocal test_client
        if test_client:
            test_client.disconnect()
            test_client = None
        socketio.emit("tester_status", {"connected": False})
        return jsonify({"success": True, "message": "Disconnected"})

    @app.route("/api/tester/publish", methods=["POST"])
    @login_required
    def api_tester_publish():
        """Publish a test message."""
        client = _get_test_client()
        if not client:
            return jsonify({"success": False, "message": "Not connected"})

        data = request.get_json()
        topic = data.get("topic", "").strip()
        if not topic:
            return jsonify({"success": False, "message": "Topic is required"})

        payload = data.get("payload", "")
        data_type = data.get("data_type", "string")
        qos = int(data.get("qos", 0))

        if data_type == "json":
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                return jsonify({"success": False, "message": "Invalid JSON"})
        elif data_type == "number":
            try:
                payload = float(payload) if "." in str(payload) else int(payload)
            except ValueError:
                return jsonify({"success": False, "message": "Invalid number"})

        success = client.publish(topic, payload, qos=qos)
        return jsonify(
            {
                "success": success,
                "message": "Published" if success else "Publish failed",
            }
        )

    @app.route("/api/tester/subscribe", methods=["POST"])
    @login_required
    def api_tester_subscribe():
        """Subscribe to a topic."""
        client = _get_test_client()
        if not client:
            return jsonify({"success": False, "message": "Not connected"})

        data = request.get_json()
        topic = data.get("topic", "#").strip()
        success = client.subscribe(topic)
        return jsonify(
            {
                "success": success,
                "message": f"Subscribed to {topic}" if success else "Subscribe failed",
            }
        )

    @app.route("/api/tester/clear", methods=["POST"])
    @login_required
    def api_tester_clear():
        """Clear received messages."""
        if test_client:
            test_client.clear_messages()
        return jsonify({"success": True})

    # SocketIO events
    @socketio.on("connect")
    def handle_connect():
        """Handle client connection."""
        emit("connected", {"status": "connected"})

    @socketio.on("request_status")
    def handle_status_request():
        """Handle status request."""
        status = broker_manager.get_status()
        conn_info = broker_manager.get_connection_info()
        emit("status_update", {"status": status, "connection": conn_info})

    return app, socketio


def main():
    """Run the web dashboard."""
    app, socketio = create_app()
    port = int(os.getenv("WEB_PORT", 8080))
    host = os.getenv("WEB_HOST", "0.0.0.0")
    debug = os.getenv("NYAMUK_DEBUG", "false").lower() == "true"

    print(f"Nyamuk Web Dashboard starting on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
