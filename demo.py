"""
Demo script to test the YouTube Comment Scraper functionality.

This script demonstrates the basic usage without requiring a real API key.
"""

import sys
from pathlib import Path
import tempfile
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.helpers import extract_video_id, validate_youtube_url, sanitize_filename
from src.utils.config import ConfigManager
from src.utils.logger import setup_logger
from src.scraper.data_validator import DataValidator


def test_url_extraction():
    """Test URL extraction functionality."""
    print("Testing URL extraction...")
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ", 
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "dQw4w9WgXcQ",
        "invalid_url"
    ]
    
    for url in test_urls:
        video_id = extract_video_id(url)
        is_valid = validate_youtube_url(url)
        print(f"  URL: {url}")
        print(f"    Video ID: {video_id}")
        print(f"    Valid: {is_valid}")
        print()


def test_config_system():
    """Test configuration system."""
    print("Testing configuration system...")
    
    # Create a temporary config for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        test_config = """
youtube:
  api_key: "test_key_123"
  max_results_per_request: 50
  max_total_comments: 500

storage:
  database_path: "data/test_comments.db"
  raw_data_path: "data/raw"
  
logging:
  level: "INFO"
  log_file: "logs/test.log"

filters:
  min_comment_length: 5
  max_comment_length: 1000
  exclude_spam: true
"""
        f.write(test_config)
        config_path = f.name
    
    try:
        # Test configuration loading
        config = ConfigManager(config_path)
        
        print("  Configuration loaded successfully")
        print(f"    API Key: {config.get('youtube.api_key')}")
        print(f"    Max Results: {config.get('youtube.max_results_per_request')}")
        print(f"    Database Path: {config.get('storage.database_path')}")
        print(f"    Log Level: {config.get('logging.level')}")
        
        # Test setting values
        config.set('test.new_value', 'hello_world')
        print(f"    New Value: {config.get('test.new_value')}")
        
    finally:
        # Clean up
        Path(config_path).unlink()


def test_data_validation():
    """Test data validation functionality."""
    print("Testing data validation...")
    
    # Create test comments
    test_comments = [
        {
            'comment_id': 'comment_1',
            'video_id': 'dQw4w9WgXcQ',
            'text': 'This is a great video! Thanks for sharing.',
            'text_original': 'This is a great video! Thanks for sharing.',
            'author_display_name': 'TestUser1',
            'author_channel_id': 'channel_123',
            'like_count': 5,
            'published_at': '2023-01-01T12:00:00Z',
            'updated_at': '2023-01-01T12:00:00Z',
            'is_reply': False,
            'parent_id': '',
            'total_reply_count': 0
        },
        {
            'comment_id': 'comment_2',
            'video_id': 'dQw4w9WgXcQ',
            'text': 'SPAM SPAM SPAM CLICK HERE FOR FREE MONEY!!!',
            'text_original': 'SPAM SPAM SPAM CLICK HERE FOR FREE MONEY!!!',
            'author_display_name': 'SpamBot',
            'author_channel_id': 'spam_channel',
            'like_count': 0,
            'published_at': '2023-01-01T12:00:00Z',
            'updated_at': '2023-01-01T12:00:00Z',
            'is_reply': False,
            'parent_id': '',
            'total_reply_count': 0
        },
        {
            'comment_id': 'comment_3',
            'video_id': 'dQw4w9WgXcQ',
            'text': 'a',  # Too short
            'text_original': 'a',
            'author_display_name': 'ShortComment',
            'author_channel_id': 'short_channel',
            'like_count': 1,
            'published_at': '2023-01-01T12:00:00Z',
            'updated_at': '2023-01-01T12:00:00Z',
            'is_reply': False,
            'parent_id': '',
            'total_reply_count': 0
        },
        {
            # Missing required fields
            'comment_id': 'comment_4',
            'text': 'This comment is missing required fields',
        }
    ]
    
    # Create a temporary config for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        test_config = """
filters:
  min_comment_length: 5
  max_comment_length: 1000
  exclude_spam: true
  languages: []
"""
        f.write(test_config)
        config_path = f.name
    
    try:
        config = ConfigManager(config_path)
        validator = DataValidator(config)
        
        print("  Validating test comments:")
        for i, comment in enumerate(test_comments, 1):
            is_valid = validator.is_valid_comment(comment)
            text_preview = comment.get('text', 'No text')[:30] + "..."
            print(f"    Comment {i}: {'VALID' if is_valid else 'INVALID'} - {text_preview}")
        
        # Get validation statistics
        stats = validator.get_validation_stats(test_comments)
        print(f"\n  Validation Statistics:")
        print(f"    Total: {stats['total_comments']}")
        print(f"    Valid: {stats['valid_comments']}")
        print(f"    Invalid: {stats['invalid_comments']}")
        print(f"    Spam: {stats['spam_comments']}")
        print(f"    Length violations: {stats['length_violations']}")
        print(f"    Missing fields: {stats['missing_fields']}")
        
    finally:
        Path(config_path).unlink()


def test_logging_system():
    """Test logging system."""
    print("Testing logging system...")
    
    # Create temporary config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        test_config = """
logging:
  level: "INFO"
  log_file: "logs/test_demo.log"
  max_log_size_mb: 5
  backup_count: 3
"""
        f.write(test_config)
        config_path = f.name
    
    try:
        config = ConfigManager(config_path)
        logger = setup_logger("demo_test", config)
        
        print("  Logger created successfully")
        
        # Test different log levels
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        
        print("  Log messages sent successfully")
        
    finally:
        Path(config_path).unlink()


def test_filename_sanitization():
    """Test filename sanitization."""
    print("Testing filename sanitization...")
    
    test_filenames = [
        "Normal Video Title",
        "Video with <invalid> characters: test?",
        "Video/with\\path|chars*.txt",
        "  Spaces at beginning and end  ",
        "Very long title that exceeds normal filename length limits and should be truncated properly"
    ]
    
    for filename in test_filenames:
        sanitized = sanitize_filename(filename)
        print(f"  Original: {filename}")
        print(f"  Sanitized: {sanitized}")
        print()


def main():
    """Run all demo tests."""
    print("YouTube Comment Scraper - Demo Tests")
    print("=" * 50)
    print()
    
    try:
        test_url_extraction()
        print()
        
        test_config_system()
        print()
        
        test_data_validation()
        print()
        
        test_logging_system()
        print()
        
        test_filename_sanitization()
        print()
        
        print("=" * 50)
        print("All demo tests completed successfully!")
        print()
        print("To use the scraper with a real YouTube video, you need to:")
        print("1. Get a YouTube Data API v3 key from Google Cloud Console")
        print("2. Update the api_key in config.yaml")
        print("3. Run: python src/main.py <youtube_url>")
        print()
        print("Example:")
        print("  python src/main.py https://www.youtube.com/watch?v=dQw4w9WgXcQ --max-comments 100 --export csv")
        
    except Exception as e:
        print(f"Demo test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
