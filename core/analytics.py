"""
ContentOS: Deep Analytics Module
Fetches watch time, retention, and advanced metrics from YouTube Analytics API v2.

Usage:
    from core.analytics import AnalyticsFetcher
    fetcher = AnalyticsFetcher(channel_path)
    data = fetcher.fetch_metrics(days=30)
"""

import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = [
    'https://www.googleapis.com/auth/yt-analytics.readonly',
    'https://www.googleapis.com/auth/youtube.readonly'
]


class AnalyticsFetcher:
    """Fetches deep analytics for a ContentOS channel."""
    
    def __init__(self, channel_path: Path):
        self.channel_path = Path(channel_path)
        self.analytics_dir = self.channel_path / "analytics"
        self.creds = None
        self.channel_id = self._load_channel_id()
        
    def _load_channel_id(self) -> str:
        """Load channel ID from .channel.json."""
        config_path = self.channel_path / ".channel.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config.get('youtube_channel_id', '')
        return ''
    
    def authenticate(self) -> bool:
        """Load or create OAuth credentials."""
        token_path = self.analytics_dir / "token.pickle"
        secrets_path = self.analytics_dir / "client_secrets.json"
        
        if not secrets_path.exists():
            print(f"No client_secrets.json found in {self.analytics_dir}")
            return False
        
        if token_path.exists():
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)
        
        return True
    
    def fetch_channel_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Fetch channel-level metrics for the past N days."""
        if not self.authenticate():
            return {}
        
        service = build('youtubeAnalytics', 'v2', credentials=self.creds)
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        response = service.reports().query(
            ids=f'channel=={self.channel_id}',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost,likes,comments,shares',
            dimensions='day',
            sort='day'
        ).execute()
        
        return self._parse_response(response)
    
    def fetch_video_metrics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Fetch per-video metrics for the past N days."""
        if not self.authenticate():
            return []
        
        service = build('youtubeAnalytics', 'v2', credentials=self.creds)
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        response = service.reports().query(
            ids=f'channel=={self.channel_id}',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage',
            dimensions='video',
            sort='-views',
            maxResults=50
        ).execute()
        
        return self._parse_video_response(response)
    
    def _parse_response(self, response: Dict) -> Dict[str, Any]:
        """Parse API response into usable format."""
        columns = [col['name'] for col in response.get('columnHeaders', [])]
        rows = response.get('rows', [])
        
        result = {
            'period': f"{len(rows)} days",
            'totals': {},
            'daily': []
        }
        
        for row in rows:
            day_data = dict(zip(columns, row))
            result['daily'].append(day_data)
            
            # Accumulate totals
            for key, value in day_data.items():
                if key != 'day' and isinstance(value, (int, float)):
                    result['totals'][key] = result['totals'].get(key, 0) + value
        
        return result
    
    def _parse_video_response(self, response: Dict) -> List[Dict[str, Any]]:
        """Parse per-video API response."""
        columns = [col['name'] for col in response.get('columnHeaders', [])]
        rows = response.get('rows', [])
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_summary(self, days: int = 30) -> str:
        """Generate a human-readable analytics summary."""
        metrics = self.fetch_channel_metrics(days)
        
        if not metrics:
            return "Could not fetch analytics."
        
        totals = metrics.get('totals', {})
        
        return f"""
**{self.channel_path.name.upper()}** Analytics ({days} Days)

| Metric | Value |
|--------|-------|
| Views | {totals.get('views', 0):,} |
| Watch Time | {totals.get('estimatedMinutesWatched', 0):,.0f} mins |
| Avg. View Duration | {totals.get('averageViewDuration', 0)/len(metrics.get('daily', [1])):.1f}s |
| Subscribers Gained | +{totals.get('subscribersGained', 0)} |
| Subscribers Lost | -{totals.get('subscribersLost', 0)} |
| Likes | {totals.get('likes', 0)} |
| Comments | {totals.get('comments', 0)} |
| Shares | {totals.get('shares', 0)} |
"""


if __name__ == '__main__':
    # Quick test
    import sys
    if len(sys.argv) > 1:
        channel_name = sys.argv[1]
        channel_path = Path(__file__).parent.parent / "channels" / channel_name
        fetcher = AnalyticsFetcher(channel_path)
        print(fetcher.get_summary(30))
    else:
        print("Usage: python analytics.py <channel_name>")
