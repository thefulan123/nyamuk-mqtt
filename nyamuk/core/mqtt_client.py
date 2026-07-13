"""MQTT test client for pub/sub testing."""

import json
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None  # type: ignore[assignment]


class MQTTTestClient:
    """Lightweight MQTT client for testing pub/sub."""

    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: str = "nyamuk_tester",
    ):
        if mqtt is None:
            raise ImportError("paho-mqtt is required. Install with: pip install paho-mqtt")

        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id

        self._client: Optional[mqtt.Client] = None
        self._connected = False
        self._messages: List[Dict[str, Any]] = []
        self._callbacks: List[Callable] = []
        self._lock = threading.Lock()
        self._subscribed_topics: List[str] = []

    def connect(self) -> bool:
        """Connect to the broker."""
        try:
            self._client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
            if self.username:
                self._client.username_pw_set(self.username, self.password)
            self._client.on_connect = self._on_connect
            self._client.on_message = self._on_message
            self._client.connect(self.broker, self.port, keepalive=60)
            self._client.loop_start()
            return True
        except Exception:
            return False

    def disconnect(self) -> None:
        """Disconnect from broker."""
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._connected = False

    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False) -> bool:
        """Publish a message. Returns True on success."""
        if not self._connected or self._client is None:
            return False
        try:
            if isinstance(payload, (dict, list)):
                payload_str = json.dumps(payload)
            elif isinstance(payload, bool):
                payload_str = str(payload).lower()
            else:
                payload_str = str(payload)
            result = self._client.publish(topic, payload_str, qos=qos, retain=retain)
            rc: int = result.rc
            return rc == mqtt.MQTT_ERR_SUCCESS
        except Exception:
            return False

    def subscribe(self, topic: str, qos: int = 0) -> bool:
        """Subscribe to a topic."""
        if not self._connected or self._client is None:
            return False
        try:
            result = self._client.subscribe(topic, qos=qos)
            rc_tuple: int = result[0]
            if rc_tuple == mqtt.MQTT_ERR_SUCCESS:
                if topic not in self._subscribed_topics:
                    self._subscribed_topics.append(topic)
                return True
            return False
        except Exception:
            return False

    def unsubscribe(self, topic: str) -> bool:
        """Unsubscribe from a topic."""
        if not self._connected or self._client is None:
            return False
        try:
            self._client.unsubscribe(topic)
            if topic in self._subscribed_topics:
                self._subscribed_topics.remove(topic)
            return True
        except Exception:
            return False

    def get_messages(self, clear: bool = False) -> List[Dict[str, Any]]:
        """Get received messages."""
        with self._lock:
            msgs = list(self._messages)
            if clear:
                self._messages.clear()
            return msgs

    def clear_messages(self) -> None:
        """Clear all received messages."""
        with self._lock:
            self._messages.clear()

    def on_message(self, callback: Callable) -> None:
        """Register a callback for incoming messages."""
        self._callbacks.append(callback)

    @property
    def is_connected(self) -> bool:
        return self._connected

    def _on_connect(self, client, userdata, flags, rc) -> None:
        """Handle connection."""
        self._connected = rc == 0
        if self._connected:
            for topic in self._subscribed_topics:
                client.subscribe(topic)

    def _on_message(self, client, userdata, msg) -> None:
        """Handle incoming message."""
        try:
            payload = msg.payload.decode("utf-8")
        except UnicodeDecodeError:
            payload = f"<binary: {len(msg.payload)} bytes>"

        entry = {
            "topic": msg.topic,
            "payload": payload,
            "qos": msg.qos,
            "retain": msg.retain,
            "timestamp": datetime.now().isoformat(),
        }

        with self._lock:
            self._messages.append(entry)

        for cb in self._callbacks:
            try:
                cb(entry)
            except Exception:
                pass
