# Bengaluru UHI Prediction and Cool-Roof Prioritisation

**I built a regression model that predicts the average land surface temperature of each of Bengaluru's 198 BBMP wards from two land-cover features. I then used it to rank the wards where cool-roof retrofits would be expected to help the most.**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Python](https://img.shields.io/badge/Python-3.10+-blue.svg) ![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-orange.svg) ![Flask](https://img.shields.io/badge/Flask-3.1-lightgrey.svg)

![LST vs Green Cover across Bengaluru wards](./LSTvsGreenCover.png)

---

## Motivation

The Urban Heat Island (UHI) effect is not spread evenly across Bengaluru's wards, and the budget for cooling measures is limited. Predicting ward-level Land Surface Temperature (LST) solves only half of the planning problem. The other half is deciding where to spend a limited budget across very different neighbourhoods.

This project has two goals. The first is a simple model, easy to interpret, that relates ward LST to land use. The second is to turn that model into a ranked list of the wards best suited to cool-roof retrofits. I wanted to show that a model's output can become a recommendation someone can act on.

---

## Data

**Temperature:** LST comes from the **MODIS/061/MOD11A2** product, an 8-day composite at 1 km resolution. I took the `LST_Day_1km` band, applied the MODIS scale factor of 0.02, and converted from Kelvin to Celsius. I used 1 January 2022 to 31 December 2024 to smooth out seasonal and monsoon effects and get a stable long-term mean. The values were averaged over each of the 198 BBMP ward boundaries with `ee.Reducer.mean()` in Google Earth Engine.

**Land use:** built-up percentage and green-cover percentage come from Sentinel-2 Dynamic World classifications, averaged over the same ward boundaries. Full details are in [`DATA.md`](./DATA.md).

The final dataset has 198 rows, each with two features and one target, and no missing values.

---

## Method

I fitted a simple **linear regression** with two features, built-up percentage and green-cover percentage, and ward-level mean LST as the target. The model is built in scikit-learn, trained on a train-test split, and saved with `joblib` so it can be served through a Flask REST API.

I chose linear regression on purpose. The aim was not the highest possible accuracy, but coefficients that can be read and defended in a policy discussion. A more complex model, such as gradient boosting, might give a slightly lower error, but it would hide how much each feature contributes.

To check the model I looked at the residual plot for bias or uneven spread, the correlations between the features and the target, and the performance on the held-out test set.

---

## Results

### Fitted model

| Item | Value |
|---|---|
| Algorithm | Linear Regression |
| Features | `BuiltUp_Pct`, `Green_Pct` |
| Target | `Mean_LST_C` (long-term mean LST in °C, 2022 to 2024) |
| Coefficients | BuiltUp_Pct: **+0.0168**, Green_Pct: **−0.0084** |
| Intercept | **29.70 °C** |
| Granularity | 198 BBMP wards |
| Spatial resolution | 1 km (MODIS MOD11A2) |

How to read the coefficients: one more percentage point of built-up area goes with a 0.017 °C rise in mean LST, and one more percentage point of green cover goes with a 0.008 °C fall. So the built-up effect is about twice the size of the green-cover effect. For policy, this suggests that retrofitting existing built-up areas may give more cooling per unit than the same investment in new green cover.

### Diagnostics

**Correlation between the features and the target:**

![Correlation heatmap](./Correlation_heatmap.png)

![Correlation inferences](./Correlation_inferences.png)

**Residual analysis.** I checked the residual plot to confirm that the errors are spread evenly and show no systematic bias across the range of predictions.

![Residual plot](./Residual_plot.png)

**Predicted vs actual LST on the test set:**

![Test predictions](./test_predictions.png)

### Cool-roof prioritisation

I combined the model output with each ward's features to find the ten wards expected to benefit most from cool-roof retrofits. The output is saved in [`BBMP_Cool_Roof_Prioritization_Top_10.csv`](./BBMP_Cool_Roof_Prioritization_Top_10.csv).

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

The top wards are concentrated in the north-west of the city, in the Dasarahalli and Rajarajeswari Nagar zones. Most are more than 80% built-up with very little green cover. These are areas widely known to be among the hottest parts of the city, which supports the ranking.

---

## Interpretation

### Why a two-feature linear model

Limiting the model to two features and a straight-line relationship reduces accuracy, but it gives an output that can be read and checked. In planning, the key finding is the relative size of the coefficients: built-up density has about twice the temperature effect of green cover per percentage point. That finding matters more than a small gain in accuracy. Adding features such as surface albedo, distance to water, and elevation would probably improve R², but each coefficient would become harder to explain.

### From prediction to a ranked list

Urban-climate ML projects often stop at the prediction and leave out the step that connects it to a decision. The cool-roof ranking here is my attempt at that step. It highlights wards that have both high LST and a land-use profile where cool roofs make sense. It is meant as a starting point for discussion with city stakeholders, not as a final allocation.

---

## Limitations

- **Spatial resolution.** 1 km MODIS data suits ward-level planning but cannot show differences inside a ward. The model should not be used for decisions about single buildings.
- **Surface temperature is not air temperature.** LST is the right measure for reflective-surface measures such as cool roofs, but it is not the air temperature people feel. This needs to be made clear when sharing results with a non-technical audience.
- **Only two features.** Adding albedo, distance to water, and elevation would probably improve accuracy but make the coefficients harder to interpret.
- **Static features.** The inputs are long-term averages. The model describes current conditions and does not forecast the effect of future development.
- **Ward boundaries.** The analysis uses the 198-ward BBMP boundaries, not the current 369-ward Greater Bengaluru Authority boundaries. Re-extracting the data for the new boundaries is the natural next step.

---

## Repository structure

```
bengaluru-uhi-prediction/
├── Bengaluru LST Prediction API.ipynb         # Training notebook with diagnostics
├── LST_predictor.py                           # Flask API entrypoint
├── model_coefficients.json                    # Human-readable model coefficients
├── BBMP_Cool_Roof_Prioritization_Top_10.csv   # Cool-roof ranking output
├── Correlation_heatmap.png                    # Diagnostic plots
├── Correlation_inferences.png
├── LSTvsGreenCover.png
├── Residual_plot.png
├── test_predictions.png
├── DATA.md                                    # Data source and extraction steps
├── requirements.txt
├── data/                                      # MODIS and LULC ward-level CSVs
└── model/                                     # Trained model files (joblib)
```

---

## Reproduction

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

The service starts at `http://127.0.0.1:5000`.

### 3. Request a prediction

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

The values in this example are those of Rajagopal Nagar, the top-ranked ward.

---

## Related work

- **[bengaluru-ward-climate-clustering](https://github.com/Rupali-Gauravaram/bengaluru-ward-climate-clustering)**: K-Means clustering of the same 198 wards into four climate-vulnerability types. It cross-checks the ranking produced here.
- **[Bengaluru_LST_Prediction_API](https://github.com/Rupali-Gauravaram/Bengaluru_LST_Prediction_API)**: the first version of this work, focused on the prediction API alone.
- **Part 1: Technical Deep Dive**: [chaiandcode.wordpress.com](https://chaiandcode.wordpress.com/2025/12/12/bengaluru-lst-prediction-api-part-1/)
- **Part 2: Strategic Vision**: [chaiandcode.wordpress.com](https://chaiandcode.wordpress.com/2025/12/12/bengaluru-lst-prediction-api-part-2/)
- **[Bengaluru Quorum](https://linkedin.com/company/bengaluru-quorum)**: the climate-intelligence platform this analysis was built for.

---

## Author

**Rupali Gauravaram**. MSc Climate Resilience & Environmental Sustainability (University of Liverpool, 2024). Advanced Certification in Data Science & AI (IIT Roorkee).

[LinkedIn](https://linkedin.com/in/rupali99) · [GitHub](https://github.com/Rupali-Gauravaram) · [Blog: Chai & Code](https://chaiandcode.wordpress.com)
