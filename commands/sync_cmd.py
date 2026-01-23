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
    next_page_token = None
    
    while True:
        # Calculate how many to fetch in this page (max 50 per page API limit)
        page_size = min(50, max_results - len(videos))
        if page_size <= 0:
            break

        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=page_size,
            pageToken=next_page_token
        )
        response = request.execute()
        
        items = response.get("items", [])
        if not items:
            break
            
        video_ids = [item["snippet"]["resourceId"]["videoId"] for item in items]
        
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
        
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    
    return videos

def run(args):
    """Main entry point for sync command."""
    
    # --- DISPATCH SUBCOMMANDS ---
    sync_action = getattr(args, 'sync_action', None)
    if sync_action == 'import-studio':
        import_studio_csv(args)
        return
    if sync_action == 'analytics':
        fetch_analytics_auto(args)
        return
    # If no action specified or action is 'run', continue with default sync
    
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
                    deep = getattr(args, 'deep', False)
                    count = getattr(args, 'count', None)
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
        
        # Determine fetch count
        count = 10
        if hasattr(args, 'deep') and args.deep:
            count = 50
        if hasattr(args, 'count') and args.count:
            count = args.count
            
        print(f"   Fetching last {count} videos...")
        videos = get_video_stats(youtube, playlist_id, max_results=count)
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
                
                # Also try to match video_id_short
                matched_short = None
                if data.get('video_id_short'):
                    matched_short = next((v for v in videos if v['id'] == data['video_id_short']), None)
                
                if matched_short:
                    if 'performance_short' not in data or data['performance_short'] is None:
                        data['performance_short'] = {}
                    
                    data['performance_short']['views_7d'] = matched_short['views']
                    data['performance_short']['likes'] = matched_short['likes']
                    data['performance_short']['synced_at'] = matched_short['published_at'][:10]

                if matched_video or matched_short:
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


def import_studio_csv(args):
    """Import YouTube Studio CSV export into video_metrics table.
    
    Expected CSV columns (from YouTube Studio > Content export):
    - Video, Video title, Video publish time, Views, Watch time (hours),
    - Average view duration, Impressions, Impressions click-through rate (%),
    - Subscribers, Comments, Likes
    """
    import csv
    import sqlite3
    from datetime import datetime
    from core.database import get_db_path, init_db
    
    ctx = context_manager.get_current_context()
    if not ctx:
        print("[!] No active channel. Run: contentos channel use <name>")
        return
    
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        print(f"[!] File not found: {csv_path}")
        return
    
    print(f">> Importing YouTube Studio data from: {csv_path.name}")
    
    # Initialize DB (creates video_metrics table if missing)
    init_db(ctx)
    db_path = get_db_path(ctx)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing video_id -> project_id mapping
    cursor.execute("SELECT id, video_id FROM projects WHERE video_id IS NOT NULL")
    video_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    snapshot_date = datetime.now().strftime("%Y-%m-%d")
    imported_count = 0
    skipped_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # YouTube Studio CSV uses "Video" column for video ID
                video_id = row.get('Video', '').strip()
                
                if not video_id or video_id not in video_map:
                    skipped_count += 1
                    continue
                
                project_id = video_map[video_id]
                
                # Parse metrics (handle various formats)
                def parse_float(val):
                    try:
                        return float(val.replace(',', '').replace('%', '').strip())
                    except:
                        return None
                
                def parse_int(val):
                    try:
                        return int(val.replace(',', '').strip())
                    except:
                        return None
                
                views = parse_int(row.get('Views', '0'))
                likes = parse_int(row.get('Likes', '0'))
                comments = parse_int(row.get('Comments', '0'))
                impressions = parse_int(row.get('Impressions', '0'))
                ctr = parse_float(row.get('Impressions click-through rate (%)', '0'))
                watch_time = parse_float(row.get('Watch time (hours)', '0'))
                subscribers = parse_int(row.get('Subscribers', '0'))
                
                # Parse average view duration (format: "0:30" or "1:23:45")
                avg_duration_str = row.get('Average view duration', '0:00')
                try:
                    parts = avg_duration_str.split(':')
                    if len(parts) == 2:
                        avg_duration = float(parts[0]) * 60 + float(parts[1])
                    elif len(parts) == 3:
                        avg_duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                    else:
                        avg_duration = 0
                except:
                    avg_duration = 0
                
                # Calculate avg_percentage_viewed (needs video duration - skip for now)
                avg_percentage = None
                
                # Insert into video_metrics
                cursor.execute('''
                    INSERT INTO video_metrics (
                        project_id, snapshot_date, views, likes, comments,
                        impressions, ctr, avg_view_duration, avg_percentage_viewed,
                        watch_time_hours, subscribers_gained
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    project_id, snapshot_date, views, likes, comments,
                    impressions, ctr, avg_duration, avg_percentage,
                    watch_time, subscribers
                ))
                
                imported_count += 1
                print(f"   ✓ {row.get('Video title', video_id)[:30]}... -> {views:,} views, {ctr:.1f}% CTR")
        
        conn.commit()
        print(f"\n>> Imported {imported_count} videos, skipped {skipped_count} (not linked to kits)")
        
    except Exception as e:
        print(f"[!] Error parsing CSV: {e}")
    finally:
        conn.close()


def fetch_analytics_auto(args):
    """Automatically fetch CTR, impressions, watch time via YouTube Analytics API.
    
    Uses the youtubeAnalytics.reports().query() endpoint to get detailed metrics
    for all videos linked to kits AND recent channel uploads.
    """
    import sqlite3
    from datetime import datetime, timedelta
    from core.database import get_db_path, init_db
    from core.auth import get_analytics_for_channel, get_youtube_for_channel
    
    ctx = context_manager.get_current_context()
    if not ctx:
        print("[!] No active channel. Run: contentos channel use <name>")
        return
    
    print(f">> Fetching Analytics for {ctx.config.name}...")
    
    # 1. Auth Services
    try:
        analytics = get_analytics_for_channel(ctx)
        youtube = get_youtube_for_channel(ctx)
    except Exception as e:
        print(f"[!] API auth failed: {e}")
        return
    
    # 2. Database Videos (Linked Kits)
    init_db(ctx)
    db_path = get_db_path(ctx)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, video_id, name FROM projects WHERE video_id IS NOT NULL")
    db_rows = cursor.fetchall()
    
    # Normalize DB videos -> {video_id: {data}}
    target_videos = {}
    for pid, vid, name in db_rows:
        target_videos[vid] = {
            "project_id": pid,
            "name": name,
            "source": "db"
        }
        
    # 3. Channel Uploads (Recent)
    # Fetch last 50 videos to ensure coverage of unlinked/manual uploads
    print("   Fetching recent channel uploads...")
    playlist_id = get_channel_uploads(youtube)
    if playlist_id:
        recent_videos = get_video_stats(youtube, playlist_id, max_results=50)
        for v in recent_videos:
            vid = v['id']
            if vid not in target_videos:
                target_videos[vid] = {
                    "project_id": None,
                    "name": v['title'],
                    "source": "channel"
                }
    
    # 4. Query Analytics
    print(f"   Analyzing {len(target_videos)} videos...")
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")
    snapshot_date = end_date
    
    fetched_count = 0
    error_count = 0
    
    # Sort for consistent output (DB first, then recent)
    sorted_vids = sorted(target_videos.items(), key=lambda x: (0 if x[1]['source']=='db' else 1))
    
    for vid_id, data in sorted_vids:
        try:
            name = data['name'][:30].replace("\n", " ").strip()
            
            response = analytics.reports().query(
                ids="channel==MINE",
                startDate=start_date,
                endDate=end_date,
                metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes,comments",
                dimensions="video",
                filters=f"video=={vid_id}"
            ).execute()
            
            rows = response.get("rows", [])
            if not rows:
                if data['source'] == 'db':
                    print(f"   - {name}... (no data)")
                continue
            
            row = rows[0]
            # [video, views, watch_min, avg_dur, avg_pct, subs, likes, comments]
            views = int(row[1]) if row[1] else 0
            watch_minutes = float(row[2]) if row[2] else 0
            avg_duration = float(row[3]) if row[3] else 0
            avg_percentage = float(row[4]) if row[4] else 0
            subs_gained = int(row[5]) if row[5] else 0
            likes = int(row[6]) if row[6] else 0
            comments = int(row[7]) if row[7] else 0
            
            # Store in DB if linked
            if data['project_id']:
                cursor.execute('''
                    INSERT INTO video_metrics (
                        project_id, snapshot_date, views, likes, comments,
                        impressions, ctr, avg_view_duration, avg_percentage_viewed,
                        watch_time_hours, subscribers_gained
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['project_id'], snapshot_date, views, likes, comments,
                    None, None, avg_duration, avg_percentage,
                    watch_minutes / 60.0, subs_gained
                ))
            
            fetched_count += 1
            source_mark = "[OK]" if data['source'] == 'db' else "[EXT]"
            print(f"   {source_mark} {name}... -> {views:,} views, {avg_percentage:.1f}% retention")
            
        except Exception as e:
            error_count += 1
            # Only complain loudly if it's a DB video we expect to work
            if data['source'] == 'db':
                print(f"   [ERR] {name}... Error: {str(e)[:40]}")
    
    conn.commit()
    conn.close()
    
    print(f"\n>> Fetched analytics for {fetched_count} videos ({error_count} errors)")
