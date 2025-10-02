"""
Analysis module for YouTube Comment Scraper.

This module provides sentiment analysis and emotional insights
for YouTube comments using advanced NLP techniques.
"""

from .sentiment_analyzer import (
    SentimentAnalyzer,
    SentimentResult,
    analyze_single_comment,
    analyze_comment_list
)

__all__ = [
    'SentimentAnalyzer',
    'SentimentResult', 
    'analyze_single_comment',
    'analyze_comment_list'
]
