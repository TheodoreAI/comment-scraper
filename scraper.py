#!/usr/bin/env python3
"""
Simple launcher for YouTube Comment Scraper commands.
"""

import sys
import os
from pathlib import Path

# Add the project root and src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    # Handle different command patterns
    if len(sys.argv) > 1:
        first_arg = sys.argv[1].lower()
        
        if first_arg == 'list':
            # List command
            from src.scraper.comment_extractor import CommentExtractor
            from src.utils.config import ConfigManager
            from src.main import print_video_list
            
            config = ConfigManager()
            extractor = CommentExtractor(config)
            videos = extractor.list_extracted_videos()
            print_video_list(videos, 'table')
            
        elif first_arg == 'info' and len(sys.argv) > 2:
            # Info command
            from src.scraper.comment_extractor import CommentExtractor
            from src.utils.config import ConfigManager
            import json
            
            video_id = sys.argv[2]
            config = ConfigManager()
            extractor = CommentExtractor(config)
            video_info = extractor.get_video_from_database(video_id)
            
            if video_info:
                print(json.dumps(video_info, indent=2))
            else:
                print(f"Video {video_id} not found in database.")
                sys.exit(1)
                
        else:
            # Default: extract comments
            from src.main import main
            sys.exit(main())
    else:
        # No arguments, show help
        from src.main import main
        sys.exit(main())
