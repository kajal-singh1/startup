"""
Shared utilities for the Startup Growth Analysis dashboard.
Centralizes data loading, model loading, color palette, and reusable UI components
so every page renders consistently.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------------------
# Palette & formal chart theme
# ---------------------------------------------------------------------------
NAVY = "#1B4B66"
TEAL = "#4C8C9E"
SLATE = "#5A6B72"
LIGHT_GRAY = "#F4F6F8"
BORDER_GRAY = "#E1E5E8"
ACCENT_WARN = "#B8763E"
TEXT_DARK = "#1A1A1A"

CATEGORICAL_PALETTE = ["#1B4B66", "#4C8C9E", "#8FB8AE", "#B8763E", "#8C6B9E", "#5A6B72", "#C4A35A"]

_formal_template = go.layout.Template()
_formal_template.layout = go.Layout(
    font=dict(family="Arial, Helvetica, sans-serif", color=TEXT_DARK, size=13),
    paper_bgcolor="white",
    plot_bgcolor="white",
    colorway=CATEGORICAL_PALETTE,
    xaxis=dict(showgrid=True, gridcolor=BORDER_GRAY, zeroline=False, linecolor=BORDER_GRAY),
    yaxis=dict(showgrid=True, gridcolor=BORDER_GRAY, zeroline=False, linecolor=BORDER_GRAY),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=40, r=20, t=50, b=40),
)
pio.templates["formal"] = _formal_template
pio.templates.default = "formal"

INCOME_ORDER = ["Low income", "Lower middle income", "Upper middle income", "High income"]


# ---------------------------------------------------------------------------
# Data loading (cached)
# ---------------------------------------------------------------------------
@st.cache_data
def load_eda_data():
    df = pd.read_csv("data/eda_output.csv")
    return df


@st.cache_data
def load_predictions():
    df = pd.read_csv("data/dashboard_predictions_full.csv")
    return df


@st.cache_data
def load_excluded():
    return pd.read_csv("data/excluded_countries.csv")


@st.cache_data
def load_indicators():
    return pd.read_csv("data/indicators.csv")


@st.cache_resource
def load_model():
    return joblib.load("models/final_linear_model.pkl")


@st.cache_resource
def load_scaler():
    return joblib.load("models/feature_scaler.pkl")


FEATURES_FINAL = ["governance_index", "log_gdp_per_capita", "internet_users", "unemployment_rate"]
FEATURE_LABELS = {
    "governance_index": "Governance Index",
    "log_gdp_per_capita": "GDP per Capita (log)",
    "internet_users": "Internet Users (%)",
    "unemployment_rate": "Unemployment Rate (%)",
}


# ---------------------------------------------------------------------------
# Page chrome
# ---------------------------------------------------------------------------
def page_setup(title: str, icon: str = None):
    st.set_page_config(page_title=f"{title} | Startup Growth Analysis", layout="wide")
    _inject_css()
    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-header-title">Startup Growth Analysis</div>
            <div class="app-header-sub">Cross-Country Drivers of New Business Formation, 2006&ndash;2024</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"## {title}")
    st.markdown("<div class='hr-thin'></div>", unsafe_allow_html=True)


def _inject_css():
    st.markdown(
        f"""
        <style>
        .app-header {{
            padding: 0.4rem 0 0.9rem 0;
            border-bottom: 2px solid {NAVY};
            margin-bottom: 1.1rem;
        }}
        .app-header-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: {NAVY};
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }}
        .app-header-sub {{
            font-size: 0.85rem;
            color: {SLATE};
            margin-top: 0.1rem;
        }}
        .hr-thin {{
            border-top: 1px solid {BORDER_GRAY};
            margin: 0.3rem 0 1.1rem 0;
        }}
        .takeaway-box {{
            background-color: {LIGHT_GRAY};
            border-left: 4px solid {NAVY};
            padding: 0.9rem 1.1rem;
            border-radius: 3px;
            margin-top: 1.4rem;
        }}
        .takeaway-label {{
            font-weight: 700;
            color: {NAVY};
            font-size: 0.78rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }}
        .stat-card {{
            background-color: white;
            border: 1px solid {BORDER_GRAY};
            border-radius: 5px;
            padding: 1rem 1.2rem;
        }}
        .stat-card-label {{
            font-size: 0.78rem;
            color: {SLATE};
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .stat-card-value {{
            font-size: 1.55rem;
            font-weight: 700;
            color: {NAVY};
            margin-top: 0.15rem;
        }}
        .stat-card-note {{
            font-size: 0.76rem;
            color: {SLATE};
            margin-top: 0.2rem;
        }}
        .pill {{
            display: inline-block;
            background-color: {LIGHT_GRAY};
            color: {NAVY};
            border: 1px solid {BORDER_GRAY};
            border-radius: 12px;
            padding: 0.15rem 0.7rem;
            font-size: 0.76rem;
            margin-right: 0.4rem;
            margin-bottom: 0.3rem;
        }}
        section[data-testid="stSidebar"] {{
            border-right: 1px solid {BORDER_GRAY};
        }}
        div[data-testid="stMetricValue"] {{
            color: {NAVY};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def takeaway(text: str):
    st.markdown(
        f"""
        <div class="takeaway-box">
            <div class="takeaway-label">Key Takeaway</div>
            <div>{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label: str, value: str, note: str = ""):
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-card-label">{label}</div>
            <div class="stat-card-value">{value}</div>
            <div class="stat-card-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
