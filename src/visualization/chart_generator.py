"""
Visualization Module for YouTube Comment Scraper.

This module provides comprehensive data visualization capabilities for sentiment
analysis results, including charts, graphs, and word clouds to help users
understand comment sentiment patterns and trends.

Features:
- Sentiment distribution charts (pie charts, bar charts)
- Timeline sentiment analysis
- Word clouds for positive/negative comments
- Interactive visualizations with Plotly
- Export to various formats (PNG, HTML, PDF)
"""

import logging
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from wordcloud import WordCloud
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# Set style preferences
plt.style.use('default')
sns.set_palette("husl")


class ChartGenerator:
    """
    Advanced chart generation for sentiment analysis visualization.
    
    This class provides comprehensive visualization capabilities for YouTube
    comment sentiment analysis results.
    """
    
    def __init__(self, output_dir: str = "data/charts"):
        """
        Initialize the chart generator.
        
        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Chart styling
        self.colors = {
            'positive': '#2ECC71',  # Green
            'negative': '#E74C3C',  # Red
            'neutral': '#95A5A6',   # Gray
            'primary': '#3498DB',   # Blue
            'secondary': '#9B59B6'  # Purple
        }
        
        logger.info(f"Chart generator initialized. Output directory: {self.output_dir}")
    
    def create_sentiment_distribution_chart(
        self,
        sentiment_data: Dict[str, Any],
        video_title: str = "YouTube Video",
        save_path: Optional[str] = None
    ) -> str:
        """
        Create a pie chart showing sentiment distribution.
        
        Args:
            sentiment_data: Dictionary with sentiment statistics
            video_title: Title of the video for the chart
            save_path: Optional custom save path
            
        Returns:
            Path to saved chart
        """
        try:
            # Extract data
            sentiment_dist = sentiment_data.get('sentiment_distribution', {})
            
            labels = []
            sizes = []
            colors = []
            
            for sentiment in ['positive', 'negative', 'neutral']:
                if sentiment in sentiment_dist:
                    count = sentiment_dist[sentiment]['count']
                    if count > 0:  # Only include non-zero values
                        labels.append(f"{sentiment.title()} ({count})")
                        sizes.append(count)
                        colors.append(self.colors[sentiment])
            
            if not sizes:
                logger.warning("No sentiment data to visualize")
                return ""
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 11}
            )
            
            # Style the percentage text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            # Title and formatting
            ax.set_title(f'Sentiment Distribution\n{video_title}', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Add summary statistics
            total = sentiment_data.get('total_comments', 0)
            overall = sentiment_data.get('overall_sentiment', 'neutral')
            avg_polarity = sentiment_data.get('average_scores', {}).get('polarity', 0)
            
            summary_text = f"Total Comments: {total}\nOverall Sentiment: {overall.title()}\nAvg Polarity: {avg_polarity:.2f}"
            ax.text(1.3, 0.5, summary_text, transform=ax.transAxes, fontsize=12,
                   verticalalignment='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            
            plt.tight_layout()
            
            # Save chart
            if not save_path:
                safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '_')).rstrip()[:50]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = self.output_dir / f"sentiment_distribution_{safe_title}_{timestamp}.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Sentiment distribution chart saved: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Failed to create sentiment distribution chart: {str(e)}")
            return ""
    
    def create_sentiment_timeline(
        self,
        comments_df: pd.DataFrame,
        video_title: str = "YouTube Video",
        save_path: Optional[str] = None
    ) -> str:
        """
        Create a timeline chart showing sentiment over time.
        
        Args:
            comments_df: DataFrame with comment data including sentiment
            video_title: Title of the video
            save_path: Optional custom save path
            
        Returns:
            Path to saved chart
        """
        try:
            if comments_df.empty:
                logger.warning("No comment data for timeline")
                return ""
            
            # Prepare data
            df = comments_df.copy()
            df['published_at'] = pd.to_datetime(df['published_at'])
            df = df.sort_values('published_at')
            
            # Create rolling sentiment average
            df['sentiment_rolling'] = df['sentiment_polarity'].rolling(window=10, min_periods=1).mean()
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[2, 1])
            
            # Main timeline plot
            scatter = ax1.scatter(df['published_at'], df['sentiment_polarity'], 
                                c=df['sentiment_polarity'], cmap='RdYlGn', 
                                alpha=0.6, s=50)
            
            # Rolling average line
            ax1.plot(df['published_at'], df['sentiment_rolling'], 
                    color='blue', linewidth=2, label='Rolling Average (10 comments)')
            
            # Horizontal reference lines
            ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            ax1.axhline(y=0.3, color='green', linestyle=':', alpha=0.5, label='Positive Threshold')
            ax1.axhline(y=-0.3, color='red', linestyle=':', alpha=0.5, label='Negative Threshold')
            
            ax1.set_ylabel('Sentiment Polarity', fontsize=12)
            ax1.set_title(f'Sentiment Timeline\n{video_title}', fontsize=16, fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax1)
            cbar.set_label('Sentiment Polarity', rotation=270, labelpad=20)
            
            # Sentiment frequency histogram
            ax2.hist(df['sentiment_polarity'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            ax2.set_xlabel('Sentiment Polarity', fontsize=12)
            ax2.set_ylabel('Frequency', fontsize=12)
            ax2.set_title('Sentiment Distribution', fontsize=14)
            ax2.grid(True, alpha=0.3)
            
            # Format x-axis for timeline
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            ax1.xaxis.set_major_locator(mdates.HourLocator(interval=6))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            if not save_path:
                safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '_')).rstrip()[:50]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = self.output_dir / f"sentiment_timeline_{safe_title}_{timestamp}.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Sentiment timeline chart saved: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Failed to create sentiment timeline: {str(e)}")
            return ""
    
    def create_wordcloud(
        self,
        comments_df: pd.DataFrame,
        sentiment_filter: str = "all",
        video_title: str = "YouTube Video",
        save_path: Optional[str] = None
    ) -> str:
        """
        Create a word cloud from comments.
        
        Args:
            comments_df: DataFrame with comment data
            sentiment_filter: "positive", "negative", "neutral", or "all"
            video_title: Title of the video
            save_path: Optional custom save path
            
        Returns:
            Path to saved chart
        """
        try:
            if comments_df.empty:
                logger.warning("No comment data for word cloud")
                return ""
            
            # Filter comments by sentiment
            df = comments_df.copy()
            if sentiment_filter != "all":
                df = df[df['sentiment_label'] == sentiment_filter]
            
            if df.empty:
                logger.warning(f"No {sentiment_filter} comments found for word cloud")
                return ""
            
            # Combine all comment text
            text = ' '.join(df['text'].astype(str).tolist())
            
            # Clean text for word cloud
            text = self._clean_text_for_wordcloud(text)
            
            if not text.strip():
                logger.warning("No valid text found for word cloud")
                return ""
            
            # Create word cloud
            wordcloud = WordCloud(
                width=1200,
                height=800,
                background_color='white',
                max_words=100,
                colormap='viridis' if sentiment_filter == "all" 
                         else ('Greens' if sentiment_filter == "positive" 
                              else ('Reds' if sentiment_filter == "negative" else 'Blues')),
                relative_scaling=0.5,
                random_state=42
            ).generate(text)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(15, 10))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            
            # Title
            sentiment_title = f" ({sentiment_filter.title()} Comments)" if sentiment_filter != "all" else ""
            ax.set_title(f'Word Cloud{sentiment_title}\n{video_title}', 
                        fontsize=18, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            # Save chart
            if not save_path:
                safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '_')).rstrip()[:50]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"wordcloud_{sentiment_filter}_{safe_title}_{timestamp}.png"
                save_path = self.output_dir / filename
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Word cloud saved: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Failed to create word cloud: {str(e)}")
            return ""
    
    def create_interactive_sentiment_dashboard(
        self,
        sentiment_data: Dict[str, Any],
        comments_df: pd.DataFrame,
        video_title: str = "YouTube Video",
        save_path: Optional[str] = None
    ) -> str:
        """
        Create an interactive dashboard with multiple sentiment visualizations.
        
        Args:
            sentiment_data: Dictionary with sentiment statistics
            comments_df: DataFrame with comment data
            video_title: Title of the video
            save_path: Optional custom save path
            
        Returns:
            Path to saved HTML dashboard
        """
        try:
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Sentiment Distribution', 'Sentiment Timeline', 
                              'Emotion Strength', 'Subjectivity Analysis'),
                specs=[[{"type": "pie"}, {"type": "scatter"}],
                       [{"type": "bar"}, {"type": "histogram"}]]
            )
            
            # 1. Sentiment Distribution (Pie Chart)
            sentiment_dist = sentiment_data.get('sentiment_distribution', {})
            labels = []
            values = []
            colors_list = []
            
            for sentiment in ['positive', 'negative', 'neutral']:
                if sentiment in sentiment_dist:
                    count = sentiment_dist[sentiment]['count']
                    if count > 0:
                        labels.append(sentiment.title())
                        values.append(count)
                        colors_list.append(self.colors[sentiment])
            
            if values:
                fig.add_trace(
                    go.Pie(labels=labels, values=values, marker_colors=colors_list,
                           textinfo='label+percent', name="Sentiment"),
                    row=1, col=1
                )
            
            # 2. Sentiment Timeline
            if not comments_df.empty:
                df = comments_df.copy()
                df['published_at'] = pd.to_datetime(df['published_at'])
                df = df.sort_values('published_at')
                
                fig.add_trace(
                    go.Scatter(x=df['published_at'], y=df['sentiment_polarity'],
                             mode='markers', marker=dict(color=df['sentiment_polarity'],
                                                        colorscale='RdYlGn', size=8),
                             name="Comments", text=df['text'].str[:100] + "...",
                             hovertemplate='<b>%{text}</b><br>Sentiment: %{y:.2f}<br>Time: %{x}<extra></extra>'),
                    row=1, col=2
                )
            
            # 3. Emotion Strength Distribution
            emotion_data = sentiment_data.get('emotion_strength', {})
            if emotion_data:
                emotions = list(emotion_data.keys())
                counts = list(emotion_data.values())
                
                fig.add_trace(
                    go.Bar(x=emotions, y=counts, marker_color=['#3498DB', '#E67E22', '#E74C3C'],
                           name="Emotion Strength"),
                    row=2, col=1
                )
            
            # 4. Subjectivity Histogram
            if not comments_df.empty and 'sentiment_subjectivity' in comments_df.columns:
                fig.add_trace(
                    go.Histogram(x=comments_df['sentiment_subjectivity'], 
                               nbinsx=20, marker_color='#9B59B6',
                               name="Subjectivity"),
                    row=2, col=2
                )
            
            # Update layout
            fig.update_layout(
                title=f'Sentiment Analysis Dashboard<br>{video_title}',
                height=800,
                showlegend=False,
                template='plotly_white'
            )
            
            # Save interactive chart
            if not save_path:
                safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '_')).rstrip()[:50]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = self.output_dir / f"interactive_dashboard_{safe_title}_{timestamp}.html"
            
            fig.write_html(str(save_path))
            
            logger.info(f"Interactive dashboard saved: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Failed to create interactive dashboard: {str(e)}")
            return ""
    
    def create_comprehensive_report(
        self,
        sentiment_data: Dict[str, Any],
        comments_df: pd.DataFrame,
        video_title: str = "YouTube Video",
        video_id: str = ""
    ) -> Dict[str, str]:
        """
        Create a comprehensive visualization report with all charts.
        
        Args:
            sentiment_data: Dictionary with sentiment statistics
            comments_df: DataFrame with comment data
            video_title: Title of the video
            video_id: YouTube video ID
            
        Returns:
            Dictionary with paths to all generated charts
        """
        logger.info(f"Generating comprehensive visualization report for: {video_title}")
        
        charts = {}
        
        try:
            # 1. Sentiment Distribution
            charts['distribution'] = self.create_sentiment_distribution_chart(
                sentiment_data, video_title
            )
            
            # 2. Timeline (if we have enough data)
            if not comments_df.empty and len(comments_df) > 5:
                charts['timeline'] = self.create_sentiment_timeline(
                    comments_df, video_title
                )
            
            # 3. Word clouds
            charts['wordcloud_all'] = self.create_wordcloud(
                comments_df, "all", video_title
            )
            
            # Create sentiment-specific word clouds if we have enough data
            for sentiment in ['positive', 'negative']:
                sentiment_comments = comments_df[comments_df['sentiment_label'] == sentiment]
                if len(sentiment_comments) >= 5:
                    charts[f'wordcloud_{sentiment}'] = self.create_wordcloud(
                        comments_df, sentiment, video_title
                    )
            
            # 4. Interactive Dashboard
            charts['dashboard'] = self.create_interactive_sentiment_dashboard(
                sentiment_data, comments_df, video_title
            )
            
            # Filter out empty paths
            charts = {k: v for k, v in charts.items() if v}
            
            logger.info(f"Generated {len(charts)} visualization charts")
            return charts
            
        except Exception as e:
            logger.error(f"Failed to create comprehensive report: {str(e)}")
            return charts
    
    def _clean_text_for_wordcloud(self, text: str) -> str:
        """Clean text for word cloud generation."""
        import re
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                     'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
                     'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                     'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
                     'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
        
        words = [word for word in text.split() if word not in stop_words and len(word) > 2]
        
        return ' '.join(words)


if __name__ == "__main__":
    # Example usage
    generator = ChartGenerator()
    
    # Sample data for testing
    sample_sentiment_data = {
        'total_comments': 100,
        'sentiment_distribution': {
            'positive': {'count': 60, 'percentage': 60.0},
            'negative': {'count': 25, 'percentage': 25.0},
            'neutral': {'count': 15, 'percentage': 15.0}
        },
        'average_scores': {
            'polarity': 0.25,
            'subjectivity': 0.65,
            'vader_compound': 0.30
        },
        'emotion_strength': {
            'weak': 30,
            'moderate': 50,
            'strong': 20
        },
        'overall_sentiment': 'positive'
    }
    
    # Create test chart
    chart_path = generator.create_sentiment_distribution_chart(
        sample_sentiment_data, 
        "Test Video - Sentiment Analysis Demo"
    )
    
    if chart_path:
        print(f"Test chart created: {chart_path}")
    else:
        print("Failed to create test chart")
