"""
Environment configuration loader for Emby development
"""
import os
from typing import Optional


def load_env_file(env_path: str = ".env") -> dict:
    """
    Load environment variables from a .env file
    Returns a dictionary of key-value pairs
    """
    env_vars = {}
    
    if not os.path.exists(env_path):
        print(f"Warning: {env_path} not found")
        return env_vars
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                    
                    # Also set as environment variable
                    os.environ[key] = value
    
    except Exception as e:
        print(f"Error loading {env_path}: {e}")
    
    return env_vars


def get_emby_config() -> dict:
    """
    Get Emby configuration from environment variables
    Load from .env file if present
    """
    # Load .env file
    load_env_file()
    
    config = {
        'url': os.getenv('EMBY_URL', 'http://localhost:8096'),
        'api_key': os.getenv('EMBY_API_KEY', ''),
        'ssl_verify': os.getenv('EMBY_SSL_VERIFY', 'true').lower() == 'true',
        'timeout': int(os.getenv('EMBY_TIMEOUT', '30')),
        'debug_mode': os.getenv('EMBY_DEBUG_MODE', 'false').lower() == 'true',
        'server_name': os.getenv('EMBY_SERVER_NAME', 'Emby Server')
    }
    
    return config


if __name__ == "__main__":
    # Test the environment loader
    print("Testing environment configuration...")
    config = get_emby_config()
    
    print(f"Emby URL: {config['url']}")
    print(f"API Key: {'Set' if config['api_key'] else 'Not set'}")
    print(f"SSL Verify: {config['ssl_verify']}")
    print(f"Timeout: {config['timeout']}s")
    print(f"Debug Mode: {config['debug_mode']}")
    print(f"Server Name: {config['server_name']}")