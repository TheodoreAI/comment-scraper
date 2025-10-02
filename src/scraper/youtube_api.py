"""
YouTube API client for the Comment Scraper.

This module provides a wrapper around the YouTube Data API v3 for
extracting video information and comments.
"""

import time
from typing import Dict, List, Optional, Any, Generator
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Handle imports for both package and direct execution
try:
    from ..utils.config import ConfigManager
    from ..utils.logger import LoggerMixin, log_api_call
    from ..utils.helpers import extract_video_id, is_valid_video_id
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.config import ConfigManager
    from utils.logger import LoggerMixin, log_api_call
    from utils.helpers import extract_video_id, is_valid_video_id


class YouTubeAPIError(Exception):
    """Custom exception for YouTube API errors."""
    pass


class QuotaExceededError(YouTubeAPIError):
    """Exception raised when API quota is exceeded."""
    pass


class VideoNotFoundError(YouTubeAPIError):
    """Exception raised when video is not found or inaccessible."""
    pass


class YouTubeAPIClient(LoggerMixin):
    """
    Client for interacting with the YouTube Data API v3.
    
    This class handles authentication, rate limiting, and provides
    methods for fetching video information and comments.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the YouTube API client.
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__()
        
        # Initialize configuration
        self.config = config_manager or ConfigManager()
        youtube_config = self.config.get_youtube_config()
        rate_limit_config = self.config.get_rate_limit_config()
        
        # API configuration
        # Try to get API key from Streamlit secrets first
        try:
            import streamlit as st
            if 'youtube_api_token' in st.secrets:
                self.api_key = st.secrets.youtube_api_token
            else:
                self.api_key = youtube_config.get('api_key')
        except (ImportError, AttributeError):
            self.api_key = youtube_config.get('api_key')
            
        self.api_service_name = youtube_config.get('api_service_name', 'youtube')
        self.api_version = youtube_config.get('api_version', 'v3')
        
        # Rate limiting configuration
        self.requests_per_second = rate_limit_config.get('requests_per_second', 1)
        self.last_request_time = 0
        
        # Request limits
        self.max_results_per_request = youtube_config.get('max_results_per_request', 100)
        self.max_total_comments = youtube_config.get('max_total_comments', 1000)
        
        # Validate configuration
        self._validate_config()
        
        # Initialize the YouTube service
        self._service = None
        self._initialize_service()
    
    def _validate_config(self) -> None:
        """Validate the API configuration."""
        # Try to get API key from Streamlit secrets first
        try:
            import streamlit as st
            if 'youtube_api_token' in st.secrets:
                self.api_key = st.secrets.youtube_api_token
        except (ImportError, AttributeError):
            pass  # Not running in Streamlit or secret not found
            
        if not self.api_key:
            raise YouTubeAPIError("YouTube API key is not configured")
        
        if self.api_key == "YOUR_YOUTUBE_API_KEY_HERE":
            raise YouTubeAPIError("Please set a valid YouTube API key in config.yaml or Streamlit secrets")
        
        if self.max_results_per_request > 100:
            self.logger.warning("max_results_per_request > 100, setting to 100 (API limit)")
            self.max_results_per_request = 100
    
    def _initialize_service(self) -> None:
        """Initialize the YouTube API service."""
        try:
            self._service = build(
                self.api_service_name,
                self.api_version,
                developerKey=self.api_key
            )
            self.logger.info("YouTube API service initialized successfully")
            
        except Exception as e:
            raise YouTubeAPIError(f"Failed to initialize YouTube API service: {str(e)}")
    
    def _rate_limit(self) -> None:
        """Implement rate limiting to avoid quota issues."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second
        
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _handle_api_error(self, error: HttpError, operation: str) -> None:
        """
        Handle API errors with appropriate exceptions.
        
        Args:
            error: The HTTP error from the API
            operation: Description of the operation that failed
        """
        status_code = error.resp.status
        error_details = str(error)
        
        self.logger.error(f"API error during {operation}: {error_details}")
        
        if status_code == 403:
            if "quotaExceeded" in error_details or "dailyLimitExceeded" in error_details:
                raise QuotaExceededError(f"API quota exceeded during {operation}")
            elif "commentsDisabled" in error_details:
                raise VideoNotFoundError(f"Comments are disabled for this video")
            else:
                raise YouTubeAPIError(f"Permission denied during {operation}: {error_details}")
        
        elif status_code == 404:
            raise VideoNotFoundError(f"Video not found during {operation}")
        
        elif status_code >= 500:
            raise YouTubeAPIError(f"YouTube API server error during {operation}: {error_details}")
        
        else:
            raise YouTubeAPIError(f"API error during {operation}: {error_details}")
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video information
            
        Raises:
            YouTubeAPIError: If API request fails
            VideoNotFoundError: If video is not found
        """
        if not is_valid_video_id(video_id):
            raise ValueError(f"Invalid video ID format: {video_id}")
        
        self._rate_limit()
        
        try:
            log_api_call("YouTube API", "videos.list", {"id": video_id})
            
            request = self._service.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                raise VideoNotFoundError(f"Video not found: {video_id}")
            
            video_data = response['items'][0]
            
            # Extract relevant information
            snippet = video_data.get('snippet', {})
            statistics = video_data.get('statistics', {})
            content_details = video_data.get('contentDetails', {})
            
            video_info = {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_id': snippet.get('channelId', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'duration': content_details.get('duration', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId', ''),
                'default_language': snippet.get('defaultLanguage', ''),
                'default_audio_language': snippet.get('defaultAudioLanguage', ''),
            }
            
            self.logger.info(f"Retrieved video info for: {video_info['title']}")
            return video_info
            
        except HttpError as e:
            self._handle_api_error(e, "get_video_info")
        except Exception as e:
            raise YouTubeAPIError(f"Unexpected error getting video info: {str(e)}")
    
    def get_comments(
        self,
        video_id: str,
        max_results: Optional[int] = None,
        order: str = "relevance"
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Get comments for a YouTube video with pagination.
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to fetch (None for config default)
            order: Comment ordering ('relevance', 'time')
            
        Yields:
            Comment dictionaries
            
        Raises:
            YouTubeAPIError: If API request fails
            VideoNotFoundError: If video is not found or comments disabled
        """
        if not is_valid_video_id(video_id):
            raise ValueError(f"Invalid video ID format: {video_id}")
        
        if max_results is None:
            max_results = self.max_total_comments
        
        if order not in ['relevance', 'time']:
            raise ValueError("order must be 'relevance' or 'time'")
        
        comments_fetched = 0
        next_page_token = None
        
        self.logger.info(f"Starting comment extraction for video: {video_id}")
        
        while comments_fetched < max_results:
            self._rate_limit()
            
            # Calculate how many comments to request in this batch
            remaining_comments = max_results - comments_fetched
            page_size = min(self.max_results_per_request, remaining_comments)
            
            try:
                log_api_call("YouTube API", "commentThreads.list", {
                    "videoId": video_id,
                    "maxResults": page_size,
                    "order": order
                })
                
                request = self._service.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=page_size,
                    order=order,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                items = response.get('items', [])
                
                if not items:
                    self.logger.info("No more comments found")
                    break
                
                # Process comments in this page
                for item in items:
                    if comments_fetched >= max_results:
                        break
                    
                    comment_data = self._extract_comment_data(item)
                    yield comment_data
                    comments_fetched += 1
                    
                    # Also yield replies if they exist
                    replies = item.get('replies', {}).get('comments', [])
                    for reply_item in replies:
                        if comments_fetched >= max_results:
                            break
                        
                        reply_data = self._extract_comment_data(
                            {'snippet': {'topLevelComment': reply_item}},
                            is_reply=True
                        )
                        yield reply_data
                        comments_fetched += 1
                
                # Check for next page
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    self.logger.info("Reached end of comments")
                    break
                    
                self.logger.debug(f"Fetched {comments_fetched} comments so far")
                
            except HttpError as e:
                self._handle_api_error(e, "get_comments")
            except Exception as e:
                raise YouTubeAPIError(f"Unexpected error getting comments: {str(e)}")
        
        self.logger.info(f"Comment extraction completed. Total comments: {comments_fetched}")
    
    def _extract_comment_data(self, item: Dict[str, Any], is_reply: bool = False) -> Dict[str, Any]:
        """
        Extract comment data from API response item.
        
        Args:
            item: Comment item from API response
            is_reply: Whether this is a reply to another comment
            
        Returns:
            Processed comment data
        """
        if is_reply:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_id = item['snippet']['topLevelComment']['id']
        else:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_id = item['snippet']['topLevelComment']['id']
        
        return {
            'comment_id': comment_id,
            'video_id': comment.get('videoId', ''),
            'text': comment.get('textDisplay', ''),
            'text_original': comment.get('textOriginal', ''),
            'author_display_name': comment.get('authorDisplayName', ''),
            'author_profile_image_url': comment.get('authorProfileImageUrl', ''),
            'author_channel_url': comment.get('authorChannelUrl', ''),
            'author_channel_id': comment.get('authorChannelId', {}).get('value', ''),
            'like_count': int(comment.get('likeCount', 0)),
            'published_at': comment.get('publishedAt', ''),
            'updated_at': comment.get('updatedAt', ''),
            'is_reply': is_reply,
            'parent_id': item.get('snippet', {}).get('topLevelComment', {}).get('id', '') if is_reply else '',
            'total_reply_count': item.get('snippet', {}).get('totalReplyCount', 0) if not is_reply else 0
        }
