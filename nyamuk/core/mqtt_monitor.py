"""Real-time MQTT monitoring using paho-mqtt."""

import json
import threading
import time
from typing import Callable, Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


class MQTTMonitor:
    """Monitor MQTT broker in real-time."""

    def __init__(self, broker: str = "localhost", port: int = 1883,
                 username: Optional[str] = None, password: Optional[str] = None):
        if mqtt is None:
            raise ImportError("paho-mqtt is required. Install with: pip install paho-mqtt")

        self.broker = broker
        self.port = port
        self.username = username
        self.password = password

        self._client = None
        self._connected = False
        self._messages: List[Dict[str, Any]] = []
        self._topic_stats: Dict[str, int] = defaultdict(int)
        self._callbacks: List[Callable] = []
        self._lock = threading.Lock()
        self._max_messages = 1000

    def _get_client(self):
        """Get or create MQTT client."""
        if self._client is None:
            self._client = mqtt.Client(
                client_id="nyamuk_monitor",
                protocol=mqtt.MQTTv311,
            )
            if self.username:
                self._client.username_pw_set(self.username, self.password)
            self._client.on_connect = self._on_connect
            self._client.on_message = self._on_message
            self._client.on_disconnect = self._on_disconnect
        return self._client

    def _on_connect(self, client, userdata, flags, rc):
        """Handle connection."""
        self._connected = rc == 0
        if self._connected:
            # Subscribe to all topics for monitoring
            client.subscribe("$SYS/#")  # Broker stats
            client.subscribe("#")  # All topics

    def _on_message(self, client, userdata, msg):
        """Handle incoming message."""
        with self._lock:
            try:
                payload = msg.payload.decode("utf-8")
            except UnicodeDecodeError:
                payload = f"<binary: {len(msg.payload)} bytes>"

            message = {
                "topic": msg.topic,
                "payload": payload,
                "qos": msg.qos,
                "retain": msg.retain,
                "timestamp": datetime.now().isoformat(),
            }

            self._messages.append(message)
            if len(self._messages) > self._max_messages:
                self._messages = self._messages[-self._max_messages:]

            self._topic_stats[msg.topic] += 1

            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(message)
                except Exception:
                    pass

    def _on_disconnect(self, client, userdata, rc):
        """Handle disconnection."""
        self._connected = False

    def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            client = self._get_client()
            client.connect(self.broker, self.port, 60)
            client.loop_start()
            time.sleep(0.1)
            return self._connected
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._connected = False

    def is_connected(self) -> bool:
        """Check if connected to broker."""
        return self._connected

    def get_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent messages."""
        with self._lock:
            return list(self._messages[-limit:])

    def get_topic_stats(self) -> Dict[str, int]:
        """Get message count per topic."""
        with self._lock:
            return dict(self._topic_stats)

    def get_message_rate(self, window: int = 60) -> float:
        """Get messages per second over a time window."""
        with self._lock:
            now = datetime.now()
            recent = [
                m for m in self._messages
                if (now - datetime.fromisoformat(m["timestamp"])).seconds <= window
            ]
            return len(recent) / window if window > 0 else 0

    def on_message(self, callback: Callable):
        """Register message callback."""
        self._callbacks.append(callback)

    def clear_messages(self):
        """Clear message buffer."""
        with self._lock:
            self._messages.clear()
            self._topic_stats.clear()

    def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> bool:
        """Publish a message."""
        if not self._connected:
            return False
        try:
            result = self._client.publish(topic, payload, qos=qos, retain=retain)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception:
            return False

    def subscribe(self, topic: str, qos: int = 0) -> bool:
        """Subscribe to a topic."""
        if not self._connected:
            return False
        try:
            result = self._client.subscribe(topic, qos=qos)
            return result[0] == mqtt.MQTT_ERR_SUCCESS
        except Exception:
            return False

    def get_broker_stats(self) -> Dict[str, Any]:
        """Get broker statistics from $SYS topics."""
        stats = {}
        with self._lock:
            for msg in self._messages:
                if msg["topic"].startswith("$SYS/"):
                    stats[msg["topic"]] = msg["payload"]
        return stats
