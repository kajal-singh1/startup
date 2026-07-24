# Data Sources and Collection Methodology
## Startup Growth Analytics System

**Final dataset:** `data/master/startup_master_dataset.csv`
**Structure:** 217 countries × 21 years (2005–2025) = 4,557 rows, 41 variables
**Principle followed throughout:** every variable in this dataset comes from a real, publicly
documented, official source. Where a genuinely complete free source did not exist (startup
funding/deal-count panels), the variable was substituted with the closest real, defensible
proxy rather than filled with synthetic or scraped data — this is documented explicitly in
Section 4 below.

---

## 1. Data Sources Overview

| # | Source | Provider | Access Method | Variables Contributed | Coverage |
|---|---|---|---|---|---|
| 1 | World Bank World Development Indicators (WDI) | World Bank | REST API (`api.worldbank.org/v2`) | 26 core economic, demographic, digital, financial, education indicators | 217 countries, 2005–2025 |
| 2 | World Bank Worldwide Governance Indicators (WGI) | World Bank | REST API (`api.worldbank.org/v2`, source=75, post-2025 revision) | 6 governance dimensions | 217 countries, ~84% avg. coverage |
| 3 | World Bank Entrepreneurship Database | World Bank | REST API (`api.worldbank.org/v2`) | `new_business_density`, `new_businesses_registered` | 217 countries, ~64% coverage |
| 4 | UNESCO Institute for Statistics (UIS) | UNESCO | Live REST API via `unesco_reader` Python package | `researchers_per_million` | 190/217 countries, 32.9% coverage |
| 5 | WIPO IP Statistics Data Center | World Intellectual Property Organization | Manual CSV export (no public bulk/API access) | `patent_applications`, `trademark_applications` | 177–186/217 countries, ~57–61% coverage |

All five sources are official international statistical agencies (World Bank, UNESCO, WIPO —
all UN-affiliated or Bretton Woods institutions). No commercial, scraped, or user-generated
data sources were used.

---

## 2. Source-by-Source Detail

### 2.1 World Bank — World Development Indicators (WDI)

- **What it is:** the World Bank's primary cross-country statistical database, covering
  economic, demographic, social, and infrastructure indicators.
- **Access:** `https://api.worldbank.org/v2/country/all/indicator/{CODE}?format=json&per_page=20000`
  — no authentication required.
- **26 indicators pulled**, spanning: Economic (GDP, GDP growth, inflation, FDI, trade,
  gross capital formation), Demographics (population, growth, density, urbanization,
  labor force, unemployment), Digital (internet users, mobile/broadband subscriptions,
  secure servers), Finance (domestic credit, broad money), Education (expenditure,
  tertiary enrollment, R&D expenditure), and Environment (renewable energy share, CO2
  per capita).
- **Known issue and resolution:** the World Bank retired `EN.ATM.CO2E.PC` (legacy CO2
  per-capita series) during this project. Replacement: `EN.GHG.CO2.PC.CE.AR5` (EDGAR/AR5
  methodology), validated against known real-world magnitudes (USA ~13–16 t/capita,
  India ~1.7–2.2 t/capita) before adoption.

### 2.2 World Bank — Worldwide Governance Indicators (WGI)

- **What it is:** six composite governance indices — Voice & Accountability, Political
  Stability, Government Effectiveness, Regulatory Quality, Rule of Law, Control of
  Corruption — aggregated from multiple underlying data sources by the World Bank.
- **Access:** same REST API as WDI. **Note:** during this project, WGI underwent a 2025
  methodology revision (recalculated history back to 1996) and was re-hosted under a new
  source parameter. Values remain on the familiar -2.5 to +2.5 scale (validated by range
  check: observed min/max across all six indicators fell within -3.05 to +2.40, consistent
  with the documented scale).
- **Scale:** continuous index, approximately -2.5 (weak) to +2.5 (strong) governance
  performance.

### 2.3 World Bank — Entrepreneurship Database

- **What it is:** the World Bank's own database of newly-registered limited-liability
  firms per country per year — the standard academic proxy for entrepreneurial/startup
  activity used when private funding-panel data is unavailable.
- **Variables:** `new_business_density` (new registrations per 1,000 people aged 15–64,
  code `IC.BUS.NDNS.ZS`) and `new_businesses_registered` (raw count, code `IC.BUS.NREG`).
- **Role in this dataset:** this is the real, quantitative backbone of the "Startup" block
  — see Section 4 for why this replaced the originally planned funding/unicorn variables.

### 2.4 UNESCO Institute for Statistics (UIS)

- **What it is:** UNESCO's statistical office for education, science, and culture data.
- **Variable:** `researchers_per_million` — SDG indicator 9.5.2, "Researchers (in
  full-time equivalent) per million inhabitants," indicator code `RESDEN.INHAB.TFTE`.
- **Access method:** UNESCO's older Bulk Data Download Service (dated ZIP files) proved
  unreliable — hosting paths changed during this project. Switched to the **live UIS Data
  API** (`api.uis.unesco.org`), accessed via the maintained `unesco_reader` Python package.
  The correct indicator ID was confirmed by querying UNESCO's own live indicator catalog
  and text-matching on "researcher," rather than assumed from documentation.
- **Coverage caveat:** R&D personnel surveys are not conducted annually or universally —
  32.9% coverage (190/217 countries with at least one data point) reflects genuine
  reporting sparsity, not a pipeline defect.

### 2.5 WIPO — IP Statistics Data Center

- **What it is:** the World Intellectual Property Organization's statistics on patent and
  trademark filing activity by country.
- **Variables:** `patent_applications`, `trademark_applications` — **Total count by
  applicant's origin** (resident + abroad filings combined), Indicator 1 ("Total
  applications"), **not** filtered to any specific technology domain.
- **Access method:** **manual export only** — WIPO does not provide a public bulk-download
  or REST API for this dataset (confirmed by direct investigation; contrast with World
  Bank/UNESCO, which do). Exported via `https://www3.wipo.int/ipstats` as CSV, all
  countries, "Total count by applicant's origin," Type = "Total."
- **Why "by applicant's origin" instead of "by filing office":** filing-office counts are
  dominated by the handful of large offices (USPTO, CNIPA, EPO, JPO) receiving
  applications from all over the world, and say little about most countries' own
  innovation activity. Origin-based counts measure what a country's own residents filed,
  anywhere in the world — the correct measure for a per-country innovation variable.
- **Coverage caveat:** meaningful year-by-year data is denser from ~2015 onward for most
  countries; earlier years are sparser, reflecting WIPO's own reporting depth.

---

## 3. Country Identification and Filtering

- **Real countries only.** World Bank's raw API output mixes sovereign countries with
  regional/income-group aggregates (`WLD`, `EAS`, `OECD`, `High income`, etc.) in the same
  `country_code` field. These were removed by cross-referencing every entity against World
  Bank's own country-metadata endpoint (`api.worldbank.org/v2/country`), which tags each
  entity's `region` as `"Aggregates"` or a real region — rather than filtering by code
  pattern, which is not reliable (aggregate codes are not distinguishable by format alone).
- **Final country count: 217**, matching World Bank's standard sovereign/economy list.
- **Code standardization.** World Bank and UNESCO both report using ISO 3166-1 **alpha-3**
  codes (`AFG`, `IND`, `USA`). WIPO's export uses ISO **alpha-2** codes (`AF`, `IN`, `US`)
  — converted to alpha-3 via World Bank's own country-metadata table before merging, to
  avoid a silent zero-match failure.

## 4. Startup-Specific Data: Documented Limitation and Resolution

The original project scope anticipated startup-specific variables: `startup_count`,
`total_funding_usd`, `number_of_deals`, `average_deal_size`, `unicorn_count`,
`startup_ecosystem_rank`. Investigation established that **no free, complete, real
country-year panel of startup funding/deal data exists** covering 2005–2025 across 217
countries. Available alternatives were evaluated and rejected or scoped down as follows:

| Candidate source | Verdict |
|---|---|
| Crunchbase (Kaggle snapshot) | Real, but stale — data cuts off ~2013/2014 |
| CB Insights / Wikipedia unicorn lists | Real, but a current snapshot only, not a time series |
| "Startup Valuation Dataset" (Kaggle) | **Explicitly synthetic/simulated** — excluded on principle |
| StartupBlink / Startup Genome (GSER) rankings | Real, but only top ~40–100 countries, only ~2017/2020 onward |
| Global Entrepreneurship Monitor (GEM) | Real, survey-based, but only ~50–100 countries/year |
| Crunchbase Pro / Dealroom / PitchBook | Real and complete, but **paid**, not accessible for this project |

**Resolution:** the World Bank Entrepreneurship Database (`new_business_density`,
`new_businesses_registered` — see Section 2.3) was adopted as the dataset's real
quantitative "startup" measure. It is not a direct measure of venture-funded startup
activity; it measures formal new-business registration, the standard academic proxy used
in entrepreneurship research precisely when funding-panel data is unavailable. This
substitution is a deliberate, documented methodological choice, not an oversight — it
should be stated explicitly in the thesis methodology section, alongside the reasoning
above.

---

## 5. Data Quality Assurance

Every merge step was independently verified before being accepted into the pipeline:

1. **Aggregate filtering** verified against World Bank's authoritative country metadata
   (not assumed from code patterns).
2. **Row-count integrity** checked at every stage: final dataset holds exactly
   217 × 21 = 4,557 rows, with zero duplicate (country, year) pairs — confirmed via
   `.duplicated()` checks, not assumed from successful execution.
3. **Dtype validation**: every indicator column confirmed as numeric (float), not
   accidentally parsed as text.
4. **Merge-artifact check**: verified no duplicate columns (`_x`/`_y` suffixes) from
   repeated merge operations — one such issue (patent/trademark columns merged twice) was
   caught and corrected during development.
5. **Missing-value audit**: every column's missing-data rate was computed and reviewed
   (range: 0%–67.1%) to distinguish genuine source sparsity (UNESCO, WIPO, WGI) from
   pipeline defects.
6. **Range sanity checks**: min/max per variable reviewed for plausibility (e.g., governance
   indices within their documented -2.5 to +2.5 scale; CO2 per capita matching known
   real-world country-level magnitudes).

## 6. Known Data Characteristics for Downstream Analysis

- **Missingness is source-dependent, not random.** UNESCO (67.1% missing) and WIPO
  (38.7–42.9% missing) are the sparsest columns, reflecting genuine reporting gaps rather
  than data loss. This should inform imputation strategy (or exclusion) decisions in the
  modeling phase rather than being treated as uniform missing-completely-at-random data.
- **`tertiary_enrollment` can exceed 100%.** This is a known, legitimate World Bank
  definitional quirk (gross enrollment ratio counts over-age/under-age enrolled students
  against the standard-age population denominator), not a data error.
- **A small number of extreme values remain unexamined at the outlier level**
  (e.g., `fdi_net_inflows` has a large negative minimum; `researchers_per_million` has a
  very high maximum, likely driven by a small-population country). These are flagged for
  the EDA/outlier-analysis phase, not resolved here — Section 5's checks confirm structural
  and type correctness, not the absence of legitimate statistical outliers.

---

*This document should be cited/adapted directly into the "Data Collection and Sources"
section of the project's methodology chapter.*
