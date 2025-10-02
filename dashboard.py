"""
YouTube Comment Scraper Dashboard

A comprehensive web interface for extracting YouTube comments and performing 
real-time sentiment analysis with interactive visualizations.

This dashboard provides:
- Video URL input and comment extraction
- Real-time sentiment analysis
- Interactive charts and visualizations  
- Data export capabilities
- Video history and comparison
"""

import streamlit as st
import pandas as pd
import sqlite3
import sys
import os
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import json

# Add project paths
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# Import project modules
try:
    from src.scraper.comment_extractor import CommentExtractor
    from src.analysis.sentiment_analyzer import SentimentAnalyzer
    from src.visualization.chart_generator import ChartGenerator
    from src.utils.config import ConfigManager
    from src.utils.helpers import extract_video_id
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="YouTube Comment Sentiment Analyzer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF0000;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #FF0000;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'extraction_complete' not in st.session_state:
    st.session_state.extraction_complete = False
if 'current_video_id' not in st.session_state:
    st.session_state.current_video_id = None
if 'sentiment_data' not in st.session_state:
    st.session_state.sentiment_data = None

def initialize_components():
    """Initialize the core components."""
    try:
        config = ConfigManager()
        extractor = CommentExtractor(config)
        analyzer = SentimentAnalyzer()
        chart_generator = ChartGenerator()
        return config, extractor, analyzer, chart_generator
    except Exception as e:
        st.error(f"Failed to initialize components: {e}")
        return None, None, None, None

def get_video_history():
    """Get list of previously analyzed videos."""
    try:
        conn = sqlite3.connect('data/comments.db')
        query = """
        SELECT video_id, title, channel_title, total_comments_extracted, extracted_at
        FROM videos 
        ORDER BY extracted_at DESC
        LIMIT 20
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error fetching video history: {e}")
        return pd.DataFrame()

def get_sentiment_data(video_id):
    """Get sentiment analysis data for a video."""
    try:
        conn = sqlite3.connect('data/comments.db')
        
        # Get video info
        video_query = "SELECT * FROM videos WHERE video_id = ?"
        video_df = pd.read_sql_query(video_query, conn, params=(video_id,))
        
        if video_df.empty:
            return None, None
        
        # Get comments with sentiment data
        comments_query = """
        SELECT * FROM comments 
        WHERE video_id = ? AND sentiment_analyzed_at IS NOT NULL
        ORDER BY published_at DESC
        """
        comments_df = pd.read_sql_query(comments_query, conn, params=(video_id,))
        conn.close()
        
        return video_df.iloc[0], comments_df
    except Exception as e:
        st.error(f"Error fetching sentiment data: {e}")
        return None, None

def create_sentiment_summary(comments_df):
    """Create sentiment summary statistics."""
    if comments_df.empty:
        return {}
    
    total = len(comments_df)
    
    # Sentiment distribution
    sentiment_counts = comments_df['sentiment_label'].value_counts()
    sentiment_dist = {}
    for sentiment in ['positive', 'negative', 'neutral']:
        count = sentiment_counts.get(sentiment, 0)
        sentiment_dist[sentiment] = {
            'count': count,
            'percentage': (count / total) * 100 if total > 0 else 0
        }
    
    # Average scores
    avg_scores = {
        'polarity': comments_df['sentiment_polarity'].mean(),
        'subjectivity': comments_df['sentiment_subjectivity'].mean(),
        'vader_compound': comments_df['vader_compound'].mean()
    }
    
    # Emotion strength
    emotion_counts = comments_df['emotion_strength'].value_counts()
    emotion_dist = {
        'strong': emotion_counts.get('strong', 0),
        'moderate': emotion_counts.get('moderate', 0),
        'weak': emotion_counts.get('weak', 0)
    }
    
    return {
        'total_comments': total,
        'sentiment_distribution': sentiment_dist,
        'average_scores': avg_scores,
        'emotion_strength': emotion_dist
    }

def main():
    """Main dashboard application."""
    
    # Header
    st.markdown('<h1 class="main-header">🎬 YouTube Comment Sentiment Analyzer</h1>', 
                unsafe_allow_html=True)
    
    # Initialize components
    config, extractor, analyzer, chart_generator = initialize_components()
    
    if not all([config, extractor, analyzer, chart_generator]):
        st.error("Failed to initialize application components. Please check your configuration.")
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "📊 Analyze Video", "📈 Video History", "ℹ️ About"]
    )
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "📊 Analyze Video":
        show_analysis_page(extractor, analyzer, chart_generator)
    elif page == "📈 Video History":
        show_history_page()
    elif page == "ℹ️ About":
        show_about_page()

def show_home_page():
    """Show the home page with overview and instructions."""
    
    st.markdown("## Welcome to the YouTube Comment Sentiment Analyzer! 🚀")
    
    st.markdown("""
    This powerful dashboard allows you to:
    
    ### 🎯 **Key Features**
    - **Extract Comments**: Get comments from any public YouTube video
    - **Sentiment Analysis**: Analyze emotions and opinions using AI
    - **Interactive Charts**: Visualize sentiment patterns and trends
    - **Real-time Processing**: Watch analysis happen in real-time
    - **Export Data**: Download results for further analysis
    
    ### 🔧 **How to Use**
    1. Go to **📊 Analyze Video** page
    2. Paste a YouTube video URL
    3. Click **Extract Comments** and wait for processing
    4. Click **Generate Analysis** to create sentiment charts
    5. Explore your results with interactive visualizations!
    
    ### 📈 **What You'll Get**
    - Sentiment distribution (positive/negative/neutral)
    - Emotion strength analysis
    - Word clouds of common themes
    - Timeline views of comment sentiment
    - Interactive dashboards for deep exploration
    """)
    
    # Quick stats
    try:
        conn = sqlite3.connect('data/comments.db')
        total_videos = pd.read_sql_query("SELECT COUNT(*) as count FROM videos", conn).iloc[0]['count']
        total_comments = pd.read_sql_query("SELECT SUM(total_comments_extracted) as count FROM videos", conn).iloc[0]['count']
        conn.close()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📹 Videos Analyzed", total_videos)
        with col2:
            st.metric("💬 Comments Processed", f"{total_comments:,}" if total_comments else "0")
        with col3:
            st.metric("🧠 AI Models Used", "TextBlob + VADER")
            
    except Exception:
        st.info("No data available yet. Start by analyzing your first video!")

def show_analysis_page(extractor, analyzer, chart_generator):
    """Show the main analysis page."""
    
    st.markdown("## 📊 Video Analysis")
    
    # Video URL input
    st.markdown("### 🎬 Step 1: Enter Video URL")
    video_url = st.text_input(
        "Paste YouTube video URL here:",
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        help="Enter any public YouTube video URL to analyze its comments"
    )
    
    # Extraction options
    col1, col2 = st.columns(2)
    with col1:
        max_comments = st.number_input(
            "Maximum comments to extract:",
            min_value=5,
            max_value=1000,
            value=100,
            step=25,
            help="More comments = better analysis but longer processing time"
        )
    
    with col2:
        order = st.selectbox(
            "Comment order:",
            ["relevance", "time"],
            help="Relevance: most popular comments first, Time: newest comments first"
        )
    
    # Extract comments button
    if st.button("🔄 Extract Comments", type="primary", use_container_width=True):
        if not video_url.strip():
            st.error("Please enter a YouTube video URL")
            return
        
        video_id = extract_video_id(video_url)
        if not video_id:
            st.error("Invalid YouTube URL. Please check the URL and try again.")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔍 Validating video URL...")
            progress_bar.progress(10)
            
            status_text.text("📥 Starting comment extraction...")
            progress_bar.progress(25)
            
            # Extract comments
            results = extractor.extract_comments(
                video_url_or_id=video_url,
                max_comments=max_comments,
                order=order,
                save_to_db=True,
                export_format=None
            )
            
            progress_bar.progress(75)
            status_text.text("🧠 Performing sentiment analysis...")
            
            # Small delay to show progress
            time.sleep(1)
            
            progress_bar.progress(100)
            status_text.text("✅ Extraction completed!")
            
            # Store results in session state
            st.session_state.extraction_complete = True
            st.session_state.current_video_id = video_id
            
            # Show results
            stats = results['statistics']
            video_info = results['video_info']
            
            st.success("🎉 Comments extracted successfully!")
            
            # Display video information
            st.markdown("### 📹 Video Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Title:** {video_info['title']}")
                st.markdown(f"**Channel:** {video_info['channel_title']}")
                st.markdown(f"**Published:** {video_info['published_at'][:10]}")
            
            with col2:
                st.markdown(f"**Views:** {video_info['view_count']:,}")
                st.markdown(f"**Likes:** {video_info['like_count']:,}")
                st.markdown(f"**Total Comments:** {video_info['comment_count']:,}")
            
            # Show extraction stats
            st.markdown("### 📊 Extraction Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Comments Extracted", stats['total_comments_extracted'])
            with col2:
                st.metric("Valid Comments", stats['valid_comments'])
            with col3:
                st.metric("Invalid Comments", stats['invalid_comments'])
            
        except Exception as e:
            st.error(f"Error during extraction: {str(e)}")
            progress_bar.empty()
            status_text.empty()
    
    # Analysis section
    st.markdown("---")
    st.markdown("### 🧠 Step 2: Generate Sentiment Analysis")
    
    if st.session_state.extraction_complete and st.session_state.current_video_id:
        
        if st.button("📈 Generate Analysis & Charts", type="primary", use_container_width=True):
            video_id = st.session_state.current_video_id
            
            with st.spinner("🔄 Generating sentiment analysis..."):
                video_info, comments_df = get_sentiment_data(video_id)
                
                if video_info is None or comments_df.empty:
                    st.error("No sentiment data found. Please re-extract comments.")
                    return
                
                # Create sentiment summary
                sentiment_summary = create_sentiment_summary(comments_df)
                st.session_state.sentiment_data = sentiment_summary
                
                # Display sentiment analysis results
                show_sentiment_results(video_info, comments_df, sentiment_summary, chart_generator)
    
    elif not st.session_state.extraction_complete:
        st.info("👆 Please extract comments first using Step 1 above")
    
    # Quick analysis for existing videos
    st.markdown("---")
    st.markdown("### 🔍 Or Analyze Previously Extracted Video")
    
    history_df = get_video_history()
    if not history_df.empty:
        selected_video = st.selectbox(
            "Choose a video from history:",
            options=history_df['video_id'].tolist(),
            format_func=lambda x: f"{history_df[history_df['video_id']==x]['title'].iloc[0][:50]}..."
        )
        
        if st.button("📊 Analyze Selected Video", use_container_width=True):
            video_info, comments_df = get_sentiment_data(selected_video)
            
            if video_info is not None and not comments_df.empty:
                sentiment_summary = create_sentiment_summary(comments_df)
                show_sentiment_results(video_info, comments_df, sentiment_summary, chart_generator)
            else:
                st.error("No sentiment data found for this video. It may have been extracted before sentiment analysis was enabled.")
    else:
        st.info("No previously analyzed videos found.")

def show_sentiment_results(video_info, comments_df, sentiment_summary, chart_generator):
    """Display comprehensive sentiment analysis results."""
    
    st.markdown("## 🎯 Sentiment Analysis Results")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Comments", 
            sentiment_summary['total_comments']
        )
    
    with col2:
        positive_pct = sentiment_summary['sentiment_distribution']['positive']['percentage']
        st.metric(
            "Positive Sentiment", 
            f"{positive_pct:.1f}%",
            delta=f"{positive_pct - 33.3:.1f}%" if positive_pct != 33.3 else None
        )
    
    with col3:
        avg_polarity = sentiment_summary['average_scores']['polarity']
        st.metric(
            "Average Polarity", 
            f"{avg_polarity:.3f}",
            help="Range: -1 (negative) to +1 (positive)"
        )
    
    with col4:
        avg_subjectivity = sentiment_summary['average_scores']['subjectivity']
        st.metric(
            "Subjectivity", 
            f"{avg_subjectivity:.3f}",
            help="Range: 0 (objective) to 1 (subjective)"
        )
    
    # Sentiment distribution chart
    st.markdown("### 📊 Sentiment Distribution")
    
    sentiment_dist = sentiment_summary['sentiment_distribution']
    
    # Create pie chart
    labels = []
    values = []
    colors = []
    
    for sentiment, data in sentiment_dist.items():
        if data['count'] > 0:
            labels.append(f"{sentiment.title()} ({data['count']})")
            values.append(data['count'])
            if sentiment == 'positive':
                colors.append('#2ECC71')
            elif sentiment == 'negative':
                colors.append('#E74C3C')
            else:
                colors.append('#95A5A6')
    
    if values:
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values,
            marker_colors=colors,
            textinfo='label+percent',
            textfont_size=12
        )])
        
        fig.update_layout(
            title=f"Sentiment Distribution - {video_info['title'][:50]}...",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment timeline
    if len(comments_df) > 10:
        st.markdown("### 📈 Sentiment Timeline")
        
        # Convert datetime and sort
        comments_df['published_at'] = pd.to_datetime(comments_df['published_at'])
        comments_df_sorted = comments_df.sort_values('published_at')
        
        # Create timeline chart
        fig = px.scatter(
            comments_df_sorted,
            x='published_at',
            y='sentiment_polarity',
            color='sentiment_polarity',
            color_continuous_scale='RdYlGn',
            hover_data=['text'],
            title="Sentiment Over Time"
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_hline(y=0.3, line_dash="dot", line_color="green", opacity=0.5)
        fig.add_hline(y=-0.3, line_dash="dot", line_color="red", opacity=0.5)
        
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Sentiment Polarity",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Comments table
    st.markdown("### 💬 Comments Analysis")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        sentiment_filter = st.selectbox(
            "Filter by sentiment:",
            ["All", "Positive", "Negative", "Neutral"]
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort by:",
            ["Most Recent", "Most Positive", "Most Negative", "Most Liked"]
        )
    
    # Apply filters
    filtered_df = comments_df.copy()
    
    if sentiment_filter != "All":
        filtered_df = filtered_df[filtered_df['sentiment_label'] == sentiment_filter.lower()]
    
    if sort_by == "Most Recent":
        filtered_df = filtered_df.sort_values('published_at', ascending=False)
    elif sort_by == "Most Positive":
        filtered_df = filtered_df.sort_values('sentiment_polarity', ascending=False)
    elif sort_by == "Most Negative":
        filtered_df = filtered_df.sort_values('sentiment_polarity', ascending=True)
    elif sort_by == "Most Liked":
        filtered_df = filtered_df.sort_values('like_count', ascending=False)
    
    # Display table
    if not filtered_df.empty:
        display_df = filtered_df[['text', 'sentiment_label', 'sentiment_polarity', 'like_count', 'author_display_name']].head(10)
        display_df.columns = ['Comment', 'Sentiment', 'Polarity', 'Likes', 'Author']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        st.info(f"Showing top 10 of {len(filtered_df)} comments")
    else:
        st.warning("No comments match the selected filters.")
    
    # Export options
    st.markdown("### 📥 Export Results")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Download Analysis Data (CSV)", use_container_width=True):
            csv = comments_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"sentiment_analysis_{video_info['video_id']}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📋 Download Summary (JSON)", use_container_width=True):
            summary_data = {
                'video_info': dict(video_info),
                'sentiment_summary': sentiment_summary,
                'generated_at': datetime.now().isoformat()
            }
            json_str = json.dumps(summary_data, indent=2)
            st.download_button(
                label="💾 Download JSON",
                data=json_str,
                file_name=f"sentiment_summary_{video_info['video_id']}.json",
                mime="application/json"
            )

def show_history_page():
    """Show video analysis history."""
    
    st.markdown("## 📈 Video Analysis History")
    
    history_df = get_video_history()
    
    if not history_df.empty:
        st.markdown(f"### 📊 Total Videos Analyzed: {len(history_df)}")
        
        # Display history table
        display_df = history_df.copy()
        display_df['extracted_at'] = pd.to_datetime(display_df['extracted_at']).dt.strftime('%Y-%m-%d %H:%M')
        display_df.columns = ['Video ID', 'Title', 'Channel', 'Comments', 'Date']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Quick analysis buttons
        st.markdown("### 🔍 Quick Actions")
        selected_video = st.selectbox(
            "Select a video to analyze:",
            options=history_df['video_id'].tolist(),
            format_func=lambda x: f"{history_df[history_df['video_id']==x]['title'].iloc[0][:60]}..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 View Analysis", use_container_width=True):
                st.session_state.current_video_id = selected_video
                st.rerun()
        
        with col2:
            if st.button("📈 Compare Videos", use_container_width=True):
                st.info("Video comparison feature coming in Phase 4!")
    
    else:
        st.info("No videos analyzed yet. Go to the Analysis page to get started!")

def show_about_page():
    """Show information about the application."""
    
    st.markdown("## ℹ️ About This Application")
    
    st.markdown("""
    ### 🎯 **Project Overview**
    
    The YouTube Comment Sentiment Analyzer is a comprehensive tool that extracts comments from YouTube videos 
    and performs advanced sentiment analysis to help understand public opinion and discussion patterns.
    
    ### 🧠 **Technology Stack**
    
    - **Frontend**: Streamlit (Interactive Web Dashboard)
    - **Sentiment Analysis**: TextBlob + VADER (Dual Analysis)
    - **Data Storage**: SQLite Database
    - **Visualizations**: Plotly Interactive Charts
    - **API Integration**: YouTube Data API v3
    - **Language**: Python 3.8+
    
    ### 🔬 **Analysis Methods**
    
    **TextBlob**: General sentiment analysis with polarity (-1 to +1) and subjectivity (0 to 1) scores
    
    **VADER**: Social media optimized sentiment analysis with compound scores and emotion breakdown
    
    **Combined Approach**: Uses both methods for more accurate and robust sentiment classification
    
    ### 📊 **Features**
    
    ✅ **Real-time Comment Extraction**  
    ✅ **Dual Sentiment Analysis Models**  
    ✅ **Interactive Visualizations**  
    ✅ **Timeline Analysis**  
    ✅ **Data Export Capabilities**  
    ✅ **Video History Management**  
    ✅ **Responsive Web Interface**  
    
    ### 🚀 **Getting Started**
    
    1. Navigate to the **📊 Analyze Video** page
    2. Enter any public YouTube video URL
    3. Click **Extract Comments** and wait for processing
    4. Click **Generate Analysis** to create charts
    5. Explore interactive visualizations and export data
    
    ### 📈 **Coming in Phase 4**
    
    - Advanced emotion detection (joy, anger, sadness, etc.)
    - Multi-video comparison dashboards
    - Topic modeling and keyword trends
    - Real-time sentiment monitoring
    - Custom analytics and insights
    
    ### 💡 **Tips for Best Results**
    
    - Use videos with 50+ comments for meaningful analysis
    - Try different comment ordering (relevance vs time)
    - Export data for deeper analysis in Excel/Python
    - Compare sentiment across different video topics
    
    ---
    
    **Developed with ❤️ using Python & Streamlit**
    """)

if __name__ == "__main__":
    main()
