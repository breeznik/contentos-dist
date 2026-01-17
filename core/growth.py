"""Growth hacking and safety guardrails."""
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple

# Default Optimal Windows (UTC)
# These can be overridden per-channel via config
DEFAULT_OPTIMAL_WINDOWS: List[Tuple[int, int]] = [
    (12, 15),  # Window A: 12:00 - 15:00 UTC
    (19, 22),  # Window B: 19:00 - 22:00 UTC
]

# Common timezone offsets (hours from UTC)
TIMEZONE_OFFSETS = {
    'UTC': 0,
    'IST': 5.5,   # India Standard Time
    'EST': -5,    # Eastern Standard Time
    'PST': -8,    # Pacific Standard Time
    'GMT': 0,
}

def get_user_timezone_offset(tz_name: str = 'UTC') -> float:
    """Returns timezone offset in hours from UTC."""
    return TIMEZONE_OFFSETS.get(tz_name.upper(), 0)

def check_safety(
    last_publish_time: Optional[datetime], 
    daily_count: int,
    tz_offset: float = 0
) -> dict:
    """
    Checks if it is safe to post based on growth rules.
    
    Args:
        last_publish_time: Last video publish time (timezone-aware)
        daily_count: Number of videos published today
        tz_offset: User's timezone offset from UTC in hours
    """
    now = datetime.now(timezone.utc)
    warnings: List[str] = []
    
    # Rule 1: Volume
    if daily_count >= 5:
        warnings.append("DAILY LIMIT EXCEEDED (5+ videos). Risk of spam flag.")
    elif daily_count >= 3:
        warnings.append("High volume (3 videos). Consider slowing down.")
        
    # Rule 2: Spacing
    if last_publish_time:
        # Ensure timezone-aware comparison
        if last_publish_time.tzinfo is None:
            last_publish_time = last_publish_time.replace(tzinfo=timezone.utc)
        diff = now - last_publish_time
        if diff < timedelta(hours=2):
            wait_min = 120 - (diff.total_seconds() / 60)
            warnings.append(f"Gap too short ({int(diff.total_seconds()/60)}m). Wait {int(wait_min)}m.")
    
    return {
        "safe": len(warnings) == 0,
        "warnings": warnings
    }

def get_next_slot(
    tz_offset: float = 0,
    windows: Optional[List[Tuple[int, int]]] = None
) -> str:
    """
    Returns the next optimal posting slot.
    
    Args:
        tz_offset: User's timezone offset from UTC in hours
        windows: Custom optimal windows (list of (start_hour, end_hour) tuples)
    """
    if windows is None:
        windows = DEFAULT_OPTIMAL_WINDOWS
    
    now = datetime.now(timezone.utc)
    # Adjust for user's local time
    local_hour = (now.hour + tz_offset) % 24
    
    # Convert windows to local time for display
    for start, end in windows:
        local_start = (start + tz_offset) % 24
        local_end = (end + tz_offset) % 24
        
        if local_hour < local_start:
            return f"Today at {int(local_start):02d}:00 (local)"
        if local_start <= local_hour < local_end:
            return "RIGHT NOW! (Golden Window)"
            
    # If passed all, tomorrow
    first_start = (windows[0][0] + tz_offset) % 24
    return f"Tomorrow at {int(first_start):02d}:00 (local)"

