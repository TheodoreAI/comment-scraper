#!/usr/bin/env python3
"""
Simple YouTube Comment Scraper - Working Version

This script provides a simple interface for the YouTube Comment Scraper.
"""

import sys
import os
from pathlib import Path

# Add the project root and src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

def show_help():
    print("""
YouTube Comment Scraper - Phase 2 with Sentiment Analysis

Usage:
  python yt_scraper.py <video_url> [options]     # Extract comments
  python yt_scraper.py list                      # List extracted videos  
  python yt_scraper.py info <video_id>           # Get video info
  python yt_scraper.py analyze <video_id>        # Analyze sentiment (NEW)
  python yt_scraper.py visualize <video_id>      # Create charts (NEW)
  python yt_scraper.py report <video_id>         # Full report (NEW)

Extract Options:
  --max-comments N     Maximum comments to extract (default: 1000)
  --order TYPE         Order by 'relevance' or 'time' (default: relevance)
  --export FORMAT      Export to 'csv' or 'json' (default: none)
  --no-save           Don't save to database

Sentiment Analysis Options:
  --charts             Generate charts with analysis
  --wordcloud          Create word clouds
  --export-report      Export detailed report

Examples:
  python yt_scraper.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  python yt_scraper.py dQw4w9WgXcQ --max-comments 100 --export csv
  python yt_scraper.py analyze dQw4w9WgXcQ --charts --wordcloud
  python yt_scraper.py visualize dQw4w9WgXcQ  
  python yt_scraper.py report dQw4w9WgXcQ --export-report
  python yt_scraper.py list
  python yt_scraper.py info dQw4w9WgXcQ
    """)

def handle_sentiment_analysis(video_id: str, generate_charts: bool = False, generate_wordcloud: bool = False):
    """Handle sentiment analysis command."""
    import sqlite3
    import pandas as pd
    from src.analysis.sentiment_analyzer import SentimentAnalyzer
    from src.visualization.chart_generator import ChartGenerator
    from src.utils.config import ConfigManager
    
    config = ConfigManager()
    
    # Get comments from database
    conn = sqlite3.connect('data/comments.db')
    
    # Check if video exists
    video_query = "SELECT * FROM videos WHERE video_id = ?"
    video_df = pd.read_sql_query(video_query, conn, params=(video_id,))
    
    if video_df.empty:
        print(f"Error: Video {video_id} not found in database.")
        print("Please extract comments first using the extraction command.")
        conn.close()
        return 1
    
    video_info = video_df.iloc[0]
    
    # Get comments with sentiment data
    comments_query = """
    SELECT * FROM comments 
    WHERE video_id = ? AND sentiment_analyzed_at IS NOT NULL
    ORDER BY extracted_at DESC
    """
    
    comments_df = pd.read_sql_query(comments_query, conn, params=(video_id,))
    conn.close()
    
    if comments_df.empty:
        print(f"Error: No sentiment data found for video {video_id}.")
        print("Comments may have been extracted before sentiment analysis was enabled.")
        print("Try re-extracting the comments to get sentiment analysis.")
        return 1
    
    # Generate sentiment summary
    analyzer = SentimentAnalyzer()
    
    # Convert DataFrame sentiment data to SentimentResult objects for summary
    sentiment_results = []
    for _, row in comments_df.iterrows():
        try:
            # Create a mock SentimentResult for summary calculation
            from src.analysis.sentiment_analyzer import SentimentResult
            from datetime import datetime
            
            result = SentimentResult(
                polarity=row['sentiment_polarity'] or 0.0,
                subjectivity=row['sentiment_subjectivity'] or 0.0,
                vader_compound=row['vader_compound'] or 0.0,
                vader_positive=row['vader_positive'] or 0.0,
                vader_negative=row['vader_negative'] or 0.0,
                vader_neutral=row['vader_neutral'] or 1.0,
                sentiment_label=row['sentiment_label'] or 'neutral',
                emotion_strength=row['emotion_strength'] or 'weak',
                is_subjective=bool(row['is_subjective']),
                analyzed_at=datetime.now(),
                text_length=len(row['text'])
            )
            sentiment_results.append(result)
        except Exception as e:
            print(f"Warning: Error processing sentiment data for one comment: {e}")
            continue
    
    if not sentiment_results:
        print("Error: Could not process sentiment data.")
        return 1
    
    sentiment_summary = analyzer.get_sentiment_summary(sentiment_results)
    
    # Print analysis results
    print(f"\n{'='*60}")
    print(f"SENTIMENT ANALYSIS RESULTS")
    print(f"{'='*60}")
    
    print(f"\nVideo: {video_info['title']}")
    print(f"Channel: {video_info['channel_title']}")
    print(f"Total Comments Analyzed: {sentiment_summary['total_comments']}")
    
    print(f"\nSentiment Distribution:")
    for sentiment, data in sentiment_summary['sentiment_distribution'].items():
        print(f"  {sentiment.title()}: {data['count']} comments ({data['percentage']:.1f}%)")
    
    print(f"\nAverage Scores:")
    scores = sentiment_summary['average_scores']
    print(f"  Polarity: {scores['polarity']:.3f} (Range: -1 to 1)")
    print(f"  Subjectivity: {scores['subjectivity']:.3f} (Range: 0 to 1)")
    print(f"  VADER Compound: {scores['vader_compound']:.3f} (Range: -1 to 1)")
    
    print(f"\nOverall Sentiment: {sentiment_summary['overall_sentiment'].title()}")
    
    print(f"\nEmotion Strength:")
    emotion = sentiment_summary['emotion_strength']
    print(f"  Strong: {emotion['strong']} comments")
    print(f"  Moderate: {emotion['moderate']} comments")
    print(f"  Weak: {emotion['weak']} comments")
    
    subj = sentiment_summary['subjectivity_analysis']
    print(f"\nSubjectivity:")
    print(f"  Subjective: {subj['subjective_count']} comments ({subj['subjectivity_ratio']}%)")
    print(f"  Objective: {subj['objective_count']} comments")
    
    # Generate charts if requested
    if generate_charts or generate_wordcloud:
        print(f"\n{'='*60}")
        print("GENERATING VISUALIZATIONS")
        print(f"{'='*60}")
        
        chart_generator = ChartGenerator()
        
        if generate_charts:
            print("\nGenerating sentiment distribution chart...")
            chart_path = chart_generator.create_sentiment_distribution_chart(
                sentiment_summary, video_info['title']
            )
            if chart_path:
                print(f"✓ Chart saved: {chart_path}")
            
            if len(comments_df) > 10:
                print("Generating sentiment timeline...")
                timeline_path = chart_generator.create_sentiment_timeline(
                    comments_df, video_info['title']
                )
                if timeline_path:
                    print(f"✓ Timeline saved: {timeline_path}")
        
        if generate_wordcloud:
            print("Generating word cloud...")
            wordcloud_path = chart_generator.create_wordcloud(
                comments_df, "all", video_info['title']
            )
            if wordcloud_path:
                print(f"✓ Word cloud saved: {wordcloud_path}")
    
    print(f"\n{'='*60}")
    return 0

def handle_visualization(video_id: str):
    """Handle visualization command."""
    import sqlite3
    import pandas as pd
    from src.visualization.chart_generator import ChartGenerator
    from src.analysis.sentiment_analyzer import SentimentAnalyzer
    
    # Get data from database
    conn = sqlite3.connect('data/comments.db')
    
    video_query = "SELECT * FROM videos WHERE video_id = ?"
    video_df = pd.read_sql_query(video_query, conn, params=(video_id,))
    
    if video_df.empty:
        print(f"Error: Video {video_id} not found in database.")
        conn.close()
        return 1
    
    video_info = video_df.iloc[0]
    
    comments_query = """
    SELECT * FROM comments 
    WHERE video_id = ? AND sentiment_analyzed_at IS NOT NULL
    """
    
    comments_df = pd.read_sql_query(comments_query, conn, params=(video_id,))
    conn.close()
    
    if comments_df.empty:
        print(f"Error: No sentiment data found for video {video_id}.")
        return 1
    
    # Generate sentiment summary
    analyzer = SentimentAnalyzer()
    sentiment_results = []
    
    for _, row in comments_df.iterrows():
        try:
            from src.analysis.sentiment_analyzer import SentimentResult
            from datetime import datetime
            
            result = SentimentResult(
                polarity=row['sentiment_polarity'] or 0.0,
                subjectivity=row['sentiment_subjectivity'] or 0.0,
                vader_compound=row['vader_compound'] or 0.0,
                vader_positive=row['vader_positive'] or 0.0,
                vader_negative=row['vader_negative'] or 0.0,
                vader_neutral=row['vader_neutral'] or 1.0,
                sentiment_label=row['sentiment_label'] or 'neutral',
                emotion_strength=row['emotion_strength'] or 'weak',
                is_subjective=bool(row['is_subjective']),
                analyzed_at=datetime.now(),
                text_length=len(row['text'])
            )
            sentiment_results.append(result)
        except Exception:
            continue
    
    sentiment_summary = analyzer.get_sentiment_summary(sentiment_results)
    
    print(f"\n{'='*60}")
    print(f"GENERATING COMPREHENSIVE VISUALIZATIONS")
    print(f"{'='*60}")
    
    print(f"\nVideo: {video_info['title']}")
    print(f"Creating charts for {len(comments_df)} comments with sentiment data...")
    
    # Generate all visualizations
    chart_generator = ChartGenerator()
    charts = chart_generator.create_comprehensive_report(
        sentiment_summary, comments_df, video_info['title'], video_id
    )
    
    print(f"\n✓ Generated {len(charts)} visualizations:")
    for chart_type, path in charts.items():
        if path:
            chart_name = chart_type.replace('_', ' ').title()
            print(f"  • {chart_name}: {path}")
    
    print(f"\n{'='*60}")
    print("All visualizations completed!")
    print(f"{'='*60}")
    
    return 0

def handle_full_report(video_id: str, export_report: bool = False):
    """Handle full report command."""
    print(f"\n{'='*60}")
    print(f"FULL SENTIMENT REPORT")
    print(f"{'='*60}")
    
    # Run analysis
    result = handle_sentiment_analysis(video_id, generate_charts=True, generate_wordcloud=True)
    if result != 0:
        return result
    
    # Run visualization
    print(f"\n{'='*40}")
    print("ADDITIONAL VISUALIZATIONS")
    print(f"{'='*40}")
    
    result = handle_visualization(video_id)
    if result != 0:
        return result
    
    if export_report:
        print(f"\n{'='*40}")
        print("EXPORTING DETAILED REPORT")
        print(f"{'='*40}")
        print("Note: Advanced report export will be implemented in future updates.")
        print("Currently available: Charts, word clouds, and interactive dashboards.")
    
    return 0

def main():
    if len(sys.argv) < 2:
        show_help()
        return 1
    
    command = sys.argv[1]
    
    # Handle list command
    if command.lower() == 'list':
        from src.scraper.comment_extractor import CommentExtractor
        from src.utils.config import ConfigManager
        
        try:
            config = ConfigManager()
            extractor = CommentExtractor(config)
            videos = extractor.list_extracted_videos()
            
            if not videos:
                print("No videos found in database.")
                return 0
            
            print("\nExtracted Videos:")
            print("-" * 100)
            print(f"{'Video ID':<12} {'Title':<40} {'Channel':<20} {'Comments':<10} {'Date':<19}")
            print("-" * 100)
            
            for video in videos:
                title = video['title'][:37] + "..." if len(video['title']) > 40 else video['title']
                channel = video['channel_title'][:17] + "..." if len(video['channel_title']) > 20 else video['channel_title']
                date = video['extracted_at'][:19] if video['extracted_at'] else 'Unknown'
                
                print(f"{video['video_id']:<12} {title:<40} {channel:<20} {video['total_comments_extracted']:<10} {date:<19}")
            
            print("-" * 100)
            print(f"Total videos: {len(videos)}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1
        
        return 0
    
    # Handle info command
    elif command.lower() == 'info':
        if len(sys.argv) < 3:
            print("Error: Please provide a video ID")
            print("Usage: python yt_scraper.py info <video_id>")
            return 1
        
        video_id = sys.argv[2]
        
        from src.scraper.comment_extractor import CommentExtractor
        from src.utils.config import ConfigManager
        import json
        
        try:
            config = ConfigManager()
            extractor = CommentExtractor(config)
            video_info = extractor.get_video_from_database(video_id)
            
            if video_info:
                print(json.dumps(video_info, indent=2))
            else:
                print(f"Video {video_id} not found in database.")
                return 1
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1
        
        return 0
    
    # Handle analyze command
    elif command.lower() == 'analyze':
        if len(sys.argv) < 3:
            print("Error: Please provide a video ID")
            print("Usage: python yt_scraper.py analyze <video_id> [--charts] [--wordcloud]")
            return 1
        
        video_id = sys.argv[2]
        generate_charts = '--charts' in sys.argv
        generate_wordcloud = '--wordcloud' in sys.argv
        
        try:
            return handle_sentiment_analysis(video_id, generate_charts, generate_wordcloud)
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1
    
    # Handle visualize command
    elif command.lower() == 'visualize':
        if len(sys.argv) < 3:
            print("Error: Please provide a video ID")
            print("Usage: python yt_scraper.py visualize <video_id>")
            return 1
        
        video_id = sys.argv[2]
        
        try:
            return handle_visualization(video_id)
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1
    
    # Handle report command
    elif command.lower() == 'report':
        if len(sys.argv) < 3:
            print("Error: Please provide a video ID")
            print("Usage: python yt_scraper.py report <video_id> [--export-report]")
            return 1
        
        video_id = sys.argv[2]
        export_report = '--export-report' in sys.argv
        
        try:
            return handle_full_report(video_id, export_report)
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1
    
    # Handle help
    elif command.lower() in ['help', '-h', '--help']:
        show_help()
        return 0
    
    # Handle video extraction
    else:
        from src.scraper.comment_extractor import CommentExtractor
        from src.utils.config import ConfigManager
        from src.utils.logger import setup_logger
        from src.utils.helpers import extract_video_id
        
        video_url = command
        
        # Parse arguments
        max_comments = None
        order = 'relevance'
        export_format = None
        save_to_db = True
        
        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i]
            
            if arg == '--max-comments' and i + 1 < len(sys.argv):
                try:
                    max_comments = int(sys.argv[i + 1])
                    i += 2
                except ValueError:
                    print("Error: --max-comments must be a number")
                    return 1
            elif arg == '--order' and i + 1 < len(sys.argv):
                order = sys.argv[i + 1]
                if order not in ['relevance', 'time']:
                    print("Error: --order must be 'relevance' or 'time'")
                    return 1
                i += 2
            elif arg == '--export' and i + 1 < len(sys.argv):
                export_format = sys.argv[i + 1]
                if export_format not in ['csv', 'json']:
                    print("Error: --export must be 'csv' or 'json'")
                    return 1
                i += 2
            elif arg == '--no-save':
                save_to_db = False
                i += 1
            else:
                print(f"Error: Unknown argument {arg}")
                return 1
        
        # Validate video URL
        video_id = extract_video_id(video_url)
        if not video_id:
            print(f"Error: Invalid YouTube URL or video ID: {video_url}")
            return 1
        
        try:
            # Initialize components
            config = ConfigManager()
            logger = setup_logger(config_manager=config)
            extractor = CommentExtractor(config)
            
            print(f"Extracting comments from video: {video_id}")
            if max_comments:
                print(f"Max comments: {max_comments}")
            print(f"Order: {order}")
            if export_format:
                print(f"Export format: {export_format}")
            print()
            
            # Extract comments
            results = extractor.extract_comments(
                video_url_or_id=video_url,
                max_comments=max_comments,
                order=order,
                save_to_db=save_to_db,
                export_format=export_format
            )
            
            # Print results
            stats = results['statistics']
            video_info = results['video_info']
            
            print("\n" + "="*60)
            print("EXTRACTION COMPLETED SUCCESSFULLY")
            print("="*60)
            
            print(f"\nVideo Information:")
            print(f"  Title: {video_info['title']}")
            print(f"  Channel: {video_info['channel_title']}")
            print(f"  Published: {video_info['published_at']}")
            print(f"  Views: {video_info['view_count']:,}")
            print(f"  Likes: {video_info['like_count']:,}")
            print(f"  Total Comments (video): {video_info['comment_count']:,}")
            
            print(f"\nExtraction Statistics:")
            print(f"  Comments Extracted: {stats['total_comments_extracted']:,}")
            print(f"  Valid Comments: {stats['valid_comments']:,}")
            print(f"  Invalid Comments: {stats['invalid_comments']:,}")
            print(f"  Extraction Time: {stats['extraction_time']}")
            
            if 'exported_file' in results:
                print(f"\nExported to: {results['exported_file']}")
            
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1
        
        return 0

if __name__ == "__main__":
    sys.exit(main())
