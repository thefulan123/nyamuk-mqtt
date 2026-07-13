"""Web Dashboard for Nyamuk MQTT Manager."""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import os
from functools import wraps
from datetime import datetime

from nyamuk.core.docker_manager import DockerManager
from nyamuk.core.mosquitto import MosquittoManager
from nyamuk.core.user_manager import UserManager
from nyamuk.core.acl_manager import ACLManager
from nyamuk.core.log_parser import LogParser


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
    docker_manager = DockerManager()
    mosquitto_manager = MosquittoManager()
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

    @app.route("/config")
    @login_required
    def config():
        """Configuration page."""
        return render_template("config.html")

    @app.route("/api/status")
    @login_required
    def api_status():
        """Get broker status."""
        status = docker_manager.get_status()
        stats = docker_manager.get_stats()
        return jsonify({"status": status, "stats": stats})

    @app.route("/api/config", methods=["GET"])
    @login_required
    def api_get_config():
        """Get Mosquitto configuration."""
        config = mosquitto_manager.read()
        return jsonify(config)

    @app.route("/api/config", methods=["POST"])
    @login_required
    def api_set_config():
        """Set Mosquitto configuration."""
        data = request.get_json()
        if mosquitto_manager.write(data):
            return jsonify({"success": True, "message": "Configuration saved"})
        return jsonify({"success": False, "message": "Failed to save configuration"}), 500

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
        return jsonify({"logs": [l.to_dict() for l in logs]})

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
        status = docker_manager.get_status()
        stats = docker_manager.get_stats()
        emit("status_update", {"status": status, "stats": stats})

    return app, socketio


def main():
    """Run the web dashboard."""
    app, socketio = create_app()
    port = int(os.getenv("WEB_PORT", 8080))
    host = os.getenv("WEB_HOST", "0.0.0.0")
    debug = os.getenv("NYAMUK_DEBUG", "false").lower() == "true"

    print(f"🦟 Nyamuk Web Dashboard starting on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
