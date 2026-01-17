"""Database CLI commands - db sync, analyze, query, export."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.database import (
    init_db, sync_all_projects, query_projects,
    query_scripts, get_ingredient_stats
)

def cmd_sync(args):
    """Sync all project files to SQLite database."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("[!] No active channel.")
        return
    
    print(f">> Syncing projects to database...")
    count = sync_all_projects(ctx)
    print(f">> Synced {count} projects to database.")
    print(f">> Database: {ctx.analytics_path / 'contentos.db'}")
    
    from core.ui import print_ai_hint
    print_ai_hint([
        "Analyze ingredients: python contentos.py db analyze",
        "Query projects: python contentos.py db query"
    ])

def cmd_analyze(args):
    """Analyze ingredient performance from database."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("[!] No active channel.")
        return
    
    init_db(ctx)
    # init_db(ctx) # Duplicate call removed
    stats = get_ingredient_stats(ctx)
    
    # Get Baseline for Relative Grading
    from core.database import get_channel_stats
    chan_stats = get_channel_stats(ctx)
    baseline = chan_stats.get('avg_views', 0)
    print(f"Channel Baseline: {baseline:.0f} avg views (over {chan_stats.get('total_videos',0)} videos)\n")
    
    if not any(stats.values()):
        print("[!] No performance data yet.")
        print("   1. Add kit.yaml to your projects with ingredients")
        print("   2. Publish videos and add performance data")
        print("   3. Run `contentos db sync`")
        return
    
    print(">> INGREDIENT PERFORMANCE ANALYSIS\n")
    print("=" * 60)
    
    for ingredient_type, data in stats.items():
        if not data:
            continue
            
        print(f"\n### {ingredient_type.upper().replace('_', ' ')}")
        print(f"{'Ingredient':<20} {'Videos':<8} {'Avg Views':<12} {'Retention':<10} Grade")
        print("-" * 60)
        
        for row in data:
            ingredient = row.get('ingredient') or 'unknown'
            count = row.get('count', 0)
            avg_views = row.get('avg_views') or 0
            retention = row.get('avg_retention') or 0
            
            # Calculate grade
            # Calculate grade
            # Preview Grading (Console)
            if baseline > 0:
                ratio = avg_views / baseline
                if ratio >= 2.0: grade = '[S]'
                elif ratio >= 1.2: grade = '[A]'
                elif ratio >= 0.8: grade = '[B]'
                elif ratio >= 0.4: grade = '[C]'
                else: grade = '[F]'
            else:
                grade = '[?]'
            
            print(f"{ingredient:<20} {count:<8} {avg_views:<12.0f} {retention:<10.2f} {grade}")
            print(f"{ingredient:<20} {count:<8} {avg_views:<12.0f} {retention:<10.2f} {grade}")
    
    # --- AUTO-UPDATE SCOREBOARD.MD ---
    # Try plural 'strategies' first (Legacy/User location), then singular
    scoreboard_path = ctx.strategies_path / "SCOREBOARD.md"
    if not scoreboard_path.exists():
        scoreboard_path = ctx.strategy_path / "SCOREBOARD.md"

    print(f"DEBUG: Checking path {scoreboard_path} (Exists: {scoreboard_path.exists()})")
    
    if scoreboard_path.exists():
        try:
            print(f"\n>> updating {scoreboard_path.name}...")
            
            # Generate new content
            new_content = "# Strategy Scoreboard\n\n> Auto-updated via `contentos db analyze`\n\n---\n\n## INGREDIENT RANKINGS\n\n"
            
            for ingredient_type, data in stats.items():
                if not data: continue
                # Map db keys to display headers
                header_map = {
                    'hook_type': 'Hook Types',
                    'theme': 'Themes',
                    'audio_style': 'Audio Styles',
                    'visual_style': 'Visual Styles',
                    'physics_type': 'Physics Types'
                }
                title = header_map.get(ingredient_type, ingredient_type.replace('_', ' ').title())
                
                new_content += f"### {title}\n"
                new_content += "| Rank | Ingredient | Videos | Avg Views | Retention | Grade |\n"
                new_content += "|---|---|---|---|---|---|\n"
                
                # Sort by views (handled None safely)
                sorted_rows = sorted(data, key=lambda x: (x.get('avg_views') or 0), reverse=True)
                
                for rank, row in enumerate(sorted_rows, 1):
                   ing = row.get('ingredient', 'unknown')
                   vids = row.get('count', 0)
                   views = row.get('avg_views') or 0
                   ret = row.get('avg_retention') or 0
                   
                   # Calculate grade with 7-day grace period
                   from datetime import datetime
                   last_pub = row.get('max_published_at')
                   days_old = 999
                   if last_pub:
                       try:
                           # Handle YYYY-MM-DD format
                           pub_date = datetime.strptime(last_pub[:10], '%Y-%m-%d')
                           days_old = (datetime.now() - pub_date).days
                       except:
                           pass
                   
                   if baseline > 0:
                       # Dynamic Grading
                       ratio = views / baseline
                       if ratio >= 2.0: grade = 'S'      # > 2x avg
                       elif ratio >= 1.2: grade = 'A'    # > 1.2x avg
                       elif ratio >= 0.8: grade = 'B'    # > 0.8x avg
                       elif ratio >= 0.4: grade = 'C'    # > 0.4x avg
                       elif days_old < 7: grade = 'WAIT'   # Grace period for new failures
                       else: grade = 'F'
                   else:
                       # Fallback if no baseline (first video)
                       grade = 'S' if views > 0 else 'WAIT'
                   
                   # Retention calc
                   ret_str = f"{ret*100:.0f}%" if ret > 0 else "-"
                   if ret >= 0.8: ret_display = "High"
                   elif ret >= 0.5: ret_display = "Mid"
                   elif ret > 0: ret_display = "Low"
                   else: ret_display = "-"
                   
                   new_content += f"| {rank} | {ing} | {vids} | {views:,.0f} | {ret_display} | {grade} |\n"
                new_content += "\n"
                
            # Preserve manual sections if possible, or just append standard footer
            new_content += "---\n\n## INGREDIENTS TO DROP\n\n*   **Global Rule**: Drop 'F' tier ingredients after 3 failures.\n"
            
            from core.ledger import write_file
            write_file(scoreboard_path, new_content)
            print(">> Scoreboard updated.")
            
        except Exception as e:
            print(f"[!] Failed to update scoreboard: {e}")
    print("\n" + "=" * 60)
    print("\n[?] RECOMMENDATIONS\n")
    
    # Find best performers
    all_ingredients = []
    for itype, data in stats.items():
        for row in data:
            if row.get('avg_views'):
                all_ingredients.append({
                    'type': itype,
                    'name': row.get('ingredient'),
                    'views': row.get('avg_views', 0)
                })
    
    if all_ingredients:
        sorted_ing = sorted(all_ingredients, key=lambda x: x['views'], reverse=True)
        print(">> ADOPT (Top performers):")
        for ing in sorted_ing[:3]:
            print(f"   * {ing['type']}: {ing['name']} ({ing['views']:.0f} avg views)")
        
        print("\n>> DROP (Low performers):")
        for ing in sorted_ing[-2:]:
            if ing['views'] < 200:
                print(f"   * {ing['type']}: {ing['name']} ({ing['views']:.0f} avg views)")
    else:
        print("Not enough data yet. Publish more videos!")

def cmd_query(args):
    """Query and display projects from database."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("[!] No active channel.")
        return
    
    init_db(ctx)
    projects = query_projects(ctx)
    
    if not projects:
        print("[!] No projects in database. Run `contentos db sync` first.")
        return
    
    print(f"PROJECTS ({len(projects)} total)\n")
    print(f"{'ID':<6} {'Name':<25} {'Status':<12} {'Views 7d':<10} {'Rating':<6} {'Combo'}")
    print("=" * 80)
    
    for p in projects:
        combo = f"{p.get('hook_type', '?')} + {p.get('theme', '?')}"
        views = p.get('views_7d') or '-'
        rating = p.get('overall_rating') or '-'
        print(f"{p['id']:<6} {p['name'][:24]:<25} {p['status']:<12} {str(views):<10} {rating:<6} {combo[:20]}")

def cmd_export(args):
    """Export database to JSON for cloud sync."""
    import json
    
    ctx = context_manager.get_current_context()
    if not ctx:
        print("[!] No active channel.")
        return
    
    init_db(ctx)
    projects = query_projects(ctx)
    
    export_path = ctx.analytics_path / "contentos_export.json"
    with open(export_path, 'w') as f:
        json.dump({
            'channel': ctx.config.name,
            'exported_at': str(__import__('datetime').datetime.now()),
            'projects': projects
        }, f, indent=2)
    
    print(f">> Exported to {export_path}")

def run(args):
    """Main entry point for db command."""
    if args.db_action == 'sync':
        cmd_sync(args)
    elif args.db_action == 'analyze':
        cmd_analyze(args)
    elif args.db_action == 'query':
        cmd_query(args)
    elif args.db_action == 'export':
        cmd_export(args)
    else:
        print("Usage: contentos db {sync|analyze|query|export}")
