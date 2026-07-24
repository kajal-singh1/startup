# Startup Growth Analysis Dashboard

A Streamlit dashboard presenting the full pipeline for a cross-country study of new business
formation: data sources & methodology, EDA, statistical hypothesis testing, model comparison,
SHAP-based explainability, and a live prediction tool.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run Home.py
```

The app opens at `http://localhost:8501` with sidebar navigation across 8 pages.

## Structure

```
Home.py                              # Overview page (entry point)
pages/
  1_Data_and_Methodology.py
  2_EDA.py
  3_Statistical_Analysis.py
  4_Modeling.py
  5_Explainability.py
  6_Predict.py
  7_Conclusion_and_Limitations.py
utils.py                             # Shared data loading, styling, reusable UI components
data/                                # CSV data files (predictions, EDA output, exclusions, indicators)
models/                              # final_linear_model.pkl, feature_scaler.pkl
.streamlit/config.toml               # Light/formal theme
```

## Note on model files

`models/final_linear_model.pkl` and `models/feature_scaler.pkl` were regenerated from the
`07_modeling` / `08_explainability` notebook logic — the originals in the source project had been
accidentally pickled as `.feature_names_in_` arrays rather than the fitted objects. The regenerated
model was verified to reproduce `data/dashboard_predictions_full.csv` to floating-point precision.
