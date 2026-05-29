---
name: explain-model
description: Generate SHAP explanations for the categorization or anomaly model. Use when the user asks "explain this prediction", "why was X flagged", or wants per-prediction interpretability, feature importance plots, or insight summaries grounded in SHAP values.
---

# SHAP Explanation Workflow

## Standard procedure
1. Load the trained model from models/<model_name>.joblib.
2. Build a shap.Explainer matched to the model type:
   - Tree models (XGBoost, LightGBM, RandomForest) -> shap.TreeExplainer
   - Linear models                                 -> shap.LinearExplainer
   - Anything else                                 -> shap.Explainer (auto)
3. Compute shap_values on the requested rows.
4. Return BOTH:
   - A plain-English sentence per insight, e.g.:
     "Dining was 28% over your 3-month average. The biggest driver was
      a $74 charge at OSMOW'S on Saturday."
   - A Plotly figure (NOT matplotlib) suitable for embedding in Streamlit.

## Rules
- Always handle the multi-class case (check shap_values shape;
  list-of-arrays for multiclass tree models).
- Cache the explainer in Streamlit with @st.cache_resource keyed on
  the model file's mtime.
- Round monetary values to 2 decimals in the user-facing sentence.
- If SHAP cannot run (e.g., unsupported model), fall back to permutation
  importance from sklearn and LABEL the chart accordingly — don't silently
  return a misleading explainer.
- Save generated explanation artifacts to reports/explanations/<date>/.

## Output paths
- Figures:   reports/explanations/<YYYY-MM-DD>/<insight_name>.png
- Summaries: reports/explanations/<YYYY-MM-DD>/<insight_name>.md
