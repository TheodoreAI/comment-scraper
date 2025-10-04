"""CSS styles for the dashboard components."""

# Base styles with CSS variables for theming
BASE_STYLES = """
:root {
    --primary-color: #FF4B4B;
    --secondary-color: #4B4B4B;
    --background-color: #FFFFFF;
    --text-color: #31333F;
    --accent-color: #FF725C;
    --success-color: #28A745;
    --warning-color: #FFC107;
    --error-color: #DC3545;
    --border-radius: 8px;
    --box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
"""

# Dashboard container styles
DASHBOARD_STYLES = """
.dashboard-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.dashboard-header {
    text-align: center;
    margin-bottom: 3rem;
}

.dashboard-header h1 {
    color: var(--primary-color);
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

.dashboard-header .subtitle {
    color: var(--secondary-color);
    font-size: 1.2rem;
}
"""

# Metric card styles
METRIC_STYLES = """
.metric-card {
    background: var(--background-color);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    box-shadow: var(--box-shadow);
    text-align: center;
}

.metric-title {
    color: var(--secondary-color);
    font-size: 1rem;
    margin-bottom: 0.5rem;
}

.metric-value {
    color: var(--text-color);
    font-size: 2rem;
    font-weight: bold;
}

.metric-change {
    font-size: 0.9rem;
    margin-top: 0.5rem;
}

.metric-change.positive {
    color: var(--success-color);
}

.metric-change.negative {
    color: var(--error-color);
}
"""

# Video info styles
VIDEO_INFO_STYLES = """
.video-info-container {
    display: flex;
    gap: 1.5rem;
    background: var(--background-color);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    box-shadow: var(--box-shadow);
    margin-bottom: 2rem;
}

.video-thumbnail {
    flex: 0 0 200px;
}

.video-thumbnail img {
    width: 100%;
    border-radius: var(--border-radius);
}

.video-details {
    flex: 1;
}

.video-details h2 {
    color: var(--text-color);
    margin-bottom: 0.5rem;
}

.channel-name {
    color: var(--secondary-color);
    font-size: 1.1rem;
    margin-bottom: 1rem;
}

.video-stats {
    display: flex;
    gap: 1.5rem;
    color: var(--secondary-color);
}
"""

# Analysis results styles
ANALYSIS_STYLES = """
.analysis-results {
    background: var(--background-color);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    box-shadow: var(--box-shadow);
    margin-bottom: 2rem;
}

.sentiment-distribution {
    display: flex;
    height: 30px;
    border-radius: var(--border-radius);
    overflow: hidden;
    margin-top: 1rem;
}

.sentiment {
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 0.9rem;
}

.sentiment.positive {
    background-color: var(--success-color);
}

.sentiment.neutral {
    background-color: var(--warning-color);
}

.sentiment.negative {
    background-color: var(--error-color);
}
"""

# Message box styles
MESSAGE_STYLES = """
.message-box {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem;
    border-radius: var(--border-radius);
    margin-bottom: 1rem;
}

.message-box .icon {
    font-size: 1.5rem;
}

.message-box.error {
    background-color: #FFF5F5;
    border: 1px solid var(--error-color);
}

.message-box.success {
    background-color: #F0FFF4;
    border: 1px solid var(--success-color);
}

.message-content h4 {
    margin: 0;
    color: var(--text-color);
}

.message-content p {
    margin: 0.5rem 0 0;
    color: var(--secondary-color);
}
"""

# Loading spinner styles
LOADING_STYLES = """
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 2rem;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
"""

# Combine all styles
ALL_STYLES = """
<style>
    {}
    {}
    {}
    {}
    {}
    {}
    {}
</style>
""".format(
    BASE_STYLES,
    DASHBOARD_STYLES,
    METRIC_STYLES,
    VIDEO_INFO_STYLES,
    ANALYSIS_STYLES,
    MESSAGE_STYLES,
    LOADING_STYLES
)