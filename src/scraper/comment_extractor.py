"""
Main comment extractor for the YouTube Comment Scraper.

This module provides the high-level interface for extracting comments
from YouTube videos with data validation and export capabilities.
"""

import csv
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Generator
from datetime import datetime
import pandas as pd

# Handle imports for both package and direct execution
try:
    from .youtube_api import YouTubeAPIClient, YouTubeAPIError, VideoNotFoundError, QuotaExceededError
    from .data_validator import DataValidator
    from ..utils.config import ConfigManager
    from ..utils.logger import LoggerMixin
    from ..utils.helpers import extract_video_id, sanitize_filename, format_timestamp, create_safe_directory
    from ..analysis.sentiment_analyzer import SentimentAnalyzer
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from scraper.youtube_api import YouTubeAPIClient, YouTubeAPIError, VideoNotFoundError, QuotaExceededError
    from scraper.data_validator import DataValidator
    from utils.config import ConfigManager
    from utils.logger import LoggerMixin
    from utils.helpers import extract_video_id, sanitize_filename, format_timestamp, create_safe_directory
    from analysis.sentiment_analyzer import SentimentAnalyzer
    from utils.logger import LoggerMixin
    from utils.helpers import extract_video_id, sanitize_filename, format_timestamp, create_safe_directory


class CommentExtractor(LoggerMixin):
    """
    High-level interface for extracting YouTube comments.
    
    This class coordinates the API client, data validation, and storage
    to provide a simple interface for comment extraction.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the comment extractor.
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__()
        
        # Initialize configuration
        self.config = config_manager or ConfigManager()
        self.config.validate_required_config()
        self.config.create_directories()
        
        # Initialize components
        self.api_client = YouTubeAPIClient(self.config)
        self.validator = DataValidator(self.config)
        
        # Initialize sentiment analyzer (Phase 2)
        try:
            self.sentiment_analyzer = SentimentAnalyzer()
            self.sentiment_enabled = True
            self.logger.info("Sentiment analyzer initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize sentiment analyzer: {str(e)}")
            self.sentiment_analyzer = None
            self.sentiment_enabled = False
        
        # Storage configuration
        storage_config = self.config.get_storage_config()
        self.database_path = storage_config.get('database_path', 'data/comments.db')
        self.raw_data_path = storage_config.get('raw_data_path', 'data/raw')
        self.processed_data_path = storage_config.get('processed_data_path', 'data/processed')
        self.exports_path = storage_config.get('exports_path', 'data/exports')
        
        # Export configuration
        export_config = self.config.get('export', {})
        self.csv_encoding = export_config.get('csv_encoding', 'utf-8')
        self.include_metadata = export_config.get('include_metadata', True)
        self.timestamp_format = export_config.get('timestamp_format', '%Y-%m-%d %H:%M:%S')
        
        # Initialize database
        self._init_database()
        self._migrate_database()
    
    def _init_database(self) -> None:
        """Initialize the SQLite database for storing comments."""
        try:
            # Create database directory if it doesn't exist
            db_path = Path(self.database_path)
            create_safe_directory(str(db_path.parent))
            
            # Create database tables
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Videos table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    video_id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    channel_id TEXT,
                    channel_title TEXT,
                    published_at TEXT,
                    duration TEXT,
                    view_count INTEGER,
                    like_count INTEGER,
                    comment_count INTEGER,
                    thumbnail_url TEXT,
                    tags TEXT,
                    category_id TEXT,
                    default_language TEXT,
                    default_audio_language TEXT,
                    extracted_at TEXT,
                    total_comments_extracted INTEGER
                )
            ''')
            
            # Comments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    comment_id TEXT PRIMARY KEY,
                    video_id TEXT,
                    text TEXT,
                    text_original TEXT,
                    author_display_name TEXT,
                    author_profile_image_url TEXT,
                    author_channel_url TEXT,
                    author_channel_id TEXT,
                    like_count INTEGER,
                    published_at TEXT,
                    updated_at TEXT,
                    is_reply BOOLEAN,
                    parent_id TEXT,
                    total_reply_count INTEGER,
                    extracted_at TEXT,
                    is_valid BOOLEAN,
                    FOREIGN KEY (video_id) REFERENCES videos (video_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Database initialized at: {self.database_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {str(e)}")
            raise RuntimeError(f"Database initialization failed: {str(e)}")
    
    def _migrate_database(self) -> None:
        """Migrate database schema to add sentiment analysis columns."""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Check if sentiment columns already exist
            cursor.execute("PRAGMA table_info(comments)")
            columns = [column[1] for column in cursor.fetchall()]
            
            sentiment_columns = [
                'sentiment_polarity', 'sentiment_subjectivity', 'vader_compound',
                'vader_positive', 'vader_negative', 'vader_neutral',
                'sentiment_label', 'emotion_strength', 'is_subjective', 'sentiment_analyzed_at'
            ]
            
            # Add missing sentiment columns
            for column in sentiment_columns:
                if column not in columns:
                    if column in ['sentiment_polarity', 'sentiment_subjectivity', 'vader_compound', 
                                'vader_positive', 'vader_negative', 'vader_neutral']:
                        cursor.execute(f'ALTER TABLE comments ADD COLUMN {column} REAL')
                    elif column in ['sentiment_label', 'emotion_strength', 'sentiment_analyzed_at']:
                        cursor.execute(f'ALTER TABLE comments ADD COLUMN {column} TEXT')
                    elif column == 'is_subjective':
                        cursor.execute(f'ALTER TABLE comments ADD COLUMN {column} BOOLEAN')
                    
                    self.logger.info(f"Added sentiment column: {column}")
            
            conn.commit()
            conn.close()
            
            self.logger.info("Database migration completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to migrate database: {str(e)}")
            # Don't raise error here - sentiment analysis is optional
    
    def extract_comments(
        self,
        video_url_or_id: str,
        max_comments: Optional[int] = None,
        order: str = "relevance",
        save_to_db: bool = True,
        export_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract comments from a YouTube video.
        
        Args:
            video_url_or_id: YouTube video URL or ID
            max_comments: Maximum number of comments to extract
            order: Comment ordering ('relevance' or 'time')
            save_to_db: Whether to save to database
            export_format: Export format ('csv', 'json', or None)
            
        Returns:
            Dictionary containing extraction results
            
        Raises:
            ValueError: If invalid video URL/ID
            YouTubeAPIError: If API request fails
            VideoNotFoundError: If video not found
        """
        # Extract video ID
        video_id = extract_video_id(video_url_or_id)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL or video ID: {video_url_or_id}")
        
        self.logger.info(f"Starting comment extraction for video: {video_id}")
        
        try:
            # Get video information
            self.logger.info("Fetching video information...")
            video_info = self.api_client.get_video_info(video_id)
            
            # Extract comments
            self.logger.info("Extracting comments...")
            comments = []
            valid_comments = 0
            invalid_comments = 0
            
            for comment_data in self.api_client.get_comments(
                video_id=video_id,
                max_results=max_comments,
                order=order
            ):
                # Validate comment
                if self.validator.is_valid_comment(comment_data):
                    comment_data['is_valid'] = True
                    comment_data['extracted_at'] = datetime.utcnow().isoformat()
                    
                    # Add sentiment analysis (Phase 2)
                    if self.sentiment_enabled:
                        try:
                            sentiment_result = self.sentiment_analyzer.analyze_comment(comment_data['text'])
                            
                            # Add sentiment data to comment
                            comment_data['sentiment_polarity'] = sentiment_result.polarity
                            comment_data['sentiment_subjectivity'] = sentiment_result.subjectivity
                            comment_data['vader_compound'] = sentiment_result.vader_compound
                            comment_data['vader_positive'] = sentiment_result.vader_positive
                            comment_data['vader_negative'] = sentiment_result.vader_negative
                            comment_data['vader_neutral'] = sentiment_result.vader_neutral
                            comment_data['sentiment_label'] = sentiment_result.sentiment_label
                            comment_data['emotion_strength'] = sentiment_result.emotion_strength
                            comment_data['is_subjective'] = sentiment_result.is_subjective
                            comment_data['sentiment_analyzed_at'] = sentiment_result.analyzed_at.isoformat()
                            
                            self.logger.debug(f"Sentiment analyzed for comment {comment_data['comment_id']}: {sentiment_result.sentiment_label}")
                        except Exception as e:
                            self.logger.warning(f"Failed to analyze sentiment for comment {comment_data['comment_id']}: {str(e)}")
                            # Set default values if sentiment analysis fails
                            comment_data.update({
                                'sentiment_polarity': None,
                                'sentiment_subjectivity': None,
                                'vader_compound': None,
                                'vader_positive': None,
                                'vader_negative': None,
                                'vader_neutral': None,
                                'sentiment_label': None,
                                'emotion_strength': None,
                                'is_subjective': None,
                                'sentiment_analyzed_at': None
                            })
                    
                    comments.append(comment_data)
                    valid_comments += 1
                else:
                    invalid_comments += 1
                    self.logger.debug(f"Invalid comment filtered out: {comment_data.get('comment_id', 'unknown')}")
            
            # Update video info with extraction metadata
            video_info['extracted_at'] = datetime.utcnow().isoformat()
            video_info['total_comments_extracted'] = len(comments)
            
            # Save to database if requested
            if save_to_db:
                self._save_to_database(video_info, comments)
            
            # Export if requested
            exported_file = None
            if export_format:
                exported_file = self._export_data(video_info, comments, export_format)
            
            # Prepare results
            results = {
                'video_info': video_info,
                'comments': comments,
                'statistics': {
                    'total_comments_extracted': len(comments),
                    'valid_comments': valid_comments,
                    'invalid_comments': invalid_comments,
                    'extraction_time': video_info['extracted_at'],
                    'video_title': video_info['title'],
                    'channel_title': video_info['channel_title']
                }
            }
            
            if exported_file:
                results['exported_file'] = exported_file
            
            self.logger.info(f"Comment extraction completed successfully. "
                           f"Extracted {len(comments)} valid comments")
            
            return results
            
        except (YouTubeAPIError, VideoNotFoundError, QuotaExceededError) as e:
            self.logger.error(f"API error during extraction: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during extraction: {str(e)}")
            raise RuntimeError(f"Comment extraction failed: {str(e)}")
    
    def _save_to_database(self, video_info: Dict[str, Any], comments: List[Dict[str, Any]]) -> None:
        """
        Save video information and comments to the database.
        
        Args:
            video_info: Video metadata
            comments: List of comment data
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Save video information
            cursor.execute('''
                INSERT OR REPLACE INTO videos (
                    video_id, title, description, channel_id, channel_title,
                    published_at, duration, view_count, like_count, comment_count,
                    thumbnail_url, tags, category_id, default_language,
                    default_audio_language, extracted_at, total_comments_extracted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_info['video_id'],
                video_info['title'],
                video_info['description'],
                video_info['channel_id'],
                video_info['channel_title'],
                video_info['published_at'],
                video_info['duration'],
                video_info['view_count'],
                video_info['like_count'],
                video_info['comment_count'],
                video_info['thumbnail_url'],
                json.dumps(video_info['tags']),
                video_info['category_id'],
                video_info['default_language'],
                video_info['default_audio_language'],
                video_info['extracted_at'],
                video_info['total_comments_extracted']
            ))
            
            # Save comments
            for comment in comments:
                cursor.execute('''
                    INSERT OR REPLACE INTO comments (
                        comment_id, video_id, text, text_original, author_display_name,
                        author_profile_image_url, author_channel_url, author_channel_id,
                        like_count, published_at, updated_at, is_reply, parent_id,
                        total_reply_count, extracted_at, is_valid,
                        sentiment_polarity, sentiment_subjectivity, vader_compound,
                        vader_positive, vader_negative, vader_neutral,
                        sentiment_label, emotion_strength, is_subjective, sentiment_analyzed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    comment['comment_id'],
                    comment['video_id'],
                    comment['text'],
                    comment['text_original'],
                    comment['author_display_name'],
                    comment['author_profile_image_url'],
                    comment['author_channel_url'],
                    comment['author_channel_id'],
                    comment['like_count'],
                    comment['published_at'],
                    comment['updated_at'],
                    comment['is_reply'],
                    comment['parent_id'],
                    comment['total_reply_count'],
                    comment['extracted_at'],
                    comment['is_valid'],
                    # Sentiment analysis data
                    comment.get('sentiment_polarity'),
                    comment.get('sentiment_subjectivity'),
                    comment.get('vader_compound'),
                    comment.get('vader_positive'),
                    comment.get('vader_negative'),
                    comment.get('vader_neutral'),
                    comment.get('sentiment_label'),
                    comment.get('emotion_strength'),
                    comment.get('is_subjective'),
                    comment.get('sentiment_analyzed_at')
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Saved {len(comments)} comments to database")
            
        except Exception as e:
            self.logger.error(f"Failed to save to database: {str(e)}")
            raise
    
    def _export_data(
        self,
        video_info: Dict[str, Any],
        comments: List[Dict[str, Any]],
        format_type: str
    ) -> str:
        """
        Export data to specified format.
        
        Args:
            video_info: Video metadata
            comments: Comment data
            format_type: Export format ('csv' or 'json')
            
        Returns:
            Path to exported file
        """
        # Create safe filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = sanitize_filename(video_info['title'])
        video_id = video_info['video_id']
        
        if format_type.lower() == 'csv':
            filename = f"{video_id}_{safe_title}_{timestamp}.csv"
            filepath = Path(self.exports_path) / filename
            
            # Ensure export directory exists
            create_safe_directory(self.exports_path)
            
            # Export to CSV
            with open(filepath, 'w', newline='', encoding=self.csv_encoding) as csvfile:
                if comments:
                    fieldnames = list(comments[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(comments)
            
            self.logger.info(f"Exported to CSV: {filepath}")
            
        elif format_type.lower() == 'json':
            filename = f"{video_id}_{safe_title}_{timestamp}.json"
            filepath = Path(self.exports_path) / filename
            
            # Ensure export directory exists
            create_safe_directory(self.exports_path)
            
            # Prepare export data
            export_data = {
                'video_info': video_info,
                'comments': comments,
                'export_metadata': {
                    'exported_at': datetime.utcnow().isoformat(),
                    'total_comments': len(comments),
                    'export_format': 'json'
                }
            }
            
            # Export to JSON
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported to JSON: {filepath}")
            
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
        
        return str(filepath)
    
    def get_video_from_database(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get video information from the database.
        
        Args:
            video_id: Video ID to retrieve
            
        Returns:
            Video information or None if not found
        """
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM videos WHERE video_id = ?', (video_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve video from database: {str(e)}")
            return None
    
    def get_comments_from_database(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get comments for a video from the database.
        
        Args:
            video_id: Video ID to retrieve comments for
            
        Returns:
            List of comment dictionaries
        """
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT * FROM comments WHERE video_id = ? ORDER BY published_at DESC',
                (video_id,)
            )
            rows = cursor.fetchall()
            
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve comments from database: {str(e)}")
            return []
    
    def list_extracted_videos(self) -> List[Dict[str, Any]]:
        """
        List all videos that have been processed.
        
        Returns:
            List of video summaries
        """
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT video_id, title, channel_title, extracted_at, 
                       total_comments_extracted, view_count
                FROM videos 
                ORDER BY extracted_at DESC
            ''')
            rows = cursor.fetchall()
            
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to list extracted videos: {str(e)}")
            return []
