"""
Main entry point for the YouTube Comment Scraper application.

This module provides command-line interface and main application logic.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports  
src_path = str(Path(__file__).parent)
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, src_path)
sys.path.insert(0, project_root)

# Import with proper path handling
try:
    from scraper.comment_extractor import CommentExtractor
    from utils.config import ConfigManager
    from utils.logger import setup_logger
    from utils.helpers import extract_video_id, validate_youtube_url
except ImportError:
    # Fallback for direct execution
    from src.scraper.comment_extractor import CommentExtractor
    from src.utils.config import ConfigManager
    from src.utils.logger import setup_logger
    from src.utils.helpers import extract_video_id, validate_youtube_url


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="YouTube Comment Scraper - Extract and analyze YouTube video comments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s dQw4w9WgXcQ --max-comments 500 --export csv
  %(prog)s list
  %(prog)s info dQw4w9WgXcQ
        """
    )
    
    # Subcommands first
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List extracted videos')
    list_parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format'
    )
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get video information')
    info_parser.add_argument('video_id', help='Video ID to get info for')
    
    # For the main video extraction (when no subcommand is used)
    parser.add_argument(
        'video',
        nargs='?',
        help='YouTube video URL or video ID'
    )
    
    parser.add_argument(
        '--max-comments', '-m',
        type=int,
        default=None,
        help='Maximum number of comments to extract (default: from config)'
    )
    
    parser.add_argument(
        '--order', '-o',
        choices=['relevance', 'time'],
        default='relevance',
        help='Comment ordering (default: relevance)'
    )
    
    parser.add_argument(
        '--export', '-e',
        choices=['csv', 'json'],
        default=None,
        help='Export format (default: no export)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save to database'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default=None,
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=None,
        help='Logging level (default: from config)'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='YouTube Comment Scraper 0.1.0'
    )
    
    return parser


def print_extraction_results(results: dict) -> None:
    """Print extraction results in a formatted way."""
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


def print_video_list(videos: list, format_type: str = 'table') -> None:
    """Print list of extracted videos."""
    if not videos:
        print("No videos found in database.")
        return
    
    if format_type == 'json':
        import json
        print(json.dumps(videos, indent=2))
        return
    
    # Table format
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


def main() -> int:
    """Main application entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        # Initialize configuration
        config = ConfigManager(args.config)
        
        # Setup logging
        logger = setup_logger(log_level=args.log_level, config_manager=config)
        
        # Handle subcommands
        if args.command == 'list':
            extractor = CommentExtractor(config)
            videos = extractor.list_extracted_videos()
            print_video_list(videos, args.format)
            return 0
        
        elif args.command == 'info':
            extractor = CommentExtractor(config)
            video_info = extractor.get_video_from_database(args.video_id)
            
            if video_info:
                import json
                print(json.dumps(video_info, indent=2))
            else:
                print(f"Video {args.video_id} not found in database.")
                return 1
            
            return 0
        
        # Default behavior - direct video extraction
        video_url = args.video
        if not video_url:
            parser.print_help()
            return 1
        
        # Validate video URL/ID
        video_id = extract_video_id(video_url)
        if not video_id:
            print(f"Error: Invalid YouTube URL or video ID: {video_url}")
            return 1
        
        logger.info(f"Starting comment extraction for video: {video_id}")
        
        # Initialize extractor
        extractor = CommentExtractor(config)
        
        # Extract comments
        results = extractor.extract_comments(
            video_url_or_id=video_url,
            max_comments=args.max_comments,
            order=args.order,
            save_to_db=not args.no_save,
            export_format=args.export
        )
        
        # Print results
        print_extraction_results(results)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.log_level == 'DEBUG':
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
