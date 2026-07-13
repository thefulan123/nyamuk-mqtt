"""Web Dashboard for Nyamuk MQTT Manager - v2.0."""

import os
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit

from nyamuk.core.acl_manager import ACLManager
from nyamuk.core.broker_manager import BrokerManager
from nyamuk.core.log_parser import LogParser
from nyamuk.core.provisioning import ESP32Provisioning
from nyamuk.core.user_manager import UserManager


def create_app(config: dict = None) -> Flask:
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

        ip = conn_info['broker'].split(':')[0]
        provisioning = ESP32Provisioning(ip, int(conn_info['port']))
        snippet = provisioning.generate_arduino_snippet(
            device_id="esp32_001",
            username=conn_info['username'],
            password=conn_info['password']
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
