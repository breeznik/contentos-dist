"""Sync command - Updates analytics ledger (context-aware)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.auth import get_youtube_for_channel
from core.ledger import read_file, write_file, list_production_kits
from core.database import sync_all_projects
import yaml
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_channel_uploads(youtube):
    """Gets the uploads playlist ID for the authenticated user's channel."""
    request = youtube.channels().list(part="contentDetails", mine=True)
    response = request.execute()
    if not response.get("items"):
        return None
    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_video_stats(youtube, playlist_id, max_results=10):
    """Fetches video IDs from playlist and their statistics."""
    videos = []
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=max_results
    )
    response = request.execute()
    
    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in response.get("items", [])]
    
    if video_ids:
        stats_request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        )
        stats_response = stats_request.execute()
        
        for item in stats_response.get("items", []):
            videos.append({
                "id": item["id"],
                "title": item["snippet"]["title"][:40],
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "published_at": item["snippet"]["publishedAt"]
            })
    
    return videos

def run(args):
    """Main entry point for sync command."""
    
    # --- GLOBAL SYNC LOGIC ---
    if hasattr(args, 'all_channels') and args.all_channels:
        print("GLOBAL SYNC INITIATED...")
        channels = context_manager.list_channels()
        for ch in channels:
            name = ch['name']
            print(f"\n>> Switching to channel: {name}")
            if context_manager.use_channel(name):
                # Recursive call without the --all flag
                class SingleArgs:
                    auto_dna = getattr(args, 'auto_dna', False)
                    all_channels = False
                run(SingleArgs())
        print("\n>> GLOBAL SYNC COMPLETE.")
        return

    # --- SINGLE CHANNEL LOGIC ---
    ctx = context_manager.get_current_context()
    if not ctx:
        print("[!] No active channel. Run: contentos channel use <name>")
        return
    
    print(f">> Syncing {ctx.config.name} stats...")
    
    try:
        youtube = get_youtube_for_channel(ctx)
        playlist_id = get_channel_uploads(youtube)
        
        if not playlist_id:
            print("[!] Could not find channel uploads.")
            return
        
        videos = get_video_stats(youtube, playlist_id)
        print(f"   Found {len(videos)} videos")
        
        for v in videos:
            title_clean = v['title'].encode('ascii', 'ignore').decode('ascii')
            print(f"  * {title_clean[:30]}... -> {v['views']:,} views")
        
        # Generate Markdown Table
        md_content = f"# {ctx.config.name} Analytics Ledger\n\n"
        md_content += "| ID | Title | Published | Views | Likes | Score |\n"
        md_content += "|---|---|---|---|---|---|\n"
        
        for v in videos:
            score = "⚪" # Placeholder for now
            if v['views'] > 1000: score = "🟢"
            md_content += f"| {v['id']} | {v['title']} | {v['published_at'][:10]} | {v['views']:,} | {v['likes']:,} | {score} |\n"

        # Update ledger
        ledger_path = ctx.strategy_path / f"{ctx.config.name.lower()}_analytics.md"
        write_file(ledger_path, md_content)
        print(f">> Analytics synced for {ctx.config.name}!")
        
        
        # --- NEW LOGIC: Update kit.yaml files ---
        kits = list_production_kits(ctx)
        updated_kits = 0
        
        print("\n>> Mapping videos to valid Kits...")
        for kit in kits:
            kit_path = ctx.production_path / f"{kit['id']}_{kit['name']}"
            yaml_path = kit_path / 'kit.yaml'
            
            if not yaml_path.exists():
                continue
                
            try:
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                # Find matching video
                matched_video = None
                
                # 1. Match by stored Video ID
                if data.get('video_id'):
                    matched_video = next((v for v in videos if v['id'] == data['video_id']), None)
                
                # 2. Match by Title Similarity (if no ID or ID not found)
                if not matched_video:
                    if not isinstance(data, dict):
                        print(f"   [!] Skipping malformed kit (list): {kit['name']}")
                        continue
                    # Fuzzy match title
                    clean_name = kit['name'].replace('_', ' ')
                    best_match = None
                    best_score = 0.0
                    for v in videos:
                        score = similarity(clean_name.lower(), v['title'].lower())
                        if score > 0.4 and score > best_score: # Threshold
                            best_score = score
                            best_match = v
                    
                    if best_match:
                        print(f"   * Auto-linked '{kit['name']}' -> '{best_match['title'][:20]}...'")
                        matched_video = best_match
                        data['video_id'] = matched_video['id'] # Save ID for future

                if matched_video:
                    # Update stats
                    if 'performance' not in data or data['performance'] is None:
                        data['performance'] = {}
                    
                    data['performance']['views_7d'] = matched_video['views']
                    data['performance']['likes'] = matched_video['likes']
                    data['performance']['synced_at'] = matched_video['published_at'][:10] # Just the date
                    data['status'] = 'published'

                    with open(yaml_path, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, default_flow_style=False)
                    updated_kits += 1
            except Exception as e:
                print(f"[!] Error updating {kit['name']}: {e}")

        print(f">> Updated {updated_kits} kits with fresh analytics.")

        # --- Trigger DB Sync ---
        print("\n>> Updating Database...")
        from commands import db_cmd
        # Create a dummy args object
        class Args:
            pass
        db_cmd.cmd_sync(Args())

        # Auto-update viral DNA if flag is set
        if hasattr(args, 'auto_dna') and args.auto_dna:
            print("\n>> Auto-updating Viral DNA...")
            from commands import strategy_cmd
            # Create a mock args object for strategy update
            class MockArgs:
                strategy_action = 'update'
            strategy_cmd.run(MockArgs())
        else:
            from core.ui import print_ai_hint
            print_ai_hint([
                f"Analyze trends: python contentos.py strategy update",
                f"Get next video idea: python contentos.py strategy suggest"
            ])
        
    except FileNotFoundError as e:
        print(f"[!] {e}")
        print(f"   Copy client_secrets.json to {ctx.analytics_path}/")
    except Exception as e:
        print(f"[!] Error: {e}")

