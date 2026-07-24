import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import page_setup, takeaway, load_eda_data, NAVY, TEAL, CATEGORICAL_PALETTE, INCOME_ORDER

page_setup("Exploratory Data Analysis")

df = load_eda_data()

tab1, tab2, tab3 = st.tabs(["Distributions", "Correlations", "Explore by Country / Region"])

# ---------------------------------------------------------------------------
with tab1:
    st.markdown("#### Target Variable: New Business Density")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(df, x="new_business_density", nbins=50, title="Raw (Heavily Right-Skewed)")
        fig.update_traces(marker_color=NAVY)
        fig.update_layout(height=340, bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(df, x="log_new_business_density", nbins=50, title="Log-Transformed (log1p)")
        fig.update_traces(marker_color=TEAL)
        fig.update_layout(height=340, bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### By Income Group & Region")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.box(
            df, x="income_group", y="log_new_business_density", category_orders={"income_group": INCOME_ORDER},
            color="income_group", color_discrete_sequence=CATEGORICAL_PALETTE, title="By Income Group",
        )
        fig.update_layout(height=380, showlegend=False, xaxis_title="", yaxis_title="Log New Business Density")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        region_order = df.groupby("region")["log_new_business_density"].median().sort_values(ascending=False).index
        fig = px.box(
            df, x="region", y="log_new_business_density", category_orders={"region": list(region_order)},
            color="region", color_discrete_sequence=CATEGORICAL_PALETTE, title="By Region",
        )
        fig.update_layout(height=380, showlegend=False, xaxis_title="", yaxis_title="")
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
with tab2:
    st.markdown("#### Correlation Matrix")
    default_cols = [
        "log_new_business_density", "governance_index", "log_gdp_per_capita", "internet_users",
        "unemployment_rate", "trade_percent_gdp", "population_density", "urban_population_percent",
        "labor_force_participation", "education_expenditure",
    ]
    available_cols = [c for c in default_cols if c in df.columns]
    selected_cols = st.multiselect(
        "Variables to include", options=sorted(df.select_dtypes(include=[np.number]).columns),
        default=available_cols,
    )
    if len(selected_cols) >= 2:
        corr = df[selected_cols].corr(numeric_only=True)
        fig = go.Figure(
            data=go.Heatmap(
                z=corr.values, x=corr.columns, y=corr.columns, zmin=-1, zmax=1,
                colorscale=[[0, "#B8763E"], [0.5, "#FFFFFF"], [1, NAVY]],
                text=np.round(corr.values, 2), texttemplate="%{text}", textfont=dict(size=10),
            )
        )
        fig.update_layout(height=520, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least two variables to render the correlation matrix.")

# ---------------------------------------------------------------------------
with tab3:
    st.markdown("#### Interactive Exploration")
    c1, c2 = st.columns([1, 2])
    with c1:
        regions = sorted(df["region"].unique())
        region_sel = st.multiselect("Region", regions, default=regions)
        df_f = df[df["region"].isin(region_sel)]
        countries = sorted(df_f["country_name"].unique())
        country_sel = st.multiselect("Highlight countries (optional)", countries, default=[])
        x_var = st.selectbox(
            "X-axis variable", ["governance_index", "log_gdp_per_capita", "internet_users", "unemployment_rate"],
            index=0,
        )
    with c2:
        plot_df = df_f.copy()
        plot_df["highlight"] = plot_df["country_name"].isin(country_sel) if country_sel else False
        fig = px.scatter(
            plot_df, x=x_var, y="log_new_business_density", color="income_group",
            category_orders={"income_group": INCOME_ORDER}, color_discrete_sequence=CATEGORICAL_PALETTE,
            hover_data=["country_name", "year"], opacity=0.55,
            title=f"Log New Business Density vs. {x_var.replace('_', ' ').title()}",
        )
        if country_sel:
            hl = plot_df[plot_df["highlight"]]
            fig.add_trace(
                go.Scatter(
                    x=hl[x_var], y=hl["log_new_business_density"], mode="markers", marker=dict(size=11, color="black", symbol="circle-open", line=dict(width=2)),
                    name="Highlighted", text=hl["country_name"] + " (" + hl["year"].astype(str) + ")", hoverinfo="text",
                )
            )
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)

    if country_sel:
        st.markdown("#### Time Trend for Highlighted Countries")
        trend_df = df[df["country_name"].isin(country_sel)].sort_values("year")
        fig = px.line(
            trend_df, x="year", y="new_business_density", color="country_name",
            color_discrete_sequence=CATEGORICAL_PALETTE, markers=True,
        )
        fig.update_layout(height=380, yaxis_title="New Business Density")
        st.plotly_chart(fig, use_container_width=True)

takeaway(
    "New business density is heavily right-skewed and requires a log transform before analysis. "
    "Income group and region both show clear, ordered separation in the log-transformed target, "
    "foreshadowing the formal hypothesis tests on the next page."
)
