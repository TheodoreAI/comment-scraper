# YouTube Comment Scraper & Sentiment Analysis Tool

A comprehensive Python tool for extracting YouTube video comments, analyzing sentiment, and generating insightful visualizations.

## Features

- Extract comments from YouTube videos using the official YouTube Data API v3
- Perform sentiment analysis on comments
- Generate interactive visualizations and reports
- Export data in multiple formats (CSV, JSON, PDF)
- Handle large datasets with efficient processing

## Quick Start

### Prerequisites

- Python 3.8 or higher
- YouTube Data API v3 key (get from Google Cloud Console)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd comment-scraper
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API credentials:
```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your YouTube API key
```

### Usage

```python
from src.scraper.comment_extractor import CommentExtractor
from src.analysis.sentiment_analyzer import SentimentAnalyzer

# Extract comments
extractor = CommentExtractor()
comments = extractor.extract_comments("VIDEO_URL_OR_ID")

# Analyze sentiment
analyzer = SentimentAnalyzer()
results = analyzer.analyze(comments)

# Generate visualizations
# (Coming in Phase 2)
```

## Project Structure

```
comment-scraper/
├── src/                    # Source code
│   ├── scraper/           # Comment extraction
│   ├── analysis/          # Sentiment analysis
│   ├── visualization/     # Charts and reports
│   ├── utils/             # Utilities
│   └── main.py           # Main application
├── data/                  # Data storage
├── tests/                 # Test suite
├── docs/                  # Documentation
└── config.yaml          # Configuration
```

## Development Status

- ✅ Phase 1: Foundation & Basic Scraping (Current)
- ⏳ Phase 2: Sentiment Analysis & Basic Visualization
- ⏳ Phase 3: Advanced Analytics & Interactive Dashboard  
- ⏳ Phase 4: Advanced Features & Optimization

## Contributing

Please read the development guidelines in `docs/` before contributing.

## License

MIT License - see LICENSE file for details.
