import streamlit as st
import pandas as pd
from utils import page_setup, takeaway, stat_card, load_model, FEATURES_FINAL, FEATURE_LABELS

page_setup("Modeling")

st.markdown("### Scope Note: Offshore Financial Centers")
st.info(
    "All 38 offshore-center rows were dropped during feature preparation &mdash; `governance_index` "
    "and `unemployment_rate` are 100% missing for these jurisdictions (WGI and labor-force surveys "
    "do not cover them). This model is valid for standard-reporting countries only "
    "(2,618 / 2,911 rows, ~90% of target-valid data)."
)

st.markdown("### Model Comparison")
comparison = pd.DataFrame(
    [
        ["Linear Regression", "0.395", "0.500", "Best generalization, simplest model \u2014 selected as final model"],
        ["Ridge (alpha = 1.0)", "0.395", "\u2014", "No improvement \u2014 limited multicollinearity to regularize"],
        ["Random Forest (deep)", "0.331", "0.468", "Overfits (train R\u00b2 = 0.84)"],
        ["Random Forest (tuned)", "0.422", "0.436", "Overfitting reduced, still underperforms Linear on CV"],
    ],
    columns=["Model", "Test R\u00b2", "CV R\u00b2 (5-fold)", "Notes"],
)
st.dataframe(comparison, use_container_width=True, hide_index=True)

c1, c2, c3 = st.columns(3)
with c1:
    stat_card("Final Model", "Linear Regression", "4 features, unscaled")
with c2:
    stat_card("Cross-Validated R\u00b2", "0.500", "5-fold, country-based split")
with c3:
    stat_card("Test R\u00b2", "0.395", "Held-out countries")

st.caption(
    "**Why Linear Regression?** CV R\u00b2 = 0.50 indicates governance, GDP, internet access, and "
    "unemployment jointly explain about half the variance in new business density &mdash; a reasonable "
    "ceiling given unmeasured factors (informal economy, specific policy detail, culture) that no "
    "available dataset fully captures. The relationship is predominantly linear; tree-based models add "
    "complexity without predictive benefit."
)

st.markdown("### Final Model Coefficients")
model = load_model()
coef_df = pd.DataFrame(
    {
        "Feature": [FEATURE_LABELS[f] for f in FEATURES_FINAL],
        "Coefficient": model.coef_,
    }
).sort_values("Coefficient", key=abs, ascending=False)
st.dataframe(coef_df.style.format({"Coefficient": "{:.4f}"}), use_container_width=True, hide_index=True)
st.caption(f"Intercept: {model.intercept_:.4f} &nbsp;|&nbsp; Target: `log_new_business_density` (log1p-transformed)")

st.markdown("### Feature Importance (Random Forest, for interpretability)")
importance = pd.DataFrame(
    {
        "Feature": ["Governance Index", "GDP per Capita (log)", "Unemployment Rate", "Internet Users"],
        "Importance": [0.62, 0.18, 0.11, 0.10],
    }
)
st.bar_chart(importance.set_index("Feature"), horizontal=True, color="#1B4B66")
st.caption("Governance quality is by far the strongest driver &mdash; consistent with the r = 0.68 Spearman result on the Statistical Analysis page.")

st.markdown("---")
st.markdown("### Multicollinearity Check (VIF)")
vif = pd.DataFrame(
    {
        "Feature": [FEATURE_LABELS[f] for f in FEATURES_FINAL],
        "VIF": [1.71, 9.56, 9.12, 2.65],
    }
)
st.dataframe(vif, use_container_width=True, hide_index=True)
st.caption(
    "GDP per capita and internet users show meaningful multicollinearity (VIF \u2248 9, near the "
    "conventional threshold of 10) \u2014 both correlate with each other and with governance quality. "
    "This explains why GDP's coefficient is near-zero despite a strong raw correlation with the "
    "target: its explanatory power is being absorbed by governance and internet access in the "
    "multivariate model. Governance index remains the cleanest, most independent signal (VIF = 1.71)."
)

takeaway(
    "Linear Regression, using just 4 features, was selected over Ridge and Random Forest based on "
    "cross-validated performance (R\u00b2 = 0.50). Governance quality dominates feature importance "
    "(62%) and carries the least multicollinearity risk (VIF = 1.71) \u2014 confirming it as the most "
    "trustworthy driver in this dataset."
)
