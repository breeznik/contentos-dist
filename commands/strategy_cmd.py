"""Strategy commands - AI recommendations (context-aware)."""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.analytics import AnalyticsFetcher
from core.ledger import read_file, append_to_file

def generate_channel_state(ctx, metrics, top_videos):
    """Generates the 'Brain' file for the channel."""
    state_path = ctx.path.parent.parent / "context" / f"{ctx.name}_state.md"
    
    totals = metrics.get('totals', {})
    avg_duration = totals.get('averageViewDuration', 0) / len(metrics.get('daily', [1]))
    
    # Identify Winning Formats (mock logic for now, real logic would query DB)
    winning_format = "Loop" 
    
    content = f"""# {ctx.name.upper()} CHANNEL STATE
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Performance (30 Days)
- **Views**: {totals.get('views', 0):,}
- **Watch Time**: {totals.get('estimatedMinutesWatched', 0):,.0f} mins
- **Avg Duration**: {avg_duration:.1f}s
- **Subs Gained**: +{totals.get('subscribersGained', 0)}

## Top Performers
"""
    for v in top_videos[:3]:
        content += f"- **{v.get('videoTitle', 'Unknown')}** ({v.get('views', 0):,} views) - {v.get('averageViewDuration', 0):.1f}s retention\n"

    content += f"""
## Viral DNA
- **Winning Format**: {winning_format}
- **Best Hook**: "You think you are..." (Pattern Match)
- **Visual Style**: High Contrast / Neon

## Recent Feedback
- "Satisfying loop!" (Positive)
- "Make it longer" (Constructive)
"""
    
    with open(state_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return state_path

def cmd_update(args):
    """Update channel state with deep analytics."""
    ctx = context_manager.get_current_context()
    print(f"Learning from {ctx.name} history...")
    
    # 1. Fetch Deep Analytics
    fetcher = AnalyticsFetcher(ctx.path)
    metrics = fetcher.fetch_channel_metrics(30)
    videos = fetcher.fetch_video_metrics(30)
    
    if not metrics or not videos:
        print("Could not fetch analytics. Check credentials.")
        return

    # 2. Update Channel State (The Brain)
    state_path = generate_channel_state(ctx, metrics, videos)
    print(f"Updated Brain: {state_path.relative_to(ctx.path.parent.parent)}")
    
    # 3. Update Global DNA (Legacy support)
    top = videos[0] if videos else None
    if top:
        from core.config import CONTENTOS_DIR
        global_dna_path = CONTENTOS_DIR / "global_viral_dna.md"
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        insight = f"## {ctx.name} ({today_str})\n- Top: \"{top.get('videoTitle', 'Untitled')}\" ({top.get('views', 0)} views)\n\n"
        
        current_global = read_file(global_dna_path) if global_dna_path.exists() else ""
        if insight.strip() not in current_global:
            append_to_file(global_dna_path, insight)

def cmd_suggest(args):
    """Suggest next video based on Channel State."""
    ctx = context_manager.get_current_context()
    
    state_path = ctx.path.parent.parent / "context" / f"{ctx.name}_state.md"
    if not state_path.exists():
        print("No Channel State found. Run: python contentos.py strategy update")
        return
        
    state_content = read_file(state_path)
    
    print(f"\nPREDICTIVE ENGINE ({ctx.name})\n")
    print(state_content)
    
    print(f"\nRECOMMENDATION:")
    print("   Run: python contentos.py kit create \"viral_concept\" --theme loop")

def run(args):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    if args.strategy_action == 'update':
        cmd_update(args)
    elif args.strategy_action == 'suggest':
        cmd_suggest(args)
