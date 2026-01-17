"""Scout command - Competitor research (context-aware)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.auth import get_youtube_for_channel
from core.ledger import append_to_file
from core.brain import add_learning, brain_exists

DEFAULT_KEYWORDS = ["satisfying loop", "macro food", "asmr cooking", "slime mixing", "oddly satisfying"]

def get_scout_keywords(ctx):
    """Load scout keywords from viral_dna.md or use defaults."""
    from core.ledger import get_viral_dna_path, read_file
    dna_path = get_viral_dna_path(ctx)
    content = read_file(dna_path)
    
    # Try to extract keywords from DNA (look for "Keywords:" line)
    import re
    match = re.search(r'Keywords?:\s*(.+)', content, re.IGNORECASE)
    if match:
        return [k.strip() for k in match.group(1).split(',')]
    
    # Fallback to channel themes + default
    themes = ctx.config.themes if hasattr(ctx.config, 'themes') else []
    return themes + DEFAULT_KEYWORDS[:3]

def search_videos(youtube, query, max_results=5):
    """Searches YouTube for videos matching query."""
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        order="viewCount",
        maxResults=max_results
    )
    response = request.execute()
    
    video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
    
    if not video_ids:
        return []
    
    stats_request = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    )
    stats_response = stats_request.execute()
    
    results = []
    for item in stats_response.get("items", []):
        results.append({
            "id": item["id"],
            "channel": item["snippet"]["channelTitle"][:20],
            "title": item["snippet"]["title"][:40],
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0))
        })
    
    return results

def run(args):
    """Main entry point for scout command."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel. Run: contentos channel use <name>")
        return
    
    # Dynamic keywords based on channel
    keywords = [args.keyword] if hasattr(args, 'keyword') and args.keyword else get_scout_keywords(ctx)
    
    print(f"Scouting for {ctx.config.name} ({len(keywords)} keywords)...")
    
    try:
        youtube = get_youtube_for_channel(ctx)
        all_results = []
        
        for kw in keywords:
            print(f"  -> {kw}")
            results = search_videos(youtube, kw)
            all_results.extend(results)
        
        # Remove duplicates
        seen = set()
        unique = []
        for v in all_results:
            if v['id'] not in seen:
                seen.add(v['id'])
                unique.append(v)
        
        print(f"\nFound {len(unique)} competitors:")
        for v in sorted(unique, key=lambda x: x['views'], reverse=True)[:10]:
            # Safe print for Windows Console
            safe_title = v['title'][:40].encode('ascii', 'ignore').decode('ascii')
            print(f"  * {v['views']:>12,} views | {safe_title}...")
        
        # --- LLM INTELLIGENCE INJECTION ---
        # --- LLM INTELLIGENCE INJECTION ---
        if ctx.global_config.features.llm_swarm:
            print("\nSummoning DeepSeek (The Scout)...")
            from core.llm import ask
            
            # Prepare context for LLM
            video_data = "\n".join([f"- {v['title']} ({v['views']} views)" for v in sorted(unique, key=lambda x: x['views'], reverse=True)[:20]])
            
            prompt = f"""
            You are 'The Scout', an elite YouTube market researcher.
            Here is a list of top performing videos in the niche '{args.keyword}':
            
            {video_data}
            
            Your Mission:
            1. Identify the top 3 specific 'Viral Angles' or patterns.
            2. Verify if there is a 'Gap' (something missing or overdone).
            3. Recommend a specific title format that would work well.
            
            Output format: Clean Markdown.
            """
            
            analysis = ask(prompt, system="You are a strategic AI analyst.", temperature=0.7)
            print("\nSCOUT REPORT:")
            # Safe print for Windows Console
            safe_analysis = analysis.encode('ascii', 'ignore').decode('ascii')
            print(safe_analysis)
    
            # Append to market research
            import datetime
            research_path = ctx.strategy_path / "market_research.md"
            with open(research_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## Scout Report: {args.keyword}\n")
                f.write(f"**Date**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write(analysis + "\n\n")
                
                f.write("### Raw Data\n")
                for v in unique:
                    score = 'MEGA' if v['views'] > 1000000 else 'HIGH'
                    link = f"[Link](https://www.youtube.com/watch?v={v['id']})"
                    f.write(f"| {v['channel']} | {v['title']}... | {link} | {v['views']:,} | {v['likes']:,} | {score} |\n")
            
            print(f"\nMarket research updated with AI analysis!")
            
            # --- BRAIN INTEGRATION ---
            if brain_exists(ctx):
                # Extract key insight from LLM analysis for brain
                add_learning(ctx, "gaps", f"Scout analyzed '{args.keyword}' niche - see market_research.md", evidence="Scout Agent")
                print("Brain updated with market gap insight.")
        else:
            print("\nDeepSeek Scout Analysis disabled (Feature Flag: llm_swarm=False).")
            print("Use 'contentos config enable llm_swarm' to activate AI insights.")
            
            # Append plain data only
            research_path = ctx.strategy_path / "market_research.md"
            with open(research_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## Scout Report: {args.keyword} (Raw Data)\n")
                f.write("### Raw Data\n")
                for v in unique:
                    score = 'MEGA' if v['views'] > 1000000 else 'HIGH'
                    link = f"[Link](https://www.youtube.com/watch?v={v['id']})"
                    f.write(f"| {v['channel']} | {v['title']}... | {link} | {v['views']:,} | {v['likes']:,} | {score} |\n")
            print(f"\nMarket research updated (Raw Data Only).")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
