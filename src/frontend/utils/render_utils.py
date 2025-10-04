"""Utility functions for rendering dashboard components."""

import streamlit as st
from typing import List, Dict, Any
from ..styles.dashboard_styles import (
    DASHBOARD_STYLES,
    LOADING_STYLES,
    TABLE_STYLES
)
from ..templates.dashboard_templates import (
    HEADER_TEMPLATE,
    METRIC_CARD_TEMPLATE,
    VIDEO_INFO_TEMPLATE,
    LOADING_SPINNER_TEMPLATE,
    SUCCESS_MESSAGE_TEMPLATE,
    WARNING_MESSAGE_TEMPLATE,
    CHART_CONTAINER_TEMPLATE,
    TABLE_TEMPLATE,
    create_table_header,
    create_table_row
)

def load_dashboard_styles():
    """Load all dashboard styles."""
    st.markdown(DASHBOARD_STYLES, unsafe_allow_html=True)
    st.markdown(LOADING_STYLES, unsafe_allow_html=True)
    st.markdown(TABLE_STYLES, unsafe_allow_html=True)

def render_header(title: str, subtitle: str = ""):
    """Render the dashboard header."""
    st.markdown(
        HEADER_TEMPLATE.format(title=title, subtitle=subtitle),
        unsafe_allow_html=True
    )

def render_metric_card(label: str, value: str):
    """Render a metric card."""
    st.markdown(
        METRIC_CARD_TEMPLATE.format(label=label, value=value),
        unsafe_allow_html=True
    )

def render_metrics_row(metrics: Dict[str, str]):
    """Render a row of metric cards."""
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            render_metric_card(label, value)

def render_video_info(video_data: Dict[str, Any]):
    """Render video information card."""
    st.markdown(
        VIDEO_INFO_TEMPLATE.format(
            title=video_data.get('title', 'N/A'),
            channel=video_data.get('channel', 'N/A'),
            published_date=video_data.get('published_date', 'N/A'),
            comment_count=video_data.get('comment_count', '0')
        ),
        unsafe_allow_html=True
    )

def render_loading_spinner():
    """Render a loading spinner."""
    st.markdown(LOADING_SPINNER_TEMPLATE, unsafe_allow_html=True)

def render_success_message(message: str):
    """Render a success message."""
    st.markdown(
        SUCCESS_MESSAGE_TEMPLATE.format(message=message),
        unsafe_allow_html=True
    )

def render_warning_message(message: str):
    """Render a warning message."""
    st.markdown(
        WARNING_MESSAGE_TEMPLATE.format(message=message),
        unsafe_allow_html=True
    )

def render_chart_container(title: str, chart_function):
    """Render a chart container with title."""
    st.markdown(
        CHART_CONTAINER_TEMPLATE.format(
            title=title,
            chart_content="{chart}"
        ),
        unsafe_allow_html=True
    )
    chart_function()

def render_data_table(data: List[Dict[str, Any]], columns: List[str]):
    """Render a styled data table."""
    header_cells = create_table_header(columns)
    body_rows = ""
    for row in data:
        row_data = [str(row.get(col, '')) for col in columns]
        body_rows += create_table_row(row_data)
    
    st.markdown(
        TABLE_TEMPLATE.format(
            header_cells=header_cells,
            body_rows=body_rows
        ),
        unsafe_allow_html=True
    )