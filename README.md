# Bengaluru UHI Prediction & Cool-Roof Prioritization

**An end-to-end ML pipeline that turns satellite-derived land cover into a ranked, actionable cool-roof intervention list for the 10 Bengaluru wards where it matters most.**

This project extends the [Bengaluru LST Prediction API](https://github.com/Rupali-Gauravaram/Bengaluru_LST_Prediction_API) from "predict temperature" to "decide where to act." Same model backbone, new emphasis: model diagnostics, residual analysis, and a downstream prioritization output that connects the prediction to a real climate intervention.

---

## Why this exists

Urban Heat Island (UHI) effects in Bengaluru are unevenly distributed across its 198 BBMP wards. Predicting Land Surface Temperature (LST) is only half the problem — the other half is deciding *where* limited cool-roof retrofit budgets should go. This project does both:

1. **Predicts** mean LST per ward from two LULC features (Built-up %, Green Cover %).
2. **Prioritizes** the top 10 wards for cool-roof intervention based on the model's outputs and ward characteristics.

---

## The model

| Item | Value |
|---|---|
| Algorithm | Linear Regression (scikit-learn) |
| Features | `BuiltUp_Pct`, `Green_Pct` |
| Target | `Mean_LST_C` (long-term mean LST in °C, 2022–2024, MODIS-derived) |
| Coefficients | BuiltUp_Pct: **+0.0168**, Green_Pct: **−0.0084**, Intercept: **29.70 °C** |
| Granularity | 198 BBMP wards |
| Resolution | 1 km (MODIS MOD11A2) |

**Interpretation:** every 1 percentage-point increase in built-up area adds ~0.017 °C to mean LST; every 1 percentage-point increase in green cover removes ~0.008 °C. Built-up density has roughly **2× the warming effect** of green cover's cooling effect, per percentage point — a quantified case for retrofitting before reforesting.

### Diagnostics (see /images section in this repo)

- `Correlation_heatmap.png` — feature relationships and target correlation
- `Correlation_inferences.png` — qualitative read of the correlation structure
- `LSTvsGreenCover.png` — the inverse relationship between green cover and LST, visualized
- `Residual_plot.png` — residuals vs fitted, used to validate linear-regression assumptions
- `test_predictions.png` — predicted vs actual LST on the held-out test set

---

## The downstream output: Top 10 Cool-Roof Priority Wards

The model's outputs are combined with ward characteristics to surface the wards where cool-roof retrofits would have the largest absolute impact. See [`BBMP_Cool_Roof_Prioritization_Top_10.csv`](./BBMP_Cool_Roof_Prioritization_Top_10.csv).

| Rank | Ward | Zone | Mean LST (°C) | Built-up % | Green % |
|---|---|---|---|---|---|
| 1 | Rajagopal Nagar | Dasarahalli | 32.6 | 86 | 6 |
| 2 | Peenya Industrial Area | Dasarahalli | 32.4 | 77 | 13 |
| 3 | Laggere | Rajarajeswari Nagar | 32.2 | 96 | 1 |
| 4 | HMT Ward | Rajarajeswari Nagar | 32.1 | 71 | 22 |
| 5 | Lakshmi Devi Nagar | Rajarajeswari Nagar | 32.1 | 81 | 14 |
| 6 | Hegganahalli | Dasarahalli | 32.0 | 96 | 1 |
| 7 | Gali Anjenaya Temple ward | South | 32.0 | 91 | 5 |
| 8 | Jagajivanaramnagar | West | 31.9 | 82 | 16 |
| 9 | Nandini Layout | West | 31.8 | 79 | 15 |
| 10 | Vrisabhavathi Nagar | West | 31.8 | 93 | 1 |

**What the list tells you:** the hottest wards are concentrated in north-west Bengaluru (Dasarahalli, Rajarajeswari Nagar zones), where built-up % consistently exceeds 80% and green cover is in single digits. These are the wards where any climate-adaptation budget should land first.

---

## Data pipeline (summary)

LST extraction pipeline (Google Earth Engine):

1. **Source:** MODIS/061/MOD11A2 — 8-day composite, 1 km resolution
2. **Time window:** 2022-01-01 to 2024-12-31 (3 years, smooths seasonal noise)
3. **Transformation:** `LST_Day_1km` band × 0.02 (MODIS scale factor), Kelvin → Celsius
4. **Temporal aggregation:** mean across all 8-day composites in the window
5. **Spatial aggregation:** `ee.Reducer.mean()` per BBMP ward geometry (198 wards)

LULC extraction (Built-up %, Green %): derived from Sentinel-2 / Dynamic World classifications, aggregated per ward.

Full data documentation in [`DATA.md`](./DATA.md).

---

## Limitations (honest read)

- **1 km MODIS resolution** is suitable for ward-level planning but **not** for building-scale design decisions.
- **LST ≠ ambient air temperature.** This model predicts surface temperature, which is the correct metric for UHI and reflective-roof analysis but should not be presented as "how hot it feels."
- **Two-feature linear model.** Intentionally simple — the goal here is interpretable coefficients, not maximum predictive power. Adding albedo, water proximity, and elevation would likely improve R² but reduce the policy clarity of the current model.
- **Static features.** The model uses long-term mean LULC, so it cannot forecast the effect of *new* development on UHI — it diagnoses the current state.

---

## Project structure

```
bengaluru-uhi-prediction/
├── Bengaluru LST Prediction API.ipynb    # Training notebook + diagnostics
├── LST_predictor.py                      # Flask API entrypoint
├── model_coefficients.json               # Human-readable coefficients
├── BBMP_Cool_Roof_Prioritization_Top_10.csv   # Downstream output
├── Correlation_heatmap.png               # Diagnostic plots
├── Correlation_inferences.png
├── LSTvsGreenCover.png
├── Residual_plot.png
├── test_predictions.png
├── DATA.md                               # Data source + extraction pipeline
├── requirements.txt
├── data/                                 # MODIS + LULC ward-level CSVs
└── model/                                # Trained model artefacts (joblib)
```

---

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
flask==3.1.2
joblib==1.5.2
pandas==2.3.1
scikit-learn==1.7.2
```

### 2. Run the API

```bash
python LST_predictor.py
```

Server starts at `http://127.0.0.1:5000`.

### 3. Make a prediction

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"builtup_pct": 86.0, "green_pct": 6.0}' \
  http://127.0.0.1:5000/predict_lst
```

Expected response:
```json
{"predicted_mean_lst_c": 31.099}
```
(Rajagopal Nagar's profile — matches the top of the priority list.)

---

## Related work

- **[Bengaluru LST Prediction API](https://github.com/Rupali-Gauravaram/Bengaluru_LST_Prediction_API)** — the v1 of this work, focused on the API itself.
- **Part 1: Technical Deep Dive** — [chaiandcode.wordpress.com](https://chaiandcode.wordpress.com/2025/12/12/bengaluru-lst-prediction-api-part-1/)
- **Part 2: Strategic Vision** — [chaiandcode.wordpress.com](https://chaiandcode.wordpress.com/2025/12/12/bengaluru-lst-prediction-api-part-2/)
- **[Bengaluru Quorum](https://linkedin.com/company/bengaluru-quorum)** — the climate-intelligence platform this work feeds into.

---

## Author

**Rupali Gauravaram** — Climate Tech ML Engineer, founder of [Bengaluru Quorum](https://linkedin.com/company/bengaluru-quorum). MSc Climate Resilience & Environmental Sustainability (University of Liverpool, 2024). Currently completing Advanced AI/ML certification at IIT Roorkee (May 2026).

[LinkedIn](https://linkedin.com/in/rupali99) · [GitHub](https://github.com/Rupali-Gauravaram) · [Blog: Chai & Code](https://chaiandcode.wordpress.com)
