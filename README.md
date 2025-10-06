# YouTube Comment Scraper & Sentiment Analysis Tool

A comprehensive Python tool for extracting YouTube video comments, analyzing sentiment, and generating insightful visualizations with an interactive dashboard.

## Features

- Extract comments from YouTube videos using the official YouTube Data API v3
- Real-time sentiment analysis on comments using TextBlob and VADER
- Interactive Streamlit dashboard with:
  - Comment extraction and processing
  - Sentiment distribution analysis
  - Top liked comments visualization
  - Video engagement metrics
  - Historical video analysis
- Export data in multiple formats (CSV, JSON)
- SQLite database for persistent storage
- Efficient processing of large comment datasets
- Comprehensive error handling and rate limiting

## Quick Start

### Prerequisites

- Python 3.8 or higher
- YouTube Data API v3 key (get from Google Cloud Console)
- Required Python packages (see requirements.txt)

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

4. Configure your YouTube API key:
   - Copy the example config: `cp config.yaml.example config.yaml`
   - Edit config.yaml and add your API key
   - Or use Streamlit secrets for secure key storage

### Usage

#### Dashboard Interface

1. Start the Streamlit dashboard:
```bash
streamlit run dashboard.py
```

2. Enter a YouTube video URL
3. Choose extraction options (number of comments, sort order)
4. Click "Extract Comments" to fetch and analyze comments
5. Generate sentiment analysis and engagement visualizations
6. Explore historical video analysis

#### Python API

```python
from src.scraper.comment_extractor import CommentExtractor
from src.analysis.sentiment_analyzer import SentimentAnalyzer

# Extract comments
extractor = CommentExtractor()
comments = extractor.extract_comments("VIDEO_URL_OR_ID")

# Analyze sentiment
analyzer = SentimentAnalyzer()
results = analyzer.analyze(comments)

# Generate visualizations using the dashboard
```

## Project Structure

```text
comment-scraper/
├── src/                    # Source code
│   ├── scraper/           # Comment extraction
│   ├── analysis/          # Sentiment analysis
│   ├── visualization/     # Charts and reports
│   ├── frontend/          # Dashboard components
│   ├── utils/            # Utilities
│   └── main.py          # Main application
├── data/                  # Data storage
│   ├── comments.db       # SQLite database
│   ├── exports/         # Exported data
│   └── charts/          # Generated visualizations
├── tests/                # Test suite
├── docs/                # Documentation
└── dashboard.py        # Streamlit dashboard
```

## Development Status

- ✅ Phase 1: Foundation & Basic Scraping (Completed)
- ✅ Phase 2: Sentiment Analysis & Basic Visualization (Completed)
- ✅ Phase 3: Interactive Dashboard & Analytics (Completed)
- ✅ Phase 4: Engagement Analysis & Optimization (Current)

## Contributing

Please read the development guidelines in `docs/` before contributing.

## License

MIT License - see LICENSE file for details.
