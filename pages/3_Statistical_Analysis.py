import streamlit as st
import plotly.express as px
from utils import page_setup, takeaway, stat_card, load_eda_data, NAVY, CATEGORICAL_PALETTE, INCOME_ORDER

page_setup("Statistical Analysis")

df = load_eda_data()

st.markdown(
    """
    Normality (Shapiro-Wilk) and variance homogeneity (Levene's test) both failed for every grouping
    tested below, so **non-parametric tests** are used throughout rather than ANOVA/Pearson
    correlation &mdash; the more conservative and defensible choice given the data.
    """
)

# ---------------------------------------------------------------------------
st.markdown("### 1. Income Group vs. Business Density")
c1, c2, c3 = st.columns(3)
with c1:
    stat_card("Kruskal-Wallis H", "1295.43", "p < 0.0001")
with c2:
    stat_card("Effect Size (\u03b5\u00b2)", "0.4446", "Large effect &mdash; ~44% variance explained")
with c3:
    stat_card("Post-hoc", "6 / 6 pairs significant", "Dunn's test, Bonferroni-corrected")

fig = px.box(
    df, x="income_group", y="log_new_business_density", category_orders={"income_group": INCOME_ORDER},
    color="income_group", color_discrete_sequence=CATEGORICAL_PALETTE,
)
fig.update_layout(height=380, showlegend=False, xaxis_title="", yaxis_title="Log New Business Density")
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "**H\u2080**: business density distribution is the same across income groups. **Result**: rejected "
    "&mdash; every income group is statistically distinct from every other, with a large effect size."
)

st.markdown("---")

# ---------------------------------------------------------------------------
st.markdown("### 2. Governance Index vs. Business Density")
c1, c2, c3 = st.columns(3)
with c1:
    stat_card("Spearman's r", "0.680", "p < 0.0001, n = 2,793")
with c2:
    stat_card("95% CI", "(0.660, 0.700)", "Tight interval &mdash; precisely estimated")
with c3:
    stat_card("Rank", "Strongest single predictor", "Of all variables tested")

fig = px.scatter(
    df.sample(min(1500, len(df)), random_state=42), x="governance_index", y="log_new_business_density",
    color="income_group", category_orders={"income_group": INCOME_ORDER}, color_discrete_sequence=CATEGORICAL_PALETTE,
    opacity=0.55, trendline="ols", trendline_scope="overall", trendline_color_override=NAVY,
)
fig.update_layout(height=420)
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "**H\u2080**: no monotonic relationship between governance index and log business density. "
    "**Result**: rejected &mdash; a strong, precisely-estimated positive relationship confirmed via "
    "Spearman's rank correlation (robust to non-normality)."
)

st.markdown("---")

# ---------------------------------------------------------------------------
st.markdown("### 3. Region & Offshore Financial Centers")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Region (Kruskal-Wallis)**")
    stat_card("H = 594.65", "\u03b5\u00b2 = 0.203", "p < 0.0001 &mdash; significant, but weaker than income group, reflecting income diversity within regions")
with c2:
    st.markdown("**Offshore Centers (Mann-Whitney U)**")
    stat_card("Rank-biserial r = \u22120.9998", "Near-perfect separation", "p < 0.0001 &mdash; offshore median density ~5x non-offshore median (4.76 vs. 0.99)")

st.caption(
    "Offshore financial centers are confirmed as a statistically distinct population &mdash; not "
    "high-variance noise &mdash; justifying their explicit flagging rather than being dropped or "
    "blended into general modeling (see Data & Methodology)."
)

takeaway(
    "All three hypothesized relationships are statistically significant with meaningful effect sizes. "
    "Governance quality (r = 0.68) and income group (\u03b5\u00b2 = 0.44) are the two strongest, most robust "
    "drivers of new business density identified in this analysis &mdash; both carried forward as the "
    "backbone of the predictive model on the next page."
)
