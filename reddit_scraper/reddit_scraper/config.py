import os
import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration management for Reddit Scraper"""
    
    def __init__(self):
        # Setup home directory paths
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / '.config' / 'reddit_scraper'
        self.data_dir = self.home_dir / 'reddit_scraper'
        self.log_dir = self.data_dir / 'logs'
        self.output_dir = self.data_dir / 'output'
        
        # Create necessary directories
        self._create_directories()
        
        # Load or create config
        self.config_file = self.config_dir / 'config.yaml'
        self.config = self._load_config()
    
    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        directories = [
            self.config_dir,
            self.data_dir,
            self.log_dir,
            self.output_dir
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file or create default"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create and save default configuration"""
        default_config = {
            'output': {
                'directory': str(self.output_dir),
                'format': 'markdown',
                'organize_by_date': True
            },
            'logging': {
                'directory': str(self.log_dir),
                'level': 'INFO',
                'max_size': '10MB',
                'backup_count': 5
            },
            'reddit': {
                'rate_limit': {
                    'requests_per_minute': 30,
                    'burst_limit': 100
                },
                'default_subreddit': 'python'
            },
            'markdown': {
                'include_metadata': True,
                'include_scores': True,
                'include_timestamps': True,
                'max_comment_depth': -1  # -1 for unlimited
            }
        }
        
        # Save default config
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(default_config, f, default_flow_style=False)
        
        return default_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save to file"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)
    
    def get_output_dir(self) -> Path:
        """Get the output directory path, creating it if necessary"""
        output_dir = Path(self.get('output.directory', str(self.output_dir)))
        if self.get('output.organize_by_date', True):
            from datetime import datetime
            output_dir = output_dir / datetime.now().strftime('%Y-%m-%d')
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def get_log_dir(self) -> Path:
        """Get the log directory path, creating it if necessary"""
        log_dir = Path(self.get('logging.directory', str(self.log_dir)))
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

# Global config instance
config = Config()