import streamlit as st
import pandas as pd
from utils import page_setup, takeaway, load_indicators, load_excluded, load_eda_data

page_setup("Data & Methodology")

st.markdown("### Data Sources")
sources = pd.DataFrame(
    [
        ["World Bank WDI", "World Development Indicators", "Economy, population, labour, digital access", "1960\u2013present, annual"],
        ["World Bank WGI", "Worldwide Governance Indicators", "6 governance dimensions (corruption, rule of law, stability, etc.)", "1996\u2013present, annual"],
        ["UNESCO UIS", "UNESCO Institute for Statistics", "R&D expenditure, researchers per million", "Varies by country"],
        ["WIPO", "World Intellectual Property Organization", "Patent and trademark applications", "1980\u2013present, annual"],
    ],
    columns=["Source", "Full Name", "Indicators Contributed", "Coverage"],
)
st.dataframe(sources, use_container_width=True, hide_index=True)

st.markdown("### Pipeline Stages")
st.markdown(
    """
    | Stage | Notebook | What Happens |
    |---|---|---|
    | 1. Source Audit | `01_data_sources_audit` | Inventory each source's coverage, format, and update frequency before pulling |
    | 2. Cleaning | `02_cleaning` | Standardize country codes, reshape to long format, handle raw missingness |
    | 3. UNESCO Merge | `03a_unesco_merge` | Join R&D/researcher indicators onto the base panel |
    | 4. WIPO Merge | `03b_wipo_merge` | Join patent/trademark indicators using a country-code crosswalk |
    | 5. Quality Check | `04_quality_check` | Post-merge validation: duplicate rows, type checks, range sanity checks |
    | 6. EDA | `05_eda` | Distribution shape, skewness, log transforms, PCA governance index |
    | 7. Statistical Analysis | `06_statistical_analysis` | Formal hypothesis tests (see next page) |
    | 8. Modeling | `07_modeling` | Model comparison and final model selection |
    | 9. Explainability | `08_explainability` | SHAP attribution, residual diagnostics, dashboard export |
    """
)

st.markdown("### Key Methodological Decisions")

with st.expander("Governance Index &mdash; PCA composite of 6 correlated indicators", expanded=True):
    st.markdown(
        """
        The 6 World Governance Indicators are pairwise correlated at r = 0.66&ndash;0.94 &mdash; too
        collinear to enter a regression individually. They were reduced via **PCA** to a single
        `governance_index`:

        - PC1 explains **86.3%** of variance across the 6 indicators, with all loadings the same sign
          (no single indicator dominates)
        - Sign-flipped so higher values = better governance (more intuitive for interpretation)
        - Correlation with the target (log new business density): **r = 0.656** &mdash; nearly matches
          the best individual raw indicator (regulatory quality, r = 0.667), confirming minimal
          information loss while eliminating multicollinearity
        - Valid for 3,641 of 4,123 rows; 482 rows dropped due to missing WGI source data
        """
    )

with st.expander("Offshore Financial Centers &mdash; flagged and scoped out of modeling"):
    excluded_preview = load_excluded()
    st.markdown(
        f"""
        Jurisdictions such as Cayman Islands, Monaco, and similar offshore financial centers report
        extreme, non-comparable business density figures driven by shell-company registration rather
        than genuine entrepreneurial activity. Statistical testing (see Statistical Analysis page)
        confirmed these form a **distinct population** (Mann-Whitney rank-biserial = &minus;0.9998,
        near-perfect separation from standard-reporting countries).

        These centers are explicitly flagged (`is_offshore_center`) rather than silently dropped.
        Separately, **{len(excluded_preview)} countries/territories** were excluded from the analysis
        entirely due to no reported business-density data in the source period &mdash; listed below.
        """
    )
    st.dataframe(excluded_preview, use_container_width=True, hide_index=True, height=220)

with st.expander("Log Transforms &mdash; correcting heavy right-skew"):
    st.markdown(
        """
        `new_business_density`, `gdp_per_capita`, patent/trademark counts, and FDI inflows are all
        heavily right-skewed (a handful of extreme values dominate the raw distribution). Each was
        log-transformed (`log1p`, or signed-log for variables that can be negative) prior to analysis
        and modeling, which is standard practice for this kind of macro-panel data and improves both
        the validity of parametric tests and the stability of linear model coefficients.
        """
    )

st.markdown("### Data Dictionary")
ind = load_indicators()
category_filter = st.multiselect(
    "Filter by category", options=sorted(ind["category"].unique()), default=sorted(ind["category"].unique())
)
st.dataframe(
    ind[ind["category"].isin(category_filter)][["display_name", "variable_name", "category", "unit", "indicator_code"]],
    use_container_width=True,
    hide_index=True,
    height=320,
)

takeaway(
    "Four public data sources were merged into a single 2,600+ row panel. Two deliberate scoping "
    "decisions &mdash; a PCA governance composite and explicit offshore-center flagging &mdash; shape "
    "everything downstream, and are re-validated statistically on the next page rather than assumed."
)
