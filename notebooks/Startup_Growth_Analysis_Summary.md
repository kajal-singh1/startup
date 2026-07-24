# Startup Growth Analysis — EDA, Statistical Analysis & Modeling Summary

## 1. Project Context

**Dataset**: 217 countries × 21 years (2005–2025), 41 variables, merged from World Bank, UNESCO, and WIPO sources — a balanced panel (every country has all 21 years present).

**Objective**: Understand and predict `new_business_density` (new business registrations per 1,000 people aged 15–64) — chosen over raw `new_businesses_registered` because density is population-normalized, making it comparable across countries of vastly different sizes (e.g., India vs. Iceland), whereas raw counts are dominated by population size alone.

---

## 2. Exploratory Data Analysis (05_eda.ipynb)

### 2.1 Structural Check
Confirmed the panel was perfectly balanced (217 × 21 = 4557 rows, no gaps in country-year coverage) — meaning no country dropped out mid-series, which simplifies later modeling.

### 2.2 Missingness Analysis
- Target variable (`new_business_density`) was 36% missing overall.
- Missingness was **not random (MNAR)** — it clustered by year (2005 and 2025 were ~100% missing due to reporting lag/survey coverage windows) and by country (34 countries had 100% missing target, mostly microstates and low-statistical-capacity states like Syria, Sudan, Eritrea).
- **Decision**: restrict analysis to 2006–2024, and later exclude the 34 fully-missing countries from modeling (they carry zero information for supervised learning).
- **Why this mattered**: naively imputing or ignoring this pattern would have introduced bias — missingness itself correlates with a country's development level, which is also a predictor of the target.

### 2.3 Distribution Analysis
- Target variable was extremely right-skewed (skew = 11.8, kurtosis = 154.7) — driven almost entirely by **Cayman Islands** and **Isle of Man**, both offshore financial centers where business registration reflects global capital flows, not local entrepreneurship, relative to a tiny population.
- **Decision**: log-transform the target (`log1p`), reducing skew to 1.19 — a much more analysis-ready distribution — while flagging offshore centers (`is_offshore_center`) rather than deleting them, preserving information for later analysis.
- Repeated the skewness check across all 40 variables; found most extreme skew concentrated in absolute-scale variables (GDP, population, money supply) — expected, since a few large economies dominate raw counts. Governance indicators (already constructed as normalized indices) were naturally well-behaved.
- `inflation` had a legitimate extreme skew (max 557%, Zimbabwe 2020) — verified these were real hyperinflation crisis events (Zimbabwe, Venezuela, Sudan, South Sudan), not data errors, and used a **signed log transform** to preserve both direction and scale.

### 2.4 Correlation Analysis
- Strongest predictors of target: governance indicators (`regulatory_quality` r=0.67, `government_effectiveness` r=0.63, `rule_of_law` r=0.62, `control_of_corruption` r=0.62) and `log_gdp_per_capita` (r=0.65).
- Weak/surprising finding: `log_patent_applications` (r=0.30) and `log_trademark_applications` (r=0.23) were only weakly correlated with new business formation — a nuanced insight, since innovation output (patents) is often driven by large incumbent firms, not new entrants.

### 2.5 Multicollinearity Diagnosis
- The six WGI governance indicators were severely intercorrelated (pairwise r = 0.66–0.94) — a clear multicollinearity problem that would destabilize regression coefficients if all six were used together.
- **Decision**: resolve via PCA rather than simply dropping variables (a more rigorous, defensible choice for an interview).
  - PC1 explained 86.3% of variance across the six indicators, with all loadings pointing the same direction — confirming a single composite "governance quality" index was a valid simplification.
  - Composite `governance_index` correlated with the target at r=0.656 — nearly matching the best individual raw variable (0.667), with almost no information loss.

### 2.6 Group Segmentation
- Segmented target by income group and region; found a clean, monotonic relationship (Low → Lower-middle → Upper-middle → High income = increasing business density).
- Discovered mean statistics were being heavily distorted by offshore financial centers (e.g., Latin America & Caribbean regional mean dropped from 12.9 to 3.4 once 8 offshore centers were excluded) — reinforced the decision to flag rather than delete these countries, and to prefer median over mean for group summaries.

---

## 3. Statistical Analysis (06_statistical_analysis.ipynb)

Added as an extra phase (not originally planned) to formally validate the patterns EDA surfaced — moving from "this looks true" to "this is statistically confirmed," which strengthens the project's rigor.

### 3.1 Assumption Checks
- Shapiro-Wilk normality tests failed for every income group and region (p < 0.0001 across the board).
- Levene's test confirmed unequal variances across groups (p = 2×10⁻⁵⁴).
- **Decision**: use non-parametric tests (Kruskal-Wallis, Mann-Whitney, Spearman) throughout instead of parametric alternatives (ANOVA, Pearson, t-test), since the normality/variance assumptions required for parametric tests were violated.

### 3.2 Key Hypothesis Tests
| Test | Result | Effect Size | Interpretation |
|------|--------|-------------|-----------------|
| Income group vs. target (Kruskal-Wallis) | H=1295.4, p<0.0001 | ε²=0.44 (large) | Income group explains ~44% of variance in business density; all 6 pairwise group comparisons significant (Dunn's test, Bonferroni-corrected) |
| Governance index vs. target (Spearman) | r=0.68, p<0.0001 | 95% CI: (0.66, 0.70) | Strong, precisely-estimated positive relationship — the strongest single predictor identified |
| Region vs. target (Kruskal-Wallis) | H=594.65, p<0.0001 | ε²=0.20 (large) | Significant but weaker than income group — regions contain internal income diversity |
| Offshore centers vs. rest (Mann-Whitney) | p<0.0001 | rank-biserial = -0.9998 (near-perfect separation) | Offshore centers are a statistically distinct population (median 4.76 vs. 0.99) — confirms they need separate treatment, not deletion |

**Why this phase mattered**: p-values alone (especially with thousands of rows) can make trivial differences look "significant." Reporting effect sizes alongside p-values shows the differences found are not just statistically real but practically meaningful.

---

## 4. Modeling (07_modeling.ipynb)

### 4.1 Approach Decision
Chose **regression** over classification: the target is continuous by nature, and all prior analysis (correlation, PCA) was built around continuous relationships. Classification would have discarded real information for no clear benefit.

### 4.2 Feature Selection
- Initial feature set (8 variables, including `researchers_per_million` and `log_patent_applications`) caused a 66% data loss (2911 → 983 rows) due to sparse reporting of R&D/patent variables.
- **Decision**: dropped the two sparsest, weakest-correlated features, recovering the dataset to 2618 rows while sacrificing minimal predictive power (these had the lowest correlations with target in EDA anyway).
- Final feature set: `governance_index`, `log_gdp_per_capita`, `internet_users`, `unemployment_rate`.

### 4.3 Train/Test Split
Split **by country**, not by row — since this is panel data (multiple years per country), a random row-level split would let the same country appear in both train and test, leaking information and inflating apparent performance.

### 4.4 A Data Integrity Catch
Discovered `is_offshore_center` had a coefficient of exactly 0.000 in the first model — investigated rather than accepted, and found all 38 offshore-center rows had been silently dropped because `governance_index` and `unemployment_rate` are 100% missing for these jurisdictions (WGI and labor-force surveys don't cover microstates like Cayman Islands or Monaco). Documented this explicitly as a **model scope limitation** rather than hiding it — the model is valid for standard-reporting countries (~90% of target-valid data) but does not extend to offshore financial centers.

### 4.5 Model Comparison
| Model | Test R² | CV R² (5-fold) | Notes |
|-------|---------|-----------------|-------|
| Linear Regression | 0.395 | **0.500** | Best generalization, simplest model |
| Ridge (α=1.0) | 0.395 | — | No improvement — limited multicollinearity left to regularize after PCA |
| Random Forest (deep) | 0.331 | 0.468 | Overfits (train R²=0.84 vs test R²=0.33) |
| Random Forest (tuned, shallow) | 0.422 | 0.436 | Overfitting reduced but still underperforms Linear |

**Decision**: selected **Linear Regression** as the final model. Random Forest was given a fair, tuned attempt but consistently underperformed on cross-validation — evidence that the true relationship between these predictors and business density is largely linear/monotonic, not one requiring complex non-linear interactions. This is treated as a genuine finding, not a failed experiment.

**Feature importance (from Random Forest, for interpretability)**: `governance_index` (62%) dominates, followed by `log_gdp_per_capita` (18%), `unemployment_rate` (11%), `internet_users` (10%).

---

## 5. Overall Narrative & Key Takeaways

1. **Governance quality is the single strongest driver** of new business formation across countries — confirmed consistently through correlation (EDA), formal hypothesis testing (Spearman r=0.68, tight CI), and feature importance (62% of Random Forest's explanatory power).
2. **Income group explains a large share of variation** (ε²=0.44) but is itself downstream of governance/institutional quality — richer countries tend to have both.
3. **Missingness in this dataset is structural, not random** — tied to a country's statistical reporting capacity, which itself correlates with development level. This shaped nearly every downstream decision (year restriction, feature selection, model scope).
4. **Offshore financial centers are a real, statistically distinct population** (confirmed three separate times — EDA outlier analysis, hypothesis testing, and the modeling data-loss investigation) requiring separate treatment rather than blending into the main analysis or silently discarding.
5. **Model complexity was tested, not assumed** — Random Forest was a fair contender, but honest comparison showed simpler Linear Regression generalizes better, which is itself a meaningful, defensible conclusion.
6. **~50% of the variance in business density remains unexplained** by governance, GDP, internet access, and unemployment — a reasonable, honest ceiling reflecting real-world complexity (informal economy size, specific policy detail, cultural factors) that no available dataset fully captures.
