"""Context manager for channel switching."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from .config import (
    load_global_config, save_global_config, 
    load_channels_registry, load_channel_config,
    get_channel_path, ChannelConfig, GlobalConfig, CHANNELS_DIR
)

@dataclass
class ChannelContext:
    """Represents the active channel context."""
    name: str
    path: Path
    config: ChannelConfig
    global_config: GlobalConfig
    
    @property
    def analytics_path(self) -> Path:
        return self.path / "analytics"
    
    @property
    def production_path(self) -> Path:
        return self.path / "production"
    
    @property
    def strategy_path(self) -> Path:
        return self.path / "strategy"

    @property
    def strategies_path(self) -> Path:
        """Legacy path (plural) used for Scoreboard."""
        return self.path / "strategies"
    
    @property
    def token_path(self) -> Path:
        return self.analytics_path / "token.pickle"
    
    @property
    def secrets_path(self) -> Path:
        # Check central credentials first (shared across all channels)
        from .config import CONTENTOS_DIR
        central_secrets = CONTENTOS_DIR / "credentials" / "client_secrets.json"
        if central_secrets.exists():
            return central_secrets
        # Fallback to channel-specific location
        return self.analytics_path / "client_secrets.json"

class ContextManager:
    """Manages channel context switching."""
    
    def __init__(self):
        self._global_config: Optional[GlobalConfig] = None
        self._current_context: Optional[ChannelContext] = None
    
    @property
    def global_config(self) -> GlobalConfig:
        if self._global_config is None:
            self._global_config = load_global_config()
        return self._global_config
    
    def get_active_channel_name(self) -> str:
        return self.global_config.active_channel
    
    def get_current_context(self) -> Optional[ChannelContext]:
        """Gets the current active channel context."""
        if self._current_context is not None:
            return self._current_context
        
        channel_name = self.get_active_channel_name()
        return self.get_context(channel_name)
    
    def get_context(self, channel_name: str) -> Optional[ChannelContext]:
        """Gets context for a specific channel."""
        channel_path = get_channel_path(channel_name)
        if not channel_path.exists():
            return None
        
        config = load_channel_config(channel_name)
        if config is None:
            # Create default config
            config = ChannelConfig(name=channel_name)
        
        return ChannelContext(
            name=channel_name,
            path=channel_path,
            config=config,
            global_config=self.global_config
        )
    
    def use_channel(self, channel_name: str) -> bool:
        """Switches to a different channel."""
        channel_path = get_channel_path(channel_name)
        if not channel_path.exists():
            return False
        
        self._global_config = load_global_config()
        self._global_config.active_channel = channel_name
        save_global_config(self._global_config)
        
        self._current_context = None  # Reset cached context
        return True
    
    def list_channels(self) -> list:
        """Lists all available channels."""
        channels = []
        if not CHANNELS_DIR.exists():
            return channels
        
        for item in CHANNELS_DIR.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                config = load_channel_config(item.name)
                channels.append({
                    'name': item.name,
                    'display_name': config.name if config else item.name,
                    'handle': config.handle if config else '',
                    'is_active': item.name == self.get_active_channel_name()
                })
        
        return channels

# Global instance
context_manager = ContextManager()
