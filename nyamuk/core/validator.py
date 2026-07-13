"""Configuration validation using Pydantic."""

from typing import Optional

from pydantic import BaseModel, Field, validator


class MosquittoConfig(BaseModel):
    """Mosquitto configuration schema with validation."""

    listener: int = Field(default=1883, ge=1, le=65535, description="MQTT listener port")
    allow_anonymous: bool = Field(default=True, description="Allow anonymous connections")
    persistence: bool = Field(default=True, description="Enable message persistence")
    persistence_location: str = Field(
        default="/mosquitto/data/", description="Persistence directory"
    )
    log_dest: str = Field(
        default="file /mosquitto/log/mosquitto.log", description="Log destination"
    )
    log_type: str = Field(default="all", description="Log types to capture")
    max_connections: int = Field(default=-1, ge=-1, description="Max connections (-1 = unlimited)")
    max_inflight_messages: int = Field(default=20, description="Max inflight messages")
    max_queued_messages: int = Field(default=1000, ge=0, description="Max queued messages")
    message_size_limit: int = Field(default=0, ge=0, description="Max message size (0 = unlimited)")

    # TLS settings
    cafile: Optional[str] = Field(default=None, description="CA certificate file")
    certfile: Optional[str] = Field(default=None, description="Server certificate file")
    keyfile: Optional[str] = Field(default=None, description="Server key file")

    # ACL settings
    acl_file: Optional[str] = Field(default=None, description="ACL file path")
    password_file: Optional[str] = Field(default=None, description="Password file path")

    @validator("listener")
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1-65535")
        return v

    @validator("allow_anonymous")
    @classmethod
    def validate_auth(cls, v):
        if v:
            import warnings

            warnings.warn(
                "Warning: Anonymous access enabled. Consider disabling for production.",
                stacklevel=2,
            )
        return v

    @validator("max_inflight_messages")
    @classmethod
    def validate_inflight(cls, v):
        if v < 0 and v != -1:
            raise ValueError("Max inflight messages must be >= 0 or -1 for unlimited")
        return v

    @validator("message_size_limit")
    @classmethod
    def validate_message_size(cls, v):
        if v < 0:
            raise ValueError("Message size limit must be >= 0")
        return v


class NyamukConfig(BaseModel):
    """Nyamuk application configuration."""

    mqtt_broker: str = Field(default="localhost", description="MQTT broker host")
    mqtt_port: int = Field(default=1883, ge=1, le=65535, description="MQTT broker port")
    mqtt_username: Optional[str] = Field(default=None, description="MQTT username")
    mqtt_password: Optional[str] = Field(default=None, description="MQTT password")
    topic_prefix: str = Field(default="nyamuk", description="Default topic prefix")

    web_host: str = Field(default="0.0.0.0", description="Web dashboard host")
    web_port: int = Field(default=8080, ge=1, le=65535, description="Web dashboard port")
    web_secret_key: str = Field(default="change-me-in-production", description="Flask secret key")
    web_admin_user: str = Field(default="admin", description="Web dashboard admin username")
    web_admin_pass: str = Field(default="nyamuk123", description="Web dashboard admin password")

    docker_container_name: str = Field(default="mosquitto", description="Docker container name")
    docker_image: str = Field(default="eclipse-mosquitto:2", description="Docker image name")

    log_level: str = Field(default="INFO", description="Application log level")
    auto_refresh_interval: int = Field(
        default=5, ge=1, description="Auto-refresh interval in seconds"
    )

    @validator("web_port", "mqtt_port")
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1-65535")
        return v

    @validator("topic_prefix")
    @classmethod
    def validate_topic_prefix(cls, v):
        if not v or "/" in v:
            raise ValueError("Topic prefix cannot be empty or contain '/'")
        return v
