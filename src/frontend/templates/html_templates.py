"""HTML templates for the dashboard components."""

# Main dashboard layout template
DASHBOARD_TEMPLATE = """
<div class="dashboard-container">
    <div class="dashboard-header">
        <h1>{title}</h1>
        <p class="subtitle">{subtitle}</p>
    </div>
    {content}
</div>
"""

# Metric card template
METRIC_CARD = """
<div class="metric-card">
    <h3 class="metric-title">{title}</h3>
    <div class="metric-value">{value}</div>
    <div class="metric-change {trend_class}">{trend}</div>
</div>
"""

# Video info template
VIDEO_INFO = """
<div class="video-info-container">
    <div class="video-thumbnail">
        <img src="{thumbnail_url}" alt="Video thumbnail">
    </div>
    <div class="video-details">
        <h2>{title}</h2>
        <p class="channel-name">{channel}</p>
        <div class="video-stats">
            <span>👁️ {views}</span>
            <span>👍 {likes}</span>
            <span>💬 {comments}</span>
        </div>
    </div>
</div>
"""

# Analysis results template
ANALYSIS_RESULTS = """
<div class="analysis-results">
    <h3>Sentiment Analysis Results</h3>
    <div class="sentiment-distribution">
        <div class="sentiment positive" style="width: {positive_percent}%">
            <span>Positive {positive_percent}%</span>
        </div>
        <div class="sentiment neutral" style="width: {neutral_percent}%">
            <span>Neutral {neutral_percent}%</span>
        </div>
        <div class="sentiment negative" style="width: {negative_percent}%">
            <span>Negative {negative_percent}%</span>
        </div>
    </div>
</div>
"""

# Error message template
ERROR_MESSAGE = """
<div class="message-box error">
    <span class="icon">⚠️</span>
    <div class="message-content">
        <h4>Error</h4>
        <p>{message}</p>
    </div>
</div>
"""

# Success message template
SUCCESS_MESSAGE = """
<div class="message-box success">
    <span class="icon">✅</span>
    <div class="message-content">
        <h4>Success</h4>
        <p>{message}</p>
    </div>
</div>
"""

# Loading spinner template
LOADING_SPINNER = """
<div class="loading-container">
    <div class="spinner"></div>
    <p>{message}</p>
</div>
"""