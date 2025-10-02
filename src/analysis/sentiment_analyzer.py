"""
Sentiment Analysis Module for YouTube Comment Scraper.

This module provides comprehensive sentiment analysis capabilities using both
TextBlob and VADER sentiment analyzers to extract emotional insights from
YouTube comments.

Features:
- TextBlob for general sentiment polarity and subjectivity
- VADER for social media-optimized sentiment analysis
- Emotion detection and classification
- Sentiment strength scoring
- Batch processing for multiple comments
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Container for sentiment analysis results."""
    
    # TextBlob results
    polarity: float  # -1 (negative) to 1 (positive)
    subjectivity: float  # 0 (objective) to 1 (subjective)
    
    # VADER results
    vader_compound: float  # -1 (negative) to 1 (positive)
    vader_positive: float  # 0 to 1
    vader_negative: float  # 0 to 1
    vader_neutral: float  # 0 to 1
    
    # Derived insights
    sentiment_label: str  # "positive", "negative", "neutral"
    emotion_strength: str  # "weak", "moderate", "strong"
    is_subjective: bool  # True if subjectivity > 0.5
    
    # Metadata
    analyzed_at: datetime
    text_length: int


class SentimentAnalyzer:
    """
    Advanced sentiment analysis using both TextBlob and VADER.
    
    This class provides comprehensive sentiment analysis capabilities specifically
    designed for social media content like YouTube comments.
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer."""
        self.vader_analyzer = SentimentIntensityAnalyzer()
        logger.info("Sentiment analyzer initialized with TextBlob and VADER")
    
    def analyze_comment(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of a single comment.
        
        Args:
            text: The comment text to analyze
            
        Returns:
            SentimentResult with comprehensive sentiment metrics
            
        Examples:
            >>> analyzer = SentimentAnalyzer()
            >>> result = analyzer.analyze_comment("I love this video!")
            >>> print(f"Sentiment: {result.sentiment_label}")
            'Sentiment: positive'
        """
        if not text or not isinstance(text, str):
            logger.warning("Invalid text provided for sentiment analysis")
            return self._create_empty_result()
        
        # Clean the text
        cleaned_text = self._preprocess_text(text)
        
        try:
            # TextBlob analysis
            blob = TextBlob(cleaned_text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # VADER analysis
            vader_scores = self.vader_analyzer.polarity_scores(cleaned_text)
            
            # Derive insights
            sentiment_label = self._determine_sentiment_label(polarity, vader_scores['compound'])
            emotion_strength = self._determine_emotion_strength(polarity, vader_scores['compound'])
            is_subjective = subjectivity > 0.5
            
            result = SentimentResult(
                # TextBlob
                polarity=polarity,
                subjectivity=subjectivity,
                
                # VADER
                vader_compound=vader_scores['compound'],
                vader_positive=vader_scores['pos'],
                vader_negative=vader_scores['neg'],
                vader_neutral=vader_scores['neu'],
                
                # Insights
                sentiment_label=sentiment_label,
                emotion_strength=emotion_strength,
                is_subjective=is_subjective,
                
                # Metadata
                analyzed_at=datetime.now(),
                text_length=len(text)
            )
            
            logger.debug(f"Analyzed comment sentiment: {sentiment_label} ({polarity:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return self._create_empty_result()
    
    def analyze_batch(self, comments: List[str]) -> List[SentimentResult]:
        """
        Analyze sentiment for multiple comments in batch.
        
        Args:
            comments: List of comment texts to analyze
            
        Returns:
            List of SentimentResult objects
        """
        logger.info(f"Starting batch sentiment analysis for {len(comments)} comments")
        
        results = []
        for i, comment in enumerate(comments):
            result = self.analyze_comment(comment)
            results.append(result)
            
            # Log progress for large batches
            if (i + 1) % 50 == 0:
                logger.info(f"Processed {i + 1}/{len(comments)} comments")
        
        logger.info(f"Completed batch sentiment analysis for {len(comments)} comments")
        return results
    
    def get_sentiment_summary(self, results: List[SentimentResult]) -> Dict[str, Any]:
        """
        Generate summary statistics from sentiment analysis results.
        
        Args:
            results: List of SentimentResult objects
            
        Returns:
            Dictionary with sentiment statistics and insights
        """
        if not results:
            return {}
        
        # Count sentiment labels
        sentiment_counts = {
            'positive': sum(1 for r in results if r.sentiment_label == 'positive'),
            'negative': sum(1 for r in results if r.sentiment_label == 'negative'),
            'neutral': sum(1 for r in results if r.sentiment_label == 'neutral')
        }
        
        total = len(results)
        
        # Calculate averages
        avg_polarity = sum(r.polarity for r in results) / total
        avg_subjectivity = sum(r.subjectivity for r in results) / total
        avg_vader_compound = sum(r.vader_compound for r in results) / total
        
        # Emotion strength distribution
        emotion_counts = {
            'weak': sum(1 for r in results if r.emotion_strength == 'weak'),
            'moderate': sum(1 for r in results if r.emotion_strength == 'moderate'),
            'strong': sum(1 for r in results if r.emotion_strength == 'strong')
        }
        
        # Subjectivity analysis
        subjective_count = sum(1 for r in results if r.is_subjective)
        
        summary = {
            'total_comments': total,
            'sentiment_distribution': {
                'positive': {
                    'count': sentiment_counts['positive'],
                    'percentage': (sentiment_counts['positive'] / total) * 100
                },
                'negative': {
                    'count': sentiment_counts['negative'],
                    'percentage': (sentiment_counts['negative'] / total) * 100
                },
                'neutral': {
                    'count': sentiment_counts['neutral'],
                    'percentage': (sentiment_counts['neutral'] / total) * 100
                }
            },
            'average_scores': {
                'polarity': round(avg_polarity, 3),
                'subjectivity': round(avg_subjectivity, 3),
                'vader_compound': round(avg_vader_compound, 3)
            },
            'emotion_strength': {
                'weak': emotion_counts['weak'],
                'moderate': emotion_counts['moderate'],
                'strong': emotion_counts['strong']
            },
            'subjectivity_analysis': {
                'subjective_count': subjective_count,
                'objective_count': total - subjective_count,
                'subjectivity_ratio': round((subjective_count / total) * 100, 1)
            },
            'overall_sentiment': self._determine_overall_sentiment(avg_polarity, avg_vader_compound),
            'generated_at': datetime.now().isoformat()
        }
        
        logger.info(f"Generated sentiment summary for {total} comments")
        return summary
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better sentiment analysis.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Cleaned text ready for analysis
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Handle common patterns that might affect sentiment
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('<br>', ' ')
        text = text.replace('<br/>', ' ')
        
        return text.strip()
    
    def _determine_sentiment_label(self, polarity: float, vader_compound: float) -> str:
        """
        Determine sentiment label based on both TextBlob and VADER scores.
        
        Args:
            polarity: TextBlob polarity score
            vader_compound: VADER compound score
            
        Returns:
            Sentiment label: "positive", "negative", or "neutral"
        """
        # Use average of both methods for more robust classification
        avg_score = (polarity + vader_compound) / 2
        
        if avg_score >= 0.1:
            return 'positive'
        elif avg_score <= -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _determine_emotion_strength(self, polarity: float, vader_compound: float) -> str:
        """
        Determine emotion strength based on sentiment scores.
        
        Args:
            polarity: TextBlob polarity score
            vader_compound: VADER compound score
            
        Returns:
            Emotion strength: "weak", "moderate", or "strong"
        """
        # Use the stronger of the two scores
        max_abs_score = max(abs(polarity), abs(vader_compound))
        
        if max_abs_score >= 0.6:
            return 'strong'
        elif max_abs_score >= 0.3:
            return 'moderate'
        else:
            return 'weak'
    
    def _determine_overall_sentiment(self, avg_polarity: float, avg_vader: float) -> str:
        """
        Determine overall sentiment for a collection of comments.
        
        Args:
            avg_polarity: Average TextBlob polarity
            avg_vader: Average VADER compound score
            
        Returns:
            Overall sentiment description
        """
        avg_score = (avg_polarity + avg_vader) / 2
        
        if avg_score >= 0.3:
            return "strongly positive"
        elif avg_score >= 0.1:
            return "positive"
        elif avg_score >= -0.1:
            return "neutral"
        elif avg_score >= -0.3:
            return "negative"
        else:
            return "strongly negative"
    
    def _create_empty_result(self) -> SentimentResult:
        """Create an empty/default sentiment result for error cases."""
        return SentimentResult(
            polarity=0.0,
            subjectivity=0.0,
            vader_compound=0.0,
            vader_positive=0.0,
            vader_negative=0.0,
            vader_neutral=1.0,
            sentiment_label='neutral',
            emotion_strength='weak',
            is_subjective=False,
            analyzed_at=datetime.now(),
            text_length=0
        )


# Convenience functions for quick analysis
def analyze_single_comment(text: str) -> SentimentResult:
    """Quick analysis of a single comment."""
    analyzer = SentimentAnalyzer()
    return analyzer.analyze_comment(text)


def analyze_comment_list(comments: List[str]) -> List[SentimentResult]:
    """Quick analysis of a list of comments."""
    analyzer = SentimentAnalyzer()
    return analyzer.analyze_batch(comments)


if __name__ == "__main__":
    # Example usage
    analyzer = SentimentAnalyzer()
    
    # Test with sample comments
    test_comments = [
        "I absolutely love this video! Amazing content!",
        "This is terrible. What a waste of time.",
        "It's okay, nothing special but not bad either.",
        "BEST VIDEO EVER!!! 😍😍😍",
        "Meh... could be better"
    ]
    
    print("Sentiment Analysis Examples:")
    print("=" * 50)
    
    for comment in test_comments:
        result = analyzer.analyze_comment(comment)
        print(f"Comment: {comment[:30]}...")
        print(f"Sentiment: {result.sentiment_label} ({result.polarity:.2f})")
        print(f"Strength: {result.emotion_strength}")
        print(f"Subjective: {result.is_subjective}")
        print("-" * 30)
