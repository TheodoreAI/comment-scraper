"""Styles for the dashboard components."""

# Main dashboard styles
DASHBOARD_STYLES = """
<style>
    /* Dashboard Theme Colors */
    :root {
        --primary-color: #FF0000;
        --secondary-color: #1E1E1E;
        --background-light: #f0f2f6;
        --text-primary: #31333F;
        --success-color: #28a745;
        --warning-color: #ffc107;
    }

    /* Main Header Styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Metric Cards */
    .metric-card {
        background-color: var(--background-light);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid var(--primary-color);
        margin: 0.5rem 0;
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: var(--primary-color);
    }

    .metric-label {
        color: var(--text-primary);
        font-size: 1rem;
    }

    /* Message Boxes */
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }

    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }

    /* Section Containers */
    .content-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }

    /* Chart Container */
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }

    /* Form Elements */
    .stTextInput > div > div > input {
        border-radius: 0.3rem;
    }

    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 0.3rem;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #cc0000;
        transform: translateY(-1px);
    }

    /* Video Info Display */
    .video-info {
        background-color: var(--background-light);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    .video-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: var(--text-primary);
    }

    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: var(--primary-color);
    }
</style>
"""

# Loading animation styles
LOADING_STYLES = """
<style>
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
"""

# Data table styles
TABLE_STYLES = """
<style>
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        font-size: 0.9em;
        border-radius: 0.5rem;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
    }

    .styled-table thead tr {
        background-color: var(--primary-color);
        color: white;
        text-align: left;
    }

    .styled-table th,
    .styled-table td {
        padding: 12px 15px;
    }

    .styled-table tbody tr {
        border-bottom: 1px solid #dddddd;
    }

    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f3f3f3;
    }

    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid var(--primary-color);
    }
</style>
"""