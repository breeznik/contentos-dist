"""Authentication utilities with per-channel token support."""
import pickle
from pathlib import Path
from typing import Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

def get_credentials(token_path: Path, secrets_path: Path):
    """Returns valid OAuth credentials for the given paths."""
    creds = None
    
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not secrets_path.exists():
                raise FileNotFoundError(f"Client secrets not found at {secrets_path}")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                if "access_denied" in str(e) or "403" in str(e):
                    print("\n🛑 AUTH ERROR: Access Denied")
                    print("   This usually means your email is not in the 'Test Users' list.")
                    print("   1. Go to Google Cloud Console > OAuth Consent Screen")
                    print("   2. Add your channel email to 'Test Users'")
                    print("   3. Save and try again.")
                raise e
        
        # Ensure parent directory exists
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_youtube_service(token_path: Path, secrets_path: Path):
    """Returns authenticated YouTube Data API service."""
    creds = get_credentials(token_path, secrets_path)
    return build('youtube', 'v3', credentials=creds)

def get_analytics_service(token_path: Path, secrets_path: Path):
    """Returns authenticated YouTube Analytics API service."""
    creds = get_credentials(token_path, secrets_path)
    return build('youtubeAnalytics', 'v2', credentials=creds)

def get_all_services(token_path: Path, secrets_path: Path):
    """Returns both YouTube and Analytics services."""
    creds = get_credentials(token_path, secrets_path)
    youtube = build('youtube', 'v3', credentials=creds)
    analytics = build('youtubeAnalytics', 'v2', credentials=creds)
    return youtube, analytics

# Context-aware helpers
def get_youtube_for_channel(context):
    """Gets YouTube service for the given channel context."""
    return get_youtube_service(context.token_path, context.secrets_path)

def get_analytics_for_channel(context):
    """Gets Analytics service for the given channel context."""
    return get_analytics_service(context.token_path, context.secrets_path)

def get_all_for_channel(context):
    """Gets both services for the given channel context."""
    return get_all_services(context.token_path, context.secrets_path)
