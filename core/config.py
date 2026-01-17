"""Configuration loading and merging for ContentOS."""
import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CONTENTOS_DIR = PROJECT_ROOT / ".contentos"
CHANNELS_DIR = PROJECT_ROOT / "channels"

@dataclass
class FeaturesConfig:
    """Toggleable system modules for distribution."""
    llm_swarm: bool = False   # Enable local/cloud LLM agents
    scout_agent: bool = True  # Enable YouTube Data API research
    cloud_sync: bool = False  # Enable remote database sync

@dataclass
class GlobalConfig:
    version: str = "1.0.0"
    active_channel: str = "rotnation"
    default_theme: str = "loop"
    auto_sync_on_publish: bool = True
    features: FeaturesConfig = field(default_factory=FeaturesConfig)

@dataclass
class ChannelConfig:
    name: str = ""
    handle: str = ""
    youtube_channel_id: str = ""
    themes: List[str] = field(default_factory=lambda: ["loop", "cinematic", "voxel"])
    production_prefix: str = "project"
    default_script_style: str = "adrenaline_hook"

def load_global_config() -> GlobalConfig:
    """Loads global config from .contentos/config.json"""
    config_path = CONTENTOS_DIR / "config.json"
    if not config_path.exists():
        return GlobalConfig()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle nested feature config manually if needed, or let dataclass handle it if straightforward
    # For safety with simple json load, we parse the sub-dict
    features_data = data.pop('features', {})
    config = GlobalConfig(**data)
    config.features = FeaturesConfig(**features_data)
    return config

def save_global_config(config: GlobalConfig) -> None:
    """Saves global config to .contentos/config.json"""
    CONTENTOS_DIR.mkdir(exist_ok=True)
    config_path = CONTENTOS_DIR / "config.json"
    
    # Convert to dict and handle nested dataclass
    data = config.__dict__.copy()
    data['features'] = config.features.__dict__
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def load_channels_registry() -> Dict[str, dict]:
    """Loads channel registry from .contentos/channels.json"""
    registry_path = CONTENTOS_DIR / "channels.json"
    if not registry_path.exists():
        return {}
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_channels_registry(registry: Dict[str, dict]) -> None:
    """Saves channel registry to .contentos/channels.json"""
    CONTENTOS_DIR.mkdir(exist_ok=True)
    registry_path = CONTENTOS_DIR / "channels.json"
    
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)

def load_channel_config(channel_name: str) -> Optional[ChannelConfig]:
    """Loads per-channel config from channels/<name>/.channel.json"""
    channel_path = CHANNELS_DIR / channel_name / ".channel.json"
    if not channel_path.exists():
        return None
    
    with open(channel_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return ChannelConfig(**data)

def save_channel_config(channel_name: str, config: ChannelConfig) -> None:
    """Saves per-channel config to channels/<name>/.channel.json"""
    channel_dir = CHANNELS_DIR / channel_name
    channel_dir.mkdir(parents=True, exist_ok=True)
    config_path = channel_dir / ".channel.json"
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config.__dict__, f, indent=2)

def get_channel_path(channel_name: str) -> Path:
    """Returns the absolute path to a channel directory."""
    return CHANNELS_DIR / channel_name
