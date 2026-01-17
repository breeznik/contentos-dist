"""UI and Output utilities for ContentOS."""
from typing import List

def print_header(title: str) -> None:
    """Prints a styled header."""
    print(f"\n{title}")
    print("=" * len(title))

def print_success(msg: str) -> None:
    """Prints a success message."""
    print(f"[OK] {msg}")

def print_error(msg: str) -> None:
    """Prints an error message."""
    print(f"[ERROR] {msg}")

def print_warning(msg: str) -> None:
    """Prints a warning message."""
    print(f"[WARN] {msg}")

def print_ai_hint(actions: List[str] = None) -> None:
    """
    Prints structured next steps for AI agents.
    
    Args:
        actions: Optional manual override. If None, auto-detects from context.
    """
    if actions is None:
        actions = []
        # Auto-detect context
        from .context import context_manager
        ctx = context_manager.get_current_context()
        
        if not ctx:
            actions.append("Select a channel: python contentos.py channel use <name>")
        else:
            # Check for pending kits
            from .ledger import list_production_kits
            kits = list_production_kits(ctx)
            pending = [k for k in kits if 'Pending' in k['status']]
            
            if pending:
                actions.append(f"Publish pending kit: python contentos.py kit publish {pending[0]['id']}")
            
            # Check for recent comments (Community Sensing)
            try:
                import sqlite3
                from .database import get_db_path
                conn = sqlite3.connect(get_db_path(ctx))
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM comments WHERE sentiment_score < 0")
                neg_comments = cursor.fetchone()[0]
                conn.close()
                
                if neg_comments > 0:
                    actions.append("Review negative feedback: python contentos.py scan comments")
            except:
                pass

            # Default: Create new content
            actions.append("Create new kit: python contentos.py kit create 'idea' --theme loop")
            actions.append("Check trends: python contentos.py strategy update")

    print("\n[AI ASSISTANT HINT]")
    print("   Recommended next steps:")
    for i, action in enumerate(actions, 1):
        print(f"   {i}. {action}")
    print("-" * 40)

