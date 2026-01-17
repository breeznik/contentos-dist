"""Community Sensing Module: Listen to the audience."""
import sqlite3
from pathlib import Path
from datetime import datetime

from core.auth import get_youtube_for_channel
from core.database import get_db_path

def fetch_comments(context, video_id=None, max_results=20):
    """
    Fetches comments from YouTube Data API and stores them in DB.
    
    Args:
        context: Active context object
        video_id: Specific video ID (optional). If None, fetches for channel's top videos.
        max_results: Max comments to fetch per video.
    """
    youtube = get_youtube_for_channel(context)
    if not youtube:
        print("No valid YouTube service found.")
        return []

    # If no video_id, we need to find recent videos first.
    # For now, let's assume we pass a list of video_ids or fetch from DB.
    # To keep it simple for v1, we will fetch for the LAST 5 videos in the DB.
    
    conn = sqlite3.connect(get_db_path(context))
    cursor = conn.cursor()
    
    if not video_id:
        # Get last 5 published videos
        # We need to query the 'scripts' or 'projects' table, but better to query actual YouTube uploads
        # For this MVP, let's rely on the strategy_cmd's analytics table which works, 
        # OR just use the 'uploads' playlist logic if we want to be pure.
        # Let's use the DB 'projects' table if it has video_ids (it might not have them all).
        # Actually, best implementation matches 'sync': query channel uploads.
        from commands.sync_cmd import get_channel_uploads, get_video_stats
        uploads_id = get_channel_uploads(youtube)
        if not uploads_id:
            return []
            
        videos = get_video_stats(youtube, uploads_id, max_results=5)
        video_ids = [v['id'] for v in videos]
    else:
        video_ids = [video_id]
        
    comments_saved = 0
    print(f"Scanning comments for {len(video_ids)} videos...")
    
    for vid in video_ids:
        try:
            request = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=vid,
                maxResults=max_results,
                textFormat="plainText",
                order="relevance" # Get top comments
            )
            response = request.execute()
            
            for item in response.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                
                comment_id = item['id']
                author = snippet['authorDisplayName']
                text = snippet['textDisplay']
                published = snippet['publishedAt']
                like_count = snippet['likeCount']
                reply_count = item['snippet']['totalReplyCount']
                
                # Mock Sentiment (To avoid installing NLTK/TextBlob for now)
                # We can add a simple keyword scanner
                sentiment = 0.0
                lower_text = text.lower()
                if any(w in lower_text for w in ['love', 'great', 'awesome', 'good', 'best']):
                    sentiment = 0.8
                elif any(w in lower_text for w in ['hate', 'bad', 'worst', 'boring']):
                    sentiment = -0.8
                
                # Upsert into DB
                cursor.execute('''
                    INSERT OR REPLACE INTO comments 
                    (id, video_id, author_name, text_original, sentiment_score, published_at, reply_count, like_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (comment_id, vid, author, text, sentiment, published, reply_count, like_count))
                
                comments_saved += 1
                
            print(f"   * {vid}: Fetched {len(response.get('items', []))} threads")
            
        except Exception as e:
            print(f"   Warning: Error fetching comments for {vid}: {e}")
            
    conn.commit()
    conn.close()
    return comments_saved

def analyze_community_sentiment(context):
    """Returns a summary of community sentiment."""
    conn = sqlite3.connect(get_db_path(context))
    cursor = conn.cursor()
    
    cursor.execute('SELECT count(*), avg(sentiment_score) FROM comments')
    total, avg_sent = cursor.fetchone()
    
    # Get top 5 most liked comments
    cursor.execute('''
        SELECT author_name, text_original, like_count 
        FROM comments 
        ORDER BY like_count DESC 
        LIMIT 5
    ''')
    top_comments = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_comments': total,
        'average_sentiment': avg_sent or 0.0,
        'top_comments': top_comments
    }
