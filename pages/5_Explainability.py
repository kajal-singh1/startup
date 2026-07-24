import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from utils import page_setup, takeaway, load_predictions, load_eda_data, NAVY, TEAL, CATEGORICAL_PALETTE, FEATURE_LABELS

page_setup("Explainability")

df = load_predictions()
shap_cols = [c for c in df.columns if c.startswith("shap_")]
shap_labels = {c: FEATURE_LABELS.get(c.replace("shap_", ""), c.replace("shap_", "")) for c in shap_cols}

tab1, tab2, tab3 = st.tabs(["SHAP Attribution", "Residual Diagnostics", "Multicollinearity (VIF)"])

# ---------------------------------------------------------------------------
with tab1:
    st.markdown("#### Mean Absolute SHAP Contribution")
    mean_abs = df[shap_cols].abs().mean().sort_values(ascending=True)
    fig = go.Figure(
        go.Bar(
            x=mean_abs.values, y=[shap_labels[c] for c in mean_abs.index], orientation="h",
            marker_color=NAVY,
        )
    )
    fig.update_layout(height=320, xaxis_title="Mean |SHAP value|", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "On average, governance index contributes the most to individual predictions, consistent with "
        "its coefficient magnitude and the Random Forest feature-importance ranking on the Modeling page."
    )

    st.markdown("#### SHAP Value Distribution by Feature")
    melted = df.melt(value_vars=shap_cols, var_name="feature", value_name="shap_value")
    melted["feature"] = melted["feature"].map(shap_labels)
    fig = px.strip(
        melted, x="shap_value", y="feature", color="feature", color_discrete_sequence=CATEGORICAL_PALETTE,
    )
    fig.update_traces(marker=dict(opacity=0.35))
    fig.update_layout(height=380, showlegend=False, xaxis_title="SHAP value (impact on log-predicted density)", yaxis_title="")
    fig.add_vline(x=0, line_dash="dash", line_color="#5A6B72")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Each point is one country-year prediction. Governance index shows both the widest spread and "
        "the clearest separation between strongly positive and strongly negative contributions."
    )

# ---------------------------------------------------------------------------
with tab2:
    st.markdown("#### Predicted vs. Actual")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(
            df, x="log_actual", y="log_predicted", color="split", opacity=0.4,
            color_discrete_map={"train": TEAL, "test": NAVY},
        )
        lims = [df["log_actual"].min(), df["log_actual"].max()]
        fig.add_trace(go.Scatter(x=lims, y=lims, mode="lines", line=dict(color="#B8763E", dash="dash"), name="Perfect fit"))
        fig.update_layout(height=400, xaxis_title="Actual (log)", yaxis_title="Predicted (log)")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Model underpredicts at high business-density values, consistent with a moderate R\u00b2 (~0.50) \u2014 it captures the general trend but compresses the top of the range.")

    with c2:
        df["residual"] = df["log_actual"] - df["log_predicted"]
        fig = px.scatter(df, x="log_predicted", y="residual", color="split", opacity=0.4, color_discrete_map={"train": TEAL, "test": NAVY})
        fig.add_hline(y=0, line_dash="dash", line_color="#B8763E")
        fig.update_layout(height=400, xaxis_title="Predicted (log)", yaxis_title="Residual")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("A mild non-linear pattern is visible \u2014 not pure random scatter.")

    st.markdown("#### Q-Q Plot of Residuals")
    c1, c2 = st.columns([1, 1])
    with c1:
        qq = stats.probplot(df["residual"].dropna(), dist="norm")
        theo, sample = qq[0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=theo, y=sample, mode="markers", marker=dict(color=NAVY, opacity=0.4), name="Residuals"))
        slope, intercept = qq[1][0], qq[1][1]
        fig.add_trace(go.Scatter(x=theo, y=slope * np.array(theo) + intercept, mode="lines", line=dict(color="#B8763E", dash="dash"), name="Normal"))
        fig.update_layout(height=360, xaxis_title="Theoretical quantiles", yaxis_title="Sample quantiles", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Residuals show heavier tails than a normal distribution (mild deviation).")
    with c2:
        st.markdown("**Root Cause: Residual Correlation with Features**")
        root_cause = pd.DataFrame(
            {
                "Feature": ["Unemployment Rate", "GDP per Capita (log)", "Internet Users", "Governance Index"],
                "Correlation with Residual": [-0.248, 0.07, 0.02, -0.02],
            }
        ).sort_values("Correlation with Residual", key=abs, ascending=False)
        st.dataframe(root_cause, use_container_width=True, hide_index=True)
        st.markdown(
            """
            Residuals correlate with unemployment far more than other features &mdash; its relationship
            with business density is likely **non-linear or threshold-based**, not fully captured by a
            single linear term. Linear Regression was still retained as the final model (best on
            cross-validated R\u00b2 among alternatives tested), with this flagged as a candidate for future
            work (e.g., a squared or binned unemployment term).
            """
        )

# ---------------------------------------------------------------------------
with tab3:
    st.markdown("#### Variance Inflation Factor")
    vif = pd.DataFrame(
        {
            "Feature": ["Governance Index", "GDP per Capita (log)", "Internet Users", "Unemployment Rate"],
            "VIF": [1.71, 9.56, 9.12, 2.65],
        }
    )
    fig = go.Figure(go.Bar(x=vif["VIF"], y=vif["Feature"], orientation="h", marker_color=NAVY))
    fig.add_vline(x=10, line_dash="dash", line_color="#B8763E", annotation_text="Conventional threshold")
    fig.update_layout(height=300, xaxis_title="VIF", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "GDP per capita and internet users approach the conventional VIF threshold of 10, reflecting "
        "that wealthier, better-governed countries also tend to have higher internet penetration. "
        "Governance index remains the cleanest, most independent signal in the model."
    )

takeaway(
    "SHAP attribution confirms governance index as the dominant driver of individual predictions, "
    "matching both its coefficient and Random Forest importance. Residual diagnostics reveal a "
    "known limitation \u2014 unemployment's relationship with business density is likely non-linear \u2014 "
    "documented here as a direction for future model refinement rather than hidden."
)
