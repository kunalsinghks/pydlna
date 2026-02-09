import logging
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import uuid
import socket
import json
import argparse
import sys

logger = logging.getLogger(__name__)

class ServerInstanceConfig(BaseSettings):
    """Configuration for a single server instance"""
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    port: int = 8200
    host: str = "0.0.0.0"
    app_name: str = "PyDLNA Server"
    friendly_name: str = "PyDLNA Media Server"
    media_paths: list[Path] = [Path("./media")]
    database_url: str = Field(default_factory=lambda: f"sqlite+aiosqlite:///./pydlna_{uuid.uuid4()}.db")
    interface_ip: str | None = None
    pid: int | None = None  # To track process ID
    username: str = "admin" # Default username
    password: str | None = None # Server access password
    pwa_mode: bool = False # Native app mode flag
    
    model_config = SettingsConfigDict(env_prefix='PYDLNA_', extra='ignore')

    @property
    def base_url(self) -> str:
        ip = self.interface_ip or self._get_local_ip()
        return f"http://{ip}:{self.port}"

    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def save(self, path: Path):
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: Path) -> "ServerInstanceConfig":
        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
            # Handle Path serialization
            if "media_paths" in data:
                data["media_paths"] = [Path(p) for p in data["media_paths"]]
            return cls(**data)
        return cls()

# Global settings object
# Load Settings
try:
    if Path("config.json").exists():
        with open("config.json", "r") as f:
            data = json.load(f)
            # Handle legacy config
            if "media_paths" in data:
                data["media_paths"] = [Path(p) for p in data["media_paths"]]
            settings = ServerInstanceConfig(**data)
    else:
        settings = ServerInstanceConfig()
except Exception as e:
    print(f"Config load error: {e}")
    settings = ServerInstanceConfig()

def save_config(conf: ServerInstanceConfig = None):
    """Save current settings to disk"""
    global settings
    if conf:
        settings = conf
    
    with open("config.json", "w") as f:
        # Pydantic v2 dump
        f.write(settings.model_dump_json(indent=2))

def update_media_paths(paths: list[str]):
    global settings
    settings.media_paths = [Path(p) for p in paths]
    print(f"Saving media paths to config.json: {settings.media_paths}")
    save_config()

def update_settings(updates: dict):
    global settings
    for key, value in updates.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    save_config()

def load_settings(config_file: str = "config.json"):
    # This function is largely superseded by the global settings loading logic.
    # It can be kept for compatibility or removed if not needed elsewhere.
    # For now, it will just ensure the global settings object is consistent.
    global settings
    path = Path(config_file)
    if path.exists():
        new_settings = ServerInstanceConfig.load(path)
        # Update existing object in-place so references remain valid
        for key, value in new_settings.model_dump().items():
            setattr(settings, key, value)
    else:
        # Save default if not exists
        settings.save(path)
