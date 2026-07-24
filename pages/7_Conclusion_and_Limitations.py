import streamlit as st
from utils import page_setup, takeaway

page_setup("Conclusion & Limitations")

st.markdown("### Summary of Findings")
st.markdown(
    """
    1. **Governance quality is the dominant driver** of new business formation across countries
       (Spearman r = 0.68; Random Forest importance = 62%; lowest multicollinearity of any feature,
       VIF = 1.71) &mdash; the single most consistent signal across every stage of this analysis.
    2. **Income group** explains a large share of variance in business density (\u03b5\u00b2 = 0.44), with
       every income tier statistically distinct from every other (Dunn's post-hoc, all p < 0.0001).
    3. **Offshore financial centers are a genuinely distinct population**, not high-variance noise
       (Mann-Whitney rank-biserial = &minus;0.9998) &mdash; correctly scoped out of the predictive
       model rather than blended in or silently dropped.
    4. A **4-feature Linear Regression** (governance, GDP per capita, internet access, unemployment)
       achieves CV R\u00b2 = 0.50, outperforming both Ridge and Random Forest on held-out generalization
       &mdash; simplicity won over model complexity for this dataset.
    """
)

st.markdown("### Limitations")
st.markdown(
    """
    - **Model scope**: valid for standard-reporting countries only (2,618 / 2,911 target-valid rows).
      Offshore financial centers require separate, rule-based treatment rather than regression.
    - **Unmodeled non-linearity**: residuals correlate with unemployment rate (r = &minus;0.248) far
      more than other features, suggesting a non-linear or threshold-based relationship not captured
      by a single linear term.
    - **Explained variance ceiling**: CV R\u00b2 = 0.50 leaves roughly half of the variance in new business
      density unexplained &mdash; plausibly reflecting factors no public dataset fully captures, such
      as informal-economy activity, policy specifics, or cultural attitudes toward entrepreneurship.
    - **Residual distribution**: mild heavy-tailed deviation from normality in the Q-Q plot, meaning
      prediction intervals should be treated as approximate rather than exact.
    """
)

st.markdown("### Directions for Future Work")
st.markdown(
    """
    - Add a squared or binned unemployment-rate term to address the non-linear residual pattern
    - Build a separate rule-based classification approach for offshore financial centers
    - Explore panel/fixed-effects models to exploit the repeated country-year structure directly,
      rather than treating observations as independent
    - Extend the governance PCA composite with additional institutional-quality indicators as they
      become available
    """
)

takeaway(
    "Governance quality, not raw economic output, is the strongest and most defensible driver of "
    "new business formation identified in this analysis \u2014 a result that held up consistently "
    "across exploratory analysis, formal hypothesis testing, predictive modeling, and SHAP "
    "attribution, rather than emerging from any single method alone."
)
