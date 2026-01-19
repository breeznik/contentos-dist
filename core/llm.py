"""
LLM Driver for ContentOS
Connects to local Ollama instance (or compatible APIs).
"""
import requests
import json
from typing import List, Dict, Any, Optional

# Default Configuration
OLLAMA_HOST = "http://localhost:11434"
# Priority list: High IQ -> Coding -> Fast Local
PRIORITY_MODELS = [
    "deepseek-v3.1:671b-cloud",  # Best reasoning
    "qwen3-coder:480b-cloud",     # Good backup
    "llama3.2:1b",               # Local fallback
    "mistral"                    # Old faithful
]

_ACTIVE_MODEL = None

def check_connection() -> bool:
    """Checks if Ollama is accessible."""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return response.status_code == 200
    except (requests.RequestException, ConnectionError):
        return False

def ensure_ollama_running() -> bool:
    """Ensures Ollama is running, starts it if not."""
    import subprocess
    import time
    from core.context import context_manager
    
    if check_connection():
        return True
    
    # Check feature flag
    try:
        config = context_manager.global_config
        if not config.features.ollama_autostart:
            print("[!] Ollama not running (Auto-start DISABLED in config)")
            return False
    except Exception:
        # Fallback if config can't be read
        pass
    
    print("[*] Ollama not running. Attempting to start...")
    
    try:
        # Try to start Ollama in background
        # Windows: ollama serve runs the server
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        # Wait for it to start (up to 10 seconds)
        for i in range(10):
            time.sleep(1)
            if check_connection():
                print("[✓] Ollama started successfully!")
                return True
            print(f"   Waiting... ({i+1}/10)")
        
        print("[!] Ollama failed to start within timeout")
        return False
        
    except FileNotFoundError:
        print("[!] Ollama not found. Install from https://ollama.ai")
        return False
    except Exception as e:
        print(f"[!] Failed to start Ollama: {e}")
        return False

def list_models() -> List[str]:
    """Returns list of available local models."""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return [m['name'] for m in data.get('models', [])]
        return []
    except (requests.RequestException, ConnectionError):
        return []

def get_best_model(force_refresh=False) -> str:
    """
    Smartly selects the best available model from the priority list.
    Pings them in order to find the first one that works.
    """
    global _ACTIVE_MODEL
    if _ACTIVE_MODEL and not force_refresh:
        return _ACTIVE_MODEL

    available = list_models()
    if not available:
        return "mistral" # Verification failed, fallback default

    # 1. Check Priority List
    for preferred in PRIORITY_MODELS:
        if preferred in available:
            # Ping test to be sure
            if _ping_model(preferred):
                print(f"ContentOS: Selected Model -> {preferred}")
                _ACTIVE_MODEL = preferred
                return preferred
    
    # 2. Fallback to whatever is there
    _ACTIVE_MODEL = available[0]
    return _ACTIVE_MODEL

def _ping_model(model_name: str) -> bool:
    """Quick inference check to ensure model is actually responding."""
    try:
        url = f"{OLLAMA_HOST}/api/chat"
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "ping"}],
            "stream": False
        }
        res = requests.post(url, json=payload, timeout=5)
        return res.status_code == 200
    except (requests.RequestException, ConnectionError):
        return False

def ask(
    prompt: str,
    system: str = "You are a helpful AI assistant for a YouTube automation system.",
    model: Optional[str] = None,
    temperature: float = 0.7,
    json_mode: bool = False
) -> str:
    """
    Sends a simple prompt to the LLM and returns the text response.
    
    Args:
        prompt: The user's query.
        system: System context/persona.
        model: Model name. If None, auto-selects best model.
        temperature: Creativity (0.0 - 1.0).
        json_mode: If True, forces valid JSON output.
    
    Returns:
        String content of the response.
    """
    target_model = model or get_best_model()
    
    url = f"{OLLAMA_HOST}/api/chat"
    
    payload = {
        "model": target_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }
    
    if json_mode:
        payload["format"] = "json"

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        # Extract content
        content = result.get("message", {}).get("content", "")
        return content
        
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Is it running on port 11434?"
    except Exception as e:
        return f"Error: {str(e)}"
