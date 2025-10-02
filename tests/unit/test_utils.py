"""
Unit tests for the YouTube Comment Scraper utilities.
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for imports
src_path = str(Path(__file__).parent.parent.parent / 'src')
sys.path.insert(0, src_path)

from src.utils.helpers import (
    extract_video_id, 
    validate_youtube_url, 
    is_valid_video_id,
    sanitize_filename,
    normalize_text
)
from src.utils.config import ConfigManager


class TestHelpers(unittest.TestCase):
    """Test helper functions."""
    
    def test_extract_video_id_standard_url(self):
        """Test extracting video ID from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = extract_video_id(url)
        self.assertEqual(result, "dQw4w9WgXcQ")
    
    def test_extract_video_id_short_url(self):
        """Test extracting video ID from short YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = extract_video_id(url)
        self.assertEqual(result, "dQw4w9WgXcQ")
    
    def test_extract_video_id_embed_url(self):
        """Test extracting video ID from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        result = extract_video_id(url)
        self.assertEqual(result, "dQw4w9WgXcQ")
    
    def test_extract_video_id_direct_id(self):
        """Test extracting video ID when input is already an ID."""
        video_id = "dQw4w9WgXcQ"
        result = extract_video_id(video_id)
        self.assertEqual(result, "dQw4w9WgXcQ")
    
    def test_extract_video_id_invalid(self):
        """Test extracting video ID from invalid input."""
        invalid_inputs = [
            "not a url",
            "https://www.example.com",
            "123",
            "",
            None
        ]
        
        for invalid_input in invalid_inputs:
            result = extract_video_id(invalid_input)
            self.assertIsNone(result, f"Should return None for: {invalid_input}")
    
    def test_validate_youtube_url(self):
        """Test YouTube URL validation."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            self.assertTrue(validate_youtube_url(url), f"Should be valid: {url}")
        
        invalid_urls = [
            "not a url",
            "https://www.example.com",
            "123"
        ]
        
        for url in invalid_urls:
            self.assertFalse(validate_youtube_url(url), f"Should be invalid: {url}")
    
    def test_is_valid_video_id(self):
        """Test video ID format validation."""
        valid_ids = [
            "dQw4w9WgXcQ",
            "jNQXAC9IVRw",
            "9bZkp7q19f0"
        ]
        
        for video_id in valid_ids:
            self.assertTrue(is_valid_video_id(video_id), f"Should be valid: {video_id}")
        
        invalid_ids = [
            "short",
            "toolongtobevalid123",
            "invalid@chars",
            "",
            None
        ]
        
        for video_id in invalid_ids:
            self.assertFalse(is_valid_video_id(video_id), f"Should be invalid: {video_id}")
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        test_cases = [
            ("normal_filename.txt", "normal_filename.txt"),
            ("file with spaces.txt", "file with spaces.txt"),
            ("file<with>invalid:chars.txt", "file_with_invalid_chars.txt"),
            ("file/with\\path|chars?.txt", "file_with_path_chars_.txt"),
            ("  leading and trailing spaces  ", "leading and trailing spaces"),
        ]
        
        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            self.assertEqual(result, expected)
    
    def test_normalize_text(self):
        """Test text normalization."""
        test_cases = [
            ("  normal text  ", "normal text"),
            ("text\nwith\nmultiple\nlines", "text with multiple lines"),
            ("text   with    excessive   spaces", "text with excessive spaces"),
            ("", ""),
            (None, "")
        ]
        
        for input_text, expected in test_cases:
            result = normalize_text(input_text)
            self.assertEqual(result, expected)


class TestConfigManager(unittest.TestCase):
    """Test configuration manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
        
        # Create a test config file
        config_content = """
youtube:
  api_key: "test_api_key"
  max_results_per_request: 50

storage:
  database_path: "test_data/comments.db"
  
logging:
  level: "INFO"
"""
        
        with open(self.config_file, 'w') as f:
            f.write(config_content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_config_loading(self):
        """Test configuration loading."""
        config = ConfigManager(self.config_file)
        
        self.assertEqual(config.get('youtube.api_key'), "test_api_key")
        self.assertEqual(config.get('youtube.max_results_per_request'), 50)
        self.assertEqual(config.get('storage.database_path'), "test_data/comments.db")
        self.assertEqual(config.get('logging.level'), "INFO")
    
    def test_config_default_values(self):
        """Test default values for missing config."""
        config = ConfigManager(self.config_file)
        
        # Test non-existent key with default
        result = config.get('non.existent.key', 'default_value')
        self.assertEqual(result, 'default_value')
        
        # Test non-existent key without default
        result = config.get('non.existent.key')
        self.assertIsNone(result)
    
    def test_config_set_and_get(self):
        """Test setting and getting configuration values."""
        config = ConfigManager(self.config_file)
        
        # Set a new value
        config.set('test.new.value', 'test_value')
        result = config.get('test.new.value')
        self.assertEqual(result, 'test_value')


if __name__ == '__main__':
    unittest.main()
