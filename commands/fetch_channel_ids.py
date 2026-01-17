"""
ContentOS: Auto-Fetch Channel IDs
Automatically populates youtube_channel_id in all .channel.json files.

Usage: python commands/fetch_channel_ids.py
"""

import json
import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Configuration
CHANNELS_DIR = Path(__file__).parent.parent / "channels"
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']


def get_credentials(channel_path: Path):
    """Load or create OAuth credentials for a channel."""
    creds = None
    token_path = channel_path / "analytics" / "token.pickle"
    secrets_path = channel_path / "analytics" / "client_secrets.json"
    
    if not secrets_path.exists():
        print(f"  ⚠️  No client_secrets.json found in {channel_path.name}/analytics/")
        return None
    
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Ensure directory exists
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


def fetch_channel_id(creds) -> dict:
    """Fetch channel info using YouTube Data API."""
    service = build('youtube', 'v3', credentials=creds)
    
    response = service.channels().list(
        part='snippet,id',
        mine=True
    ).execute()
    
    if response.get('items'):
        channel = response['items'][0]
        return {
            'id': channel['id'],
            'title': channel['snippet']['title'],
            'handle': channel['snippet'].get('customUrl', '')
        }
    return None


def update_channel_config(channel_path: Path, channel_id: str, channel_title: str):
    """Update .channel.json with the fetched ID."""
    config_path = channel_path / ".channel.json"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    config['youtube_channel_id'] = channel_id
    config['name'] = channel_title
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"  ✅ Updated {channel_path.name}/.channel.json with ID: {channel_id}")


def main():
    print("\n🔍 ContentOS: Fetching Channel IDs...\n")
    
    # Get all channel directories
    channels = [d for d in CHANNELS_DIR.iterdir() if d.is_dir() and (d / ".channel.json").exists()]
    
    if not channels:
        print("❌ No channels found with .channel.json")
        return
    
    for channel_path in channels:
        print(f"\n📺 Processing: {channel_path.name}")
        
        # Check if already has ID
        config_path = channel_path / ".channel.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if config.get('youtube_channel_id'):
            print(f"  ✓ Already has ID: {config['youtube_channel_id']}")
            continue
        
        # Get credentials and fetch ID
        creds = get_credentials(channel_path)
        if not creds:
            continue
        
        channel_info = fetch_channel_id(creds)
        if channel_info:
            update_channel_config(channel_path, channel_info['id'], channel_info['title'])
        else:
            print(f"  ❌ Could not fetch channel ID for {channel_path.name}")
    
    print("\n✅ Channel ID fetch complete!\n")


if __name__ == '__main__':
    main()
