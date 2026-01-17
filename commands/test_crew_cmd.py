"""
Test command for LLM integration.
"""
from core.llm import check_connection, list_models, ask

def run(args):
    """Diagnose LLM connection."""
    print("ContentOS: Connectivity Check")
    print("=" * 40)
    
    # 1. Ping
    print(f"Connection to Ollama...", end=" ")
    if check_connection():
        print("ONLINE")
    else:
        print("OFFLINE")
        print("   -> Is Ollama running? (Try 'ollama serve' in a terminal)")
        return

    # 2. List Models
    models = list_models()
    print(f"\nAvailable Models ({len(models)}):")
    for m in models:
        print(f"   - {m}")
    
    if not models:
        print("   Warning: No models found! Run 'ollama pull mistral'")
        return

    # 3. Test Auto-Selection
    print("\nTesting Smart Selection...")
    from core.llm import get_best_model
    best = get_best_model(force_refresh=True)
    print(f"   Auto-selected Best Model: {best}")

    print(f"\nTesting Inference (using {best})...")
    try:
        response = ask(
            prompt="Say 'Auto-selection working' and nothing else."
        )
        print(f"   Response: {best} says: {response}")
    except Exception as e:
        print(f"Error: {e}")
