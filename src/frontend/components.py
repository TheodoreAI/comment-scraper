"""UI components for the dashboard that combine styles and templates."""

import streamlit as st
from typing import Dict, Any, List, Optional
from .templates.html_templates import (
    DASHBOARD_TEMPLATE,
    METRIC_CARD,
    VIDEO_INFO,
    ANALYSIS_RESULTS,
    ERROR_MESSAGE,
    SUCCESS_MESSAGE,
    LOADING_SPINNER
)
from .templates.styles import ALL_STYLES

def init_styles():
    """Initialize dashboard styles."""
    st.markdown(ALL_STYLES, unsafe_allow_html=True)

def render_dashboard_header(title: str, subtitle: str):
    """Render the main dashboard header."""
    st.markdown(
        DASHBOARD_TEMPLATE.format(
            title=title,
            subtitle=subtitle,
            content=""
        ),
        unsafe_allow_html=True
    )

def render_metric_card(title: str, value: str, trend: Optional[str] = None, trend_class: str = ""):
    """Render a metric card with optional trend indicator."""
    st.markdown(
        METRIC_CARD.format(
            title=title,
            value=value,
            trend=trend or "",
            trend_class=trend_class
        ),
        unsafe_allow_html=True
    )

def render_video_info(
    title: str,
    channel: str,
    thumbnail_url: str,
    views: str,
    likes: str,
    comments: str
):
    """Render video information card."""
    st.markdown(
        VIDEO_INFO.format(
            title=title,
            channel=channel,
            thumbnail_url=thumbnail_url,
            views=views,
            likes=likes,
            comments=comments
        ),
        unsafe_allow_html=True
    )

def render_sentiment_analysis(
    positive_percent: float,
    neutral_percent: float,
    negative_percent: float
):
    """Render sentiment analysis results."""
    st.markdown(
        ANALYSIS_RESULTS.format(
            positive_percent=round(positive_percent, 1),
            neutral_percent=round(neutral_percent, 1),
            negative_percent=round(negative_percent, 1)
        ),
        unsafe_allow_html=True
    )

def show_error(message: str):
    """Display an error message."""
    st.markdown(
        ERROR_MESSAGE.format(message=message),
        unsafe_allow_html=True
    )

def show_success(message: str):
    """Display a success message."""
    st.markdown(
        SUCCESS_MESSAGE.format(message=message),
        unsafe_allow_html=True
    )

def show_loading(message: str = "Loading..."):
    """Display a loading spinner with message."""
    st.markdown(
        LOADING_SPINNER.format(message=message),
        unsafe_allow_html=True
    )

def create_tab_navigation(tabs: List[str]) -> str:
    """Create navigation for dashboard tabs."""
    selected_tab = st.radio("", tabs, horizontal=True)
    return selected_tab

def render_metrics_grid(metrics: Dict[str, Any]):
    """Render a grid of metric cards."""
    cols = st.columns(len(metrics))
    for col, (title, data) in zip(cols, metrics.items()):
        with col:
            value = data.get("value", "")
            trend = data.get("trend")
            trend_class = data.get("trend_class", "")
            render_metric_card(title, value, trend, trend_class)