# Dataset: Land Surface Temperature (LST) Metrics

**Filename:** `BBMP_Wards_LST_Metrics.csv`  
**Description:**  
This dataset contains the long-term mean Land Surface Temperature (LST) in Celsius for the 198 Bruhat Bengaluru Mahanagara Palike (BBMP) Wards.  
This LST data is the dependent variable (*y*) used to train the UHI prediction model.

---

## 1. Data Extraction Pipeline

The data was extracted and processed using a sophisticated Geospatial Machine Learning (GeoML) workflow implemented primarily in **Google Earth Engine (GEE)**, following these steps:

### **Input Data Source**
- LST data sourced from **MODIS/061/MOD11A2**  
- Provides an **8-day composite** at **1 km spatial resolution**

### **Temporal Filtering**
- Time period: **Jan 1, 2022 – Dec 31, 2024**  
- Chosen to capture a contemporary and climatologically stable average  
- Smooths out short-term weather anomalies

### **Transformation**
- Selected the LST band: `LST_Day_1km`  
- Scaled using MODIS factor: `0.02`  
- Converted from Kelvin to Celsius using:  
  \[
  \text{Celsius} = \text{Kelvin} - 273.15
  \]

### **Temporal Aggregation**
- Aggregated three years of 8-day images  
- Produced a single **Long-Term Mean LST** image for the Bengaluru region

### **Spatial Aggregation**
- Used `ee.Reducer.mean()`  
- Computed the average LST within each of the **198 BBMP Ward geometries**

---

## 2. Constraints and Limitations

The extraction workflow includes several constraints to ensure data quality and relevance:

| **Constraint**          | **Rationale** | **Impact on Project** |
|-------------------------|---------------|------------------------|
| **MODIS Data Source**   | MODIS provides daily LST but at **1 km (~1000 m)** resolution | Suitable for ward-level planning; not for micro-scale design such as building façades |
| **Temporal Span (3 Years)** | Averages out annual variations (e.g., monsoon failures, extreme heat days) | Ensures model coefficients represent stable LULC impacts rather than weather noise |
| **Data Type** | Uses **Land Surface Temperature**, not ambient air temperature | Correct metric for UHI modeling and thermal material efficiency |

---

## 3. Key Column

| Column Name   | Data Type | Description |
|---------------|-----------|-------------|
| **Mean_LST_C** | Float | The mean Land Surface Temperature (°C), averaged for 2022–2024 for each BBMP Ward |

