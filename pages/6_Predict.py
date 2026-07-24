import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils import page_setup, takeaway, load_model, load_predictions, load_eda_data, NAVY, TEAL

page_setup("Predict")

st.markdown(
    """
    Enter values for the four features used by the final Linear Regression model to generate a live
    prediction of new business density (newly registered firms per 1,000 working-age people).
    """
)

model = load_model()
preds_df = load_predictions()
eda_df = load_eda_data()

# Residual std (log scale) from the shipped predictions, used for an approximate interval.
resid_std = (preds_df["log_actual"] - preds_df["log_predicted"]).std()

st.markdown("### Input Features")
c1, c2 = st.columns(2)
with c1:
    governance_index = st.slider(
        "Governance Index (composite, higher = better governance)", -5.5, 5.5, 0.0, 0.1,
        help="PCA composite of 6 World Governance Indicators. Sample median \u2248 -0.19; typical range -5.3 to 5.0.",
    )
    gdp_per_capita = st.number_input(
        "GDP per Capita (current US$)", min_value=100, max_value=250000, value=6000, step=100,
        help="Sample median \u2248 $5,760. Log-transformed internally before entering the model.",
    )
with c2:
    internet_users = st.slider("Internet Users (% of population)", 0.0, 100.0, 48.0, 0.5)
    unemployment_rate = st.slider("Unemployment Rate (%)", 0.0, 40.0, 6.0, 0.1)

log_gdp_per_capita = np.log1p(gdp_per_capita)

X_input = pd.DataFrame(
    [[governance_index, log_gdp_per_capita, internet_users, unemployment_rate]],
    columns=["governance_index", "log_gdp_per_capita", "internet_users", "unemployment_rate"],
)

log_pred = model.predict(X_input)[0]
pred_density = np.expm1(log_pred)
lower = np.expm1(log_pred - 1.96 * resid_std)
upper = np.expm1(log_pred + 1.96 * resid_std)
pred_density = max(pred_density, 0)
lower = max(lower, 0)

st.markdown("### Prediction")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Predicted New Business Density", f"{pred_density:.2f}")
with c2:
    st.metric("Approx. 95% Interval", f"{lower:.2f} \u2013 {upper:.2f}")
with c3:
    percentile = (eda_df["new_business_density"] < pred_density).mean() * 100
    st.metric("Percentile vs. Historical Data", f"{percentile:.0f}th")

st.caption(
    "The interval is an approximation derived from the held-out residual spread (log scale) of the "
    "final model, not a re-estimated statsmodels prediction interval \u2014 useful for a sense of "
    "uncertainty, not for formal inference."
)

st.markdown("### Where This Prediction Falls")
fig = go.Figure()
fig.add_trace(
    go.Histogram(x=eda_df["new_business_density"].clip(upper=eda_df["new_business_density"].quantile(0.98)),
                 nbinsx=60, marker_color=TEAL, opacity=0.7, name="Historical distribution")
)
fig.add_vline(x=min(pred_density, eda_df["new_business_density"].quantile(0.98)), line_color=NAVY, line_width=3, annotation_text="Your prediction")
fig.update_layout(height=340, xaxis_title="New Business Density", yaxis_title="Country-Year Count", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Model input summary"):
    display_df = X_input.copy()
    display_df.columns = ["Governance Index", "GDP per Capita (log)", "Internet Users (%)", "Unemployment Rate (%)"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.caption(
        f"Raw GDP per capita entered: ${gdp_per_capita:,.0f} \u2192 log1p-transformed to "
        f"{log_gdp_per_capita:.3f} before entering the model, matching the training pipeline."
    )

takeaway(
    "This form runs the same Linear Regression coefficients shown on the Modeling page \u2014 no "
    "shortcuts. Try raising the Governance Index while holding other inputs fixed to see why it's "
    "identified as the dominant driver throughout this analysis."
)
