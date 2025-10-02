"""
Data validation utilities for the YouTube Comment Scraper.

This module provides functions for validating and cleaning comment data
before storage and analysis.
"""

import re
from typing import Dict, Any, List, Optional

# Handle imports for both package and direct execution
try:
    from ..utils.config import ConfigManager
    from ..utils.logger import LoggerMixin
    from ..utils.helpers import normalize_text
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.config import ConfigManager
    from utils.logger import LoggerMixin
    from utils.helpers import normalize_text


class DataValidator(LoggerMixin):
    """
    Validator for comment data with configurable filtering rules.
    
    This class provides methods to validate comments based on length,
    language, content quality, and other criteria.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the data validator.
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__()
        
        # Initialize configuration
        self.config = config_manager or ConfigManager()
        filter_config = self.config.get('filters', {})
        
        # Validation criteria
        self.min_comment_length = filter_config.get('min_comment_length', 1)
        self.max_comment_length = filter_config.get('max_comment_length', 10000)
        self.exclude_spam = filter_config.get('exclude_spam', True)
        self.allowed_languages = filter_config.get('languages', [])
        
        # Spam detection patterns
        self._init_spam_patterns()
        
        # Language detection (basic patterns for now)
        self._init_language_patterns()
    
    def _init_spam_patterns(self) -> None:
        """Initialize patterns for spam detection."""
        self.spam_patterns = [
            # Excessive repetition
            r'(.)\1{10,}',  # Same character repeated 10+ times
            r'(\w+\s+)\1{5,}',  # Same word repeated 5+ times
            
            # Common spam indicators
            r'(?i)(click\s+here|visit\s+my\s+channel|subscribe\s+to\s+me)',
            r'(?i)(free\s+money|make\s+money|earn\s+\$\d+)',
            r'(?i)(buy\s+now|limited\s+time|act\s+fast)',
            
            # Excessive punctuation/emojis
            r'[!?]{5,}',  # Multiple exclamation/question marks
            r'[\U0001F600-\U0001F64F]{5,}',  # Multiple emoji
            
            # URLs (potential spam)
            r'https?://\S+',
            r'www\.\S+\.\S+',
            
            # Excessive uppercase
            r'^[A-Z\s!?]{20,}$',  # All caps messages
        ]
        
        # Compile patterns for efficiency
        self.compiled_spam_patterns = [re.compile(pattern) for pattern in self.spam_patterns]
    
    def _init_language_patterns(self) -> None:
        """Initialize basic language detection patterns."""
        # Simple language detection based on character sets
        self.language_patterns = {
            'en': r'[a-zA-Z]',  # English characters
            'es': r'[a-zA-ZñáéíóúüÑÁÉÍÓÚÜ]',  # Spanish characters
            'fr': r'[a-zA-ZàâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]',  # French characters
            'de': r'[a-zA-ZäöüßÄÖÜ]',  # German characters
            'it': r'[a-zA-ZàèéìíîòóùúÀÈÉÌÍÎÒÓÙÚ]',  # Italian characters
            'pt': r'[a-zA-ZàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ]',  # Portuguese characters
            'ru': r'[а-яёА-ЯЁ]',  # Russian characters
            'zh': r'[\u4e00-\u9fff]',  # Chinese characters
            'ja': r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]',  # Japanese characters
            'ko': r'[\uac00-\ud7af]',  # Korean characters
            'ar': r'[\u0600-\u06ff]',  # Arabic characters
            'hi': r'[\u0900-\u097f]',  # Hindi characters
        }
        
        # Compile patterns
        self.compiled_language_patterns = {
            lang: re.compile(pattern) for lang, pattern in self.language_patterns.items()
        }
    
    def is_valid_comment(self, comment_data: Dict[str, Any]) -> bool:
        """
        Validate a comment based on all configured criteria.
        
        Args:
            comment_data: Comment data dictionary
            
        Returns:
            True if comment is valid, False otherwise
        """
        try:
            # Check if comment has required fields
            if not self._has_required_fields(comment_data):
                self.logger.debug(f"Comment missing required fields: {comment_data.get('comment_id', 'unknown')}")
                return False
            
            # Extract and normalize text
            text = comment_data.get('text', '') or comment_data.get('text_original', '')
            if not text:
                self.logger.debug(f"Comment has no text: {comment_data.get('comment_id', 'unknown')}")
                return False
            
            normalized_text = normalize_text(text)
            
            # Length validation
            if not self._is_valid_length(normalized_text):
                self.logger.debug(f"Comment length invalid: {comment_data.get('comment_id', 'unknown')}")
                return False
            
            # Spam detection
            if self.exclude_spam and self._is_spam(normalized_text):
                self.logger.debug(f"Comment detected as spam: {comment_data.get('comment_id', 'unknown')}")
                return False
            
            # Language validation
            if self.allowed_languages and not self._is_allowed_language(normalized_text):
                self.logger.debug(f"Comment language not allowed: {comment_data.get('comment_id', 'unknown')}")
                return False
            
            # Content quality validation
            if not self._is_quality_content(normalized_text):
                self.logger.debug(f"Comment quality too low: {comment_data.get('comment_id', 'unknown')}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating comment: {str(e)}")
            return False
    
    def _has_required_fields(self, comment_data: Dict[str, Any]) -> bool:
        """
        Check if comment has all required fields.
        
        Args:
            comment_data: Comment data dictionary
            
        Returns:
            True if all required fields are present
        """
        required_fields = [
            'comment_id',
            'video_id',
            'author_display_name',
            'published_at'
        ]
        
        for field in required_fields:
            if field not in comment_data or comment_data[field] is None:
                return False
        
        # Must have either text or text_original
        if not (comment_data.get('text') or comment_data.get('text_original')):
            return False
        
        return True
    
    def _is_valid_length(self, text: str) -> bool:
        """
        Check if comment length is within acceptable range.
        
        Args:
            text: Comment text
            
        Returns:
            True if length is valid
        """
        text_length = len(text.strip())
        return self.min_comment_length <= text_length <= self.max_comment_length
    
    def _is_spam(self, text: str) -> bool:
        """
        Detect if comment is likely spam.
        
        Args:
            text: Comment text
            
        Returns:
            True if likely spam
        """
        # Check against spam patterns
        for pattern in self.compiled_spam_patterns:
            if pattern.search(text):
                return True
        
        # Additional spam indicators
        
        # Check for excessive special characters
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(len(text), 1)
        if special_char_ratio > 0.5:  # More than 50% special characters
            return True
        
        # Check for excessive numeric content
        numeric_ratio = sum(1 for c in text if c.isdigit()) / max(len(text), 1)
        if numeric_ratio > 0.7:  # More than 70% numbers
            return True
        
        # Check for very short repetitive content
        words = text.split()
        if len(words) >= 3:
            unique_words = set(words)
            repetition_ratio = 1 - (len(unique_words) / len(words))
            if repetition_ratio > 0.8:  # More than 80% repeated words
                return True
        
        return False
    
    def _is_allowed_language(self, text: str) -> bool:
        """
        Check if comment is in an allowed language.
        
        Args:
            text: Comment text
            
        Returns:
            True if language is allowed (or no language restrictions)
        """
        if not self.allowed_languages:
            return True  # No language restrictions
        
        # Simple language detection based on character patterns
        detected_languages = []
        
        for lang_code, pattern in self.compiled_language_patterns.items():
            matches = pattern.findall(text)
            if matches:
                # Calculate ratio of language-specific characters
                lang_char_count = len(''.join(matches))
                total_chars = len(re.sub(r'\s+', '', text))  # Non-whitespace chars
                
                if total_chars > 0:
                    ratio = lang_char_count / total_chars
                    if ratio > 0.3:  # At least 30% of chars match this language
                        detected_languages.append(lang_code)
        
        # If no language detected, assume it's allowed (could be emoji-only, etc.)
        if not detected_languages:
            return True
        
        # Check if any detected language is in allowed list
        return any(lang in self.allowed_languages for lang in detected_languages)
    
    def _is_quality_content(self, text: str) -> bool:
        """
        Check if comment meets basic quality standards.
        
        Args:
            text: Comment text
            
        Returns:
            True if quality is acceptable
        """
        # Remove whitespace for analysis
        clean_text = text.strip()
        
        # Check for minimum word count (not just characters)
        words = clean_text.split()
        if len(words) < 1:
            return False
        
        # Check for excessive repetition of single character
        for char in set(clean_text):
            if char.isalnum():  # Only check alphanumeric characters
                char_count = clean_text.count(char)
                if char_count > len(clean_text) * 0.6:  # More than 60% same character
                    return False
        
        # Check for reasonable word length distribution
        if len(words) >= 3:
            avg_word_length = sum(len(word) for word in words) / len(words)
            if avg_word_length < 1.5 or avg_word_length > 20:  # Unrealistic averages
                return False
        
        # Check for excessive punctuation
        punctuation_count = sum(1 for c in clean_text if c in '!?.,;:')
        if punctuation_count > len(clean_text) * 0.3:  # More than 30% punctuation
            return False
        
        return True
    
    def clean_comment_text(self, text: str) -> str:
        """
        Clean and normalize comment text.
        
        Args:
            text: Raw comment text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Normalize the text
        cleaned = normalize_text(text)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove excessive punctuation (keep max 3 consecutive)
        cleaned = re.sub(r'([!?.]){4,}', r'\1\1\1', cleaned)
        
        # Remove zero-width characters
        cleaned = re.sub(r'[\u200b-\u200f\u2060\ufeff]', '', cleaned)
        
        return cleaned.strip()
    
    def get_validation_stats(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get validation statistics for a list of comments.
        
        Args:
            comments: List of comment dictionaries
            
        Returns:
            Dictionary with validation statistics
        """
        stats = {
            'total_comments': len(comments),
            'valid_comments': 0,
            'invalid_comments': 0,
            'spam_comments': 0,
            'length_violations': 0,
            'language_violations': 0,
            'quality_violations': 0,
            'missing_fields': 0
        }
        
        for comment in comments:
            if self.is_valid_comment(comment):
                stats['valid_comments'] += 1
            else:
                stats['invalid_comments'] += 1
                
                # Count specific violation types
                text = comment.get('text', '') or comment.get('text_original', '')
                normalized_text = normalize_text(text) if text else ''
                
                if not self._has_required_fields(comment):
                    stats['missing_fields'] += 1
                elif normalized_text and not self._is_valid_length(normalized_text):
                    stats['length_violations'] += 1
                elif normalized_text and self.exclude_spam and self._is_spam(normalized_text):
                    stats['spam_comments'] += 1
                elif normalized_text and self.allowed_languages and not self._is_allowed_language(normalized_text):
                    stats['language_violations'] += 1
                elif normalized_text and not self._is_quality_content(normalized_text):
                    stats['quality_violations'] += 1
        
        # Calculate percentages
        if stats['total_comments'] > 0:
            stats['valid_percentage'] = (stats['valid_comments'] / stats['total_comments']) * 100
            stats['invalid_percentage'] = (stats['invalid_comments'] / stats['total_comments']) * 100
        else:
            stats['valid_percentage'] = 0
            stats['invalid_percentage'] = 0
        
        return stats
