"""
Helper utilities for the YouTube Comment Scraper.

This module provides utility functions for URL processing, validation,
and other common operations.
"""

import re
from urllib.parse import urlparse, parse_qs
from typing import Optional, List, Dict, Any
import pandas as pd
from datetime import datetime


def extract_video_id(url_or_id: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats or return ID if already valid.
    
    Supports formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    - Just the video ID itself
    
    Args:
        url_or_id: YouTube URL or video ID
        
    Returns:
        Video ID if valid, None otherwise
        
    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    if not url_or_id or not isinstance(url_or_id, str):
        return None
    
    # Clean the input and handle escaped characters
    url_or_id = url_or_id.strip()
    
    # Remove backslash escapes that might be added by shell
    # Convert \? to ? and \= to =
    url_or_id = url_or_id.replace('\\?', '?').replace('\\=', '=').replace('\\&', '&')
    
    # YouTube video ID pattern (11 characters, alphanumeric + dashes/underscores)
    video_id_pattern = r'^[a-zA-Z0-9_-]{11}$'
    
    # If it's already a video ID, return it
    if re.match(video_id_pattern, url_or_id):
        return url_or_id
    
    # Parse as URL
    try:
        parsed_url = urlparse(url_or_id)
        
        # Standard YouTube URL: https://www.youtube.com/watch?v=VIDEO_ID
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'm.youtube.com']:
            if parsed_url.path == '/watch':
                query_params = parse_qs(parsed_url.query)
                video_id = query_params.get('v', [None])[0]
                if video_id and re.match(video_id_pattern, video_id):
                    return video_id
            
            # Embed URL: https://www.youtube.com/embed/VIDEO_ID
            elif parsed_url.path.startswith('/embed/'):
                video_id = parsed_url.path.split('/embed/')[-1]
                if re.match(video_id_pattern, video_id):
                    return video_id
            
            # Direct video URL: https://www.youtube.com/v/VIDEO_ID
            elif parsed_url.path.startswith('/v/'):
                video_id = parsed_url.path.split('/v/')[-1]
                if re.match(video_id_pattern, video_id):
                    return video_id
        
        # Short YouTube URL: https://youtu.be/VIDEO_ID
        elif parsed_url.hostname == 'youtu.be':
            video_id = parsed_url.path.lstrip('/')
            if re.match(video_id_pattern, video_id):
                return video_id
                
    except Exception:
        pass
    
    return None


def validate_youtube_url(url: str) -> bool:
    """
    Validate if a URL is a valid YouTube URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid YouTube URL, False otherwise
    """
    return extract_video_id(url) is not None


def is_valid_video_id(video_id: str) -> bool:
    """
    Check if a string is a valid YouTube video ID format.
    
    Args:
        video_id: String to check
        
    Returns:
        True if valid video ID format, False otherwise
    """
    if not video_id or not isinstance(video_id, str):
        return False
    
    # YouTube video IDs are exactly 11 characters, alphanumeric plus dashes/underscores
    video_id_pattern = r'^[a-zA-Z0-9_-]{11}$'
    return bool(re.match(video_id_pattern, video_id))


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be safe for use as a filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    
    # Limit length
    max_length = 200
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def format_timestamp(timestamp: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object as a string.
    
    Args:
        timestamp: Datetime object to format
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    if not isinstance(timestamp, datetime):
        return str(timestamp)
    
    return timestamp.strftime(format_str)


def parse_iso_timestamp(iso_string: str) -> Optional[datetime]:
    """
    Parse an ISO 8601 timestamp string to datetime object.
    
    Args:
        iso_string: ISO 8601 timestamp string
        
    Returns:
        Datetime object or None if parsing fails
    """
    if not iso_string:
        return None
    
    try:
        # Handle various ISO formats
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",           # 2023-01-01T12:00:00Z
            "%Y-%m-%dT%H:%M:%S.%fZ",       # 2023-01-01T12:00:00.123456Z
            "%Y-%m-%dT%H:%M:%S%z",         # 2023-01-01T12:00:00+00:00
            "%Y-%m-%dT%H:%M:%S.%f%z",      # 2023-01-01T12:00:00.123456+00:00
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(iso_string, fmt)
            except ValueError:
                continue
                
        # Try pandas for more flexible parsing
        import pandas as pd
        return pd.to_datetime(iso_string, utc=True).to_pydatetime()
        
    except Exception:
        return None


def chunk_list(input_list: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        input_list: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
        
    Examples:
        >>> chunk_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")
    
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


def safe_get(dictionary: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Safely get a nested dictionary value using dot notation.
    
    Args:
        dictionary: Dictionary to search
        key_path: Dot-separated key path (e.g., 'user.profile.name')
        default: Default value if key not found
        
    Returns:
        Value at key path or default
        
    Examples:
        >>> data = {'user': {'profile': {'name': 'John'}}}
        >>> safe_get(data, 'user.profile.name')
        'John'
        >>> safe_get(data, 'user.profile.age', 25)
        25
    """
    keys = key_path.split('.')
    current = dictionary
    
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def normalize_text(text: str) -> str:
    """
    Normalize text for analysis by cleaning and standardizing.
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Basic text cleaning
    normalized = text.strip()
    
    # Replace multiple whitespace with single space
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove zero-width characters and other invisible characters
    normalized = re.sub(r'[\u200b-\u200f\u2060\ufeff]', '', normalized)
    
    return normalized


def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Estimate reading time for text in minutes.
    
    Args:
        text: Text to analyze
        words_per_minute: Average reading speed
        
    Returns:
        Estimated reading time in minutes
    """
    if not text:
        return 0
    
    word_count = len(text.split())
    reading_time = max(1, round(word_count / words_per_minute))
    
    return reading_time


def create_safe_directory(path: str) -> bool:
    """
    Safely create a directory, handling errors gracefully.
    
    Args:
        path: Directory path to create
        
    Returns:
        True if directory was created or already exists, False if failed
    """
    try:
        from pathlib import Path
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False
