"""Retention command - Fetch audience retention curves (context-aware)."""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.auth import get_youtube_for_channel, get_analytics_for_channel

def get_video_id(youtube, title_search=None):
    """Gets a video ID, optionally searching by title."""
    request = youtube.channels().list(part="contentDetails", mine=True)
    response = request.execute()
    
    if not response.get("items"):
        return None
    
    playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=10
    )
    response = request.execute()
    
    videos = [(item["snippet"]["resourceId"]["videoId"], item["snippet"]["title"]) 
              for item in response.get("items", [])]
    
    if not videos:
        return None
    
    if title_search:
        for vid, title in videos:
            if title_search.lower() in title.lower():
                return vid, title
    
    return videos[0]  # Return latest

def fetch_retention(analytics, video_id):
    """Fetches retention data for a video."""
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=90)
    
    request = analytics.reports().query(
        ids="channel==MINE",
        startDate=start_date.strftime("%Y-%m-%d"),
        endDate=end_date.strftime("%Y-%m-%d"),
        metrics="audienceWatchRatio",
        dimensions="elapsedVideoTimeRatio",
        filters=f"video=={video_id}",
        sort="elapsedVideoTimeRatio"
    )
    return request.execute()

def print_retention_chart(data, title):
    """Prints ASCII chart of retention."""
    if not data or "rows" not in data:
        print("No retention data available (may take 24-48h after upload).")
        return
    
    print(f"\nRETENTION CURVE: {title[:40]}")
    print("=" * 50)
    
    for row in data["rows"]:
        time_pct, retention = row
        bar_len = int(retention * 40)
        bar = "█" * bar_len
        print(f"{int(time_pct*100):3d}% | {bar} {retention*100:.1f}%")
    
    print("=" * 50)

def run(args):
    """Main entry point for retention command."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel. Run: contentos channel use <name>")
        return
    
    print(f"Fetching retention for {ctx.config.name}...")
    
    try:
        youtube = get_youtube_for_channel(ctx)
        analytics = get_analytics_for_channel(ctx)
        
        search = args.video if hasattr(args, 'video') and args.video else None
        result = get_video_id(youtube, search)
        
        if not result:
            print("No videos found.")
            return
        
        video_id, title = result
        print(f"Analyzing: {title}")
        
        data = fetch_retention(analytics, video_id)
        print_retention_chart(data, title)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
