"""HTML templates for the dashboard components."""

# Main dashboard header template
HEADER_TEMPLATE = """
<div class="main-header">
    <h1>{title}</h1>
    <p style="font-size: 1.2rem; color: #666;">{subtitle}</p>
</div>
"""

# Metric card template
METRIC_CARD_TEMPLATE = """
<div class="metric-card">
    <div class="metric-value">{value}</div>
    <div class="metric-label">{label}</div>
</div>
"""

# Video info template
VIDEO_INFO_TEMPLATE = """
<div class="video-info">
    <div class="video-title">{title}</div>
    <div style="margin-top: 0.5rem;">
        <span style="color: #666;">Channel:</span> {channel}
    </div>
    <div style="margin-top: 0.3rem;">
        <span style="color: #666;">Published:</span> {published_date}
    </div>
    <div style="margin-top: 0.3rem;">
        <span style="color: #666;">Total Comments:</span> {comment_count}
    </div>
</div>
"""

# Loading spinner template
LOADING_SPINNER_TEMPLATE = """
<div style="display: flex; justify-content: center; align-items: center; padding: 2rem;">
    <div class="loading-spinner"></div>
</div>
"""

# Success message template
SUCCESS_MESSAGE_TEMPLATE = """
<div class="success-message">
    <i class="fas fa-check-circle"></i> {message}
</div>
"""

# Warning message template
WARNING_MESSAGE_TEMPLATE = """
<div class="warning-message">
    <i class="fas fa-exclamation-triangle"></i> {message}
</div>
"""

# Chart container template
CHART_CONTAINER_TEMPLATE = """
<div class="chart-container">
    <h3 style="margin-bottom: 1rem;">{title}</h3>
    {chart_content}
</div>
"""

# Data table template
TABLE_TEMPLATE = """
<table class="styled-table">
    <thead>
        <tr>
            {header_cells}
        </tr>
    </thead>
    <tbody>
        {body_rows}
    </tbody>
</table>
"""

def create_table_header(columns):
    """Create table header HTML from column list."""
    return "".join([f"<th>{col}</th>" for col in columns])

def create_table_row(row_data):
    """Create table row HTML from row data."""
    return f"<tr>{''.join([f'<td>{cell}</td>' for cell in row_data])}</tr>"