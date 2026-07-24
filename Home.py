import streamlit as st
from utils import page_setup, takeaway, stat_card, load_eda_data, NAVY, TEAL

page_setup("Overview")

df = load_eda_data()
n_countries = df["country_code"].nunique()
n_years = df["year"].nunique()
year_min, year_max = int(df["year"].min()), int(df["year"].max())

col1, col2, col3, col4 = st.columns(4)
with col1:
    stat_card("Countries Covered", f"{n_countries}", "World Bank-reporting economies")
with col2:
    stat_card("Time Span", f"{year_min}\u2013{year_max}", f"{n_years} years")
with col3:
    stat_card("Observations", f"{len(df):,}", "Country-year rows")
with col4:
    stat_card("Indicators Merged", "41", "Across 4 source systems")

st.markdown("### Objective")
st.markdown(
    """
    This project examines what drives **new business formation** across countries &mdash; measured
    as new business density (newly registered firms per 1,000 working-age people) &mdash; using a
    panel of macroeconomic, governance, digital-infrastructure, and demographic indicators spanning
    2006&ndash;2024.

    The analysis proceeds in five stages: data collection &amp; cleaning, exploratory analysis,
    formal hypothesis testing, predictive modeling, and model explainability &mdash; each documented
    as a page in this dashboard.
    """
)

st.markdown("### Data Pipeline")
st.markdown(
    """
    <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap; margin: 0.8rem 0 1.2rem 0;">
        <span class="pill">World Bank WDI / WGI</span>
        <span style="color:#5A6B72;">+</span>
        <span class="pill">UNESCO (R&amp;D, Researchers)</span>
        <span style="color:#5A6B72;">+</span>
        <span class="pill">WIPO (Patents, Trademarks)</span>
        <span style="color:#5A6B72;">&rarr;</span>
        <span class="pill">Cleaning &amp; Merge</span>
        <span style="color:#5A6B72;">&rarr;</span>
        <span class="pill">Feature Engineering</span>
        <span style="color:#5A6B72;">&rarr;</span>
        <span class="pill">EDA &amp; Hypothesis Testing</span>
        <span style="color:#5A6B72;">&rarr;</span>
        <span class="pill">Modeling &amp; Explainability</span>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([3, 2])
with col1:
    st.markdown("### Navigating This Dashboard")
    st.markdown(
        """
        Use the sidebar to move through the analysis:

        1. **Data & Methodology** &mdash; sources, cleaning steps, and the offshore-center scoping decision
        2. **EDA** &mdash; distributions, correlations, and interactive country/region exploration
        3. **Statistical Analysis** &mdash; formal hypothesis tests on income, governance, and region
        4. **Modeling** &mdash; model comparison, final model selection, and diagnostics
        5. **Explainability** &mdash; SHAP-based feature attribution and residual analysis
        6. **Predict** &mdash; live business-density prediction from the final model
        7. **Conclusion & Limitations** &mdash; summary findings and scope for future work
        """
    )
with col2:
    st.markdown("### Tech Stack")
    st.markdown(
        """
        <span class="pill">Python 3.10</span>
        <span class="pill">pandas / numpy</span>
        <span class="pill">scikit-learn</span>
        <span class="pill">statsmodels</span>
        <span class="pill">SHAP</span>
        <span class="pill">SciPy</span>
        <span class="pill">Plotly</span>
        <span class="pill">Streamlit</span>
        """,
        unsafe_allow_html=True,
    )

takeaway(
    "A 2,600+ row, 183-country panel dataset built from four independent public-data sources "
    "powers this analysis. Governance quality emerges as the single strongest, most robust driver "
    "of new business formation &mdash; explored in full across the following pages."
)
