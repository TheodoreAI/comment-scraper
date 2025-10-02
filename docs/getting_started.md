# Getting Started with YouTube Comment Scraper

This guide will help you set up and use the YouTube Comment Scraper tool.

## Prerequisites

- Python 3.8 or higher
- YouTube Data API v3 key from Google Cloud Console

## Installation

1. **Clone or download the project**
   ```bash
   cd /path/to/your/projects
   # If you have the project files, navigate to the directory
   cd comment-scraper
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Getting a YouTube API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click on it and press "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the generated API key

## Configuration

1. **Update the configuration file**
   ```bash
   # The config.yaml file is already created with default settings
   # You need to update the API key
   ```

2. **Edit config.yaml**
   ```yaml
   youtube:
     api_key: "YOUR_ACTUAL_API_KEY_HERE"  # Replace with your API key
     api_service_name: "youtube"
     api_version: "v3"
     max_results_per_request: 100
     max_total_comments: 1000
   ```

## Usage Examples

### Basic Usage

Extract comments from a YouTube video:
```bash
python src/main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Advanced Usage

Extract comments with specific options:
```bash
# Limit to 500 comments, order by time, export to CSV
python src/main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --max-comments 500 \
  --order time \
  --export csv

# Extract without saving to database, export to JSON
python src/main.py "dQw4w9WgXcQ" \
  --no-save \
  --export json

# Use custom configuration file
python src/main.py "https://youtu.be/dQw4w9WgXcQ" \
  --config custom_config.yaml \
  --log-level DEBUG
```

### Management Commands

List all extracted videos:
```bash
python src/main.py list
```

Get information about a specific video:
```bash
python src/main.py info dQw4w9WgXcQ
```

## Python API Usage

You can also use the scraper programmatically:

```python
from src.scraper.comment_extractor import CommentExtractor
from src.utils.config import ConfigManager

# Initialize the extractor
config = ConfigManager()
extractor = CommentExtractor(config)

# Extract comments
results = extractor.extract_comments(
    video_url_or_id="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    max_comments=100,
    order="relevance",
    save_to_db=True,
    export_format="csv"
)

# Access the results
video_info = results['video_info']
comments = results['comments']
statistics = results['statistics']

print(f"Extracted {len(comments)} comments from '{video_info['title']}'")
```

## Configuration Options

### YouTube API Settings
- `api_key`: Your YouTube Data API v3 key
- `max_results_per_request`: Comments per API call (1-100)
- `max_total_comments`: Total comments to extract per video

### Rate Limiting
- `requests_per_second`: API requests per second
- `quota_limit_per_day`: Daily quota limit

### Data Filtering
- `min_comment_length`: Minimum comment length in characters
- `max_comment_length`: Maximum comment length in characters
- `exclude_spam`: Enable spam filtering
- `languages`: List of allowed language codes (empty = all)

### Storage
- `database_path`: SQLite database location
- `raw_data_path`: Raw data storage directory
- `processed_data_path`: Processed data directory
- `exports_path`: Export files directory

## Data Output

### Database Storage
Comments are stored in a SQLite database with two main tables:
- `videos`: Video metadata and statistics
- `comments`: Individual comment data

### Export Formats

**CSV Export**: Includes all comment fields in a spreadsheet-friendly format
**JSON Export**: Complete data including video metadata and comments

## Troubleshooting

### Common Issues

1. **"Invalid YouTube URL or video ID"**
   - Check that the URL is a valid YouTube video URL
   - Ensure the video is public and not private/unlisted

2. **"API quota exceeded"**
   - You've reached your daily API quota limit
   - Wait until the quota resets or increase your quota in Google Cloud Console

3. **"Video not found"**
   - The video may be private, deleted, or region-restricted
   - Comments may be disabled for the video

4. **"Permission denied"**
   - Check that your API key is valid and has the correct permissions
   - Ensure YouTube Data API v3 is enabled for your project

### Debug Mode

Run with debug logging to see detailed information:
```bash
python src/main.py "VIDEO_URL" --log-level DEBUG
```

### Testing Without API Key

Run the demo script to test functionality without an API key:
```bash
python demo.py
```

## Next Steps

This completes Phase 1 of the YouTube Comment Scraper. The foundation is now in place for:

- **Phase 2**: Sentiment analysis and basic visualization
- **Phase 3**: Interactive dashboard and advanced analytics
- **Phase 4**: Advanced features and optimization

To continue to Phase 2, we'll add sentiment analysis capabilities using TextBlob and VADER, along with basic visualization features.
