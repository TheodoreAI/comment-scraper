"""
YouTube Comment Scraper & Sentiment Analysis Tool

A comprehensive Python package for extracting YouTube comments,
analyzing sentiment, and generating visualizations.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from src.scraper.comment_extractor import CommentExtractor
from src.utils.config import ConfigManager
from src.utils.logger import setup_logger

__all__ = [
    "CommentExtractor",
    "ConfigManager", 
    "setup_logger"
]
