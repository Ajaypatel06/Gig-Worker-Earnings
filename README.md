# 🛵 Gig Worker Earnings Reality Check
### What Swiggy / Zomato / Blinkit / Zepto / Dunzo Partners Actually Take Home (2021–2025)

<br>

> **Gig workers' real purchasing power fell −19.8% between 2021 and 2025.**
> Nominal earnings barely moved (−2.7%), but India's urban CPI rose +21.4% cumulatively.
> Meanwhile, platform commissions crept from 19.6% → 23.2%. The average delivery partner
> now takes home just **58.2% of gross earnings** — down from 60.1% in 2021.

<br>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![pandas](https://img.shields.io/badge/pandas-2.0-150458?style=flat-square&logo=pandas)](https://pandas.pydata.org)
[![MySQL](https://img.shields.io/badge/SQL-MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Dashboard](https://img.shields.io/badge/Dashboard-Chart.js-FF6384?style=flat-square)](https://chartjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## 📌 Live Dashboard

**[→ Open Interactive Dashboard](https://[your-username].github.io/gig-worker-earnings/)**

Four views — Earnings Waterfall · City & Platform · Real Wage Erosion · Break-Even Calculator.
No login, no install, works offline.

---

## 🔑 Key Findings

| Finding | Number |
|---|---|
| **Real net wage erosion 2021→2025** | **−19.8%** |
| Nominal net earnings change | −2.7% |
| Cumulative CPI inflation | +21.4% |
| Commission creep (all platforms) | 19.6% → 23.2% (+3.6pp) |
| Average take-home of gross | 58.2% |
| Best break-even scenario | 3.4 days (Mumbai · Electric Bike · Zepto) |
| Worst break-even scenario | 8.5 days (Delhi · Petrol Bike · Zomato) |
| Monsoon income loss (Jun–Sep) | ₹1,935/month vs ₹350 rest of year (5.5×) |
| Top 10 earners | All Mumbai · Electric Bike · Zepto or Blinkit |
| Electric bike net advantage | +₹2,639/month vs petrol bike |

---

## 📊 Dataset

| Sheet | Rows | Description |
|---|---|---|
| `Worker_Profiles` | 300 | Demographics · city · zone · platform · vehicle type |
| `Monthly_Earnings` | **18,000** | Gross · all deductions · net · hourly rate (2021–2025) |
| `City_Year_Summary` | 15 | Aggregated city × year metrics + real wage index |
| `Platform_Commission_Rates` | 25 | Commission % per platform per year |
| `Petrol_Prices_Monthly` | 56 | City-level petrol price per litre per month |

**Coverage:** 300 workers × 5 years × 12 months = 18,000 rows  
**Cities:** Mumbai · Delhi · Bangalore  
**Platforms:** Swiggy · Zomato · Blinkit · Zepto · Dunzo  
**Vehicle types:** Electric Bike · Petrol Bike · CNG Bike · Bicycle

---

## 📂 Repository Structure

```
gig_worker_earnings/
│
├── data/
│   ├── raw/                               ← Original Excel (5 sheets)
│   ├── processed/                         ← Cleaned CSVs per sheet
│   └── exports/                           ← Tableau-ready & SQL-ready files
│
├── notebooks/
│   ├── 01_data_validation.py              ← Step 1: 28-check validation suite
│   ├── 02_eda.py                          ← Step 2: 7 EDA charts
│   ├── 03_real_wage_analysis.py           ← Step 3: CPI-adjusted wage erosion
│   └── 04_breakeven_model.py              ← Step 4: Parameterised break-even model
│
├── sql/
│   ├── 01_highest_net_by_platform_city.sql   ← Window RANK() per city
│   ├── 02_monthly_earnings_trend.sql         ← 60-month trend + LAG() MoM/YoY
│   ├── 03_rain_month_impact.sql              ← Rain bucketing + season analysis
│   └── 04_top10_earners_profile.sql          ← Full worker profile deep-dive
│
├── docs/
│   └── index.html                         ← Interactive dashboard (GitHub Pages)
│
├── assets/images/                         ← All 20 charts (PNG, 150 DPI)
├── requirements.txt
└── README.md
```

---

## 🔍 Analysis Steps

### Step 1 — Data Validation (`01_data_validation.py`)

28 automated checks across all 5 sheets: shape validation, null checks, referential integrity, domain values, net earnings formula verification, commission cross-sheet consistency, petrol price coverage, and real wage index sanity. **All 28 passed.**

Notable: `vehicle_cc_or_watt` is a mixed-type column (`110` CC vs `500W` watts) — engineered into two clean columns (`engine_type`, `engine_value`) for downstream analysis.

### Step 2 — Exploratory Data Analysis (`02_eda.py`)

Seven charts examining the full earnings picture:

- **2A** — Gross → Net Waterfall: commission (₹5,756) is the largest single deduction, bigger than fuel + maintenance + rain loss combined
- **2B** — City comparison: Mumbai earns ₹2,755/month more than Delhi in net terms
- **2C/2D** — Platform commission impact + rate creep 2021–2025
- **2E** — Rain seasonality: Jun–Sep monsoon loss is 5.5× the rest of year
- **2F** — Vehicle efficiency: Electric bikes save ₹2,306/month on fuel vs petrol, delivering +₹2,639 more net
- **2G** — Year-on-year: gross grew +3.3% while net fell −2.7%; the gap is commission
- **2H** — Platform × City heatmap with best-in-city rankings

### Step 3 — Real Wage Analysis (`03_real_wage_analysis.py`)

CPI deflation using RBI/MoSPI India Urban CPI (2021 = 100). Monthly interpolation applied for granular accuracy.

```
Nominal net 2021:   ₹15,912
Nominal net 2025:   ₹15,487   (−2.7%)
Cumulative CPI:     +21.4%
Real net 2025:      ₹12,757   (−19.8% in 2021 purchasing power)
```

**Finding:** All three cities and all five platforms converge to real wage index ~80 by 2025 — the erosion is structural (commission + inflation), not city- or platform-specific.

### Step 4 — Break-Even Model (`04_breakeven_model.py`)

Parameterised function computing minimum working days before fixed costs are covered:

```python
breakeven_days = fixed_monthly_costs / avg_net_per_working_day
# where: fixed = fuel + phone + maintenance
```

| Scenario | Break-Even | Monthly Profit |
|---|---|---|
| Mumbai · Electric Bike · 2025 | **3.4 days** | ₹15,786 |
| Mumbai · Petrol Bike · 2025 | 7.5 days | ₹10,327 |
| Delhi · Petrol Bike · 2025 | 8.3 days | ₹8,481 |
| Delhi · Petrol Bike · Monsoon | 9.7 days | ₹7,450 |
| Mumbai · Petrol Bike · 2021 | 6.6 days | ₹11,628 |

The same Mumbai petrol-bike worker went from 6.6 → 7.5 days to break even between 2021 and 2025 — a direct, quantifiable consequence of commission creep. Supports `city`, `vehicle_type`, `year`, `platform`, `monsoon`, `custom_commission_pct`, `custom_fuel_cost`, and `custom_daily_hours` parameters.

### Step 5 — SQL Analysis (`sql/`)

Four production-grade queries tested on SQLite:

| Query | Key SQL Technique | Finding |
|---|---|---|
| `01` — Best platform by city | `RANK() OVER (PARTITION BY city)` | Zepto #1 in Mumbai & Delhi; Blinkit #1 in Bangalore; Zomato last everywhere |
| `02` — Monthly trend | `LAG()` for MoM & YoY · rolling avg | Largest single drop: −12.3% (May→Jun monsoon onset) |
| `03` — Rain impact | `CASE WHEN` bucketing · season flags | Extreme rain (7+ days) cuts net by up to 17% |
| `04` — Top 10 earners | Multi-table `JOIN` · conditional aggregation | All 10: Mumbai + Electric Bike + Zepto or Blinkit |

### Step 6 — Interactive Dashboard (`docs/index.html`)

Single-file HTML dashboard using Chart.js. No server, no dependencies beyond a browser. Four interactive views with live tooltips, animated entries, and a commission-rate slider in the break-even calculator.

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Data wrangling | Python · pandas · NumPy |
| Visualisation | matplotlib · seaborn |
| Database | SQLite · pandas SQL reader |
| Dashboard | Chart.js 4.4 · vanilla JS · CSS Grid |
| Version control | Git · GitHub Pages |
| Source data | Excel (openpyxl) |

---

## 🚀 Quick Start

```bash
git clone https://github.com/[your-username]/gig-worker-earnings.git
cd gig-worker-earnings
pip install -r requirements.txt

# Validate all 5 sheets (28 checks)
python notebooks/01_data_validation.py

# Generate all EDA charts
python notebooks/02_eda.py

# Real wage analysis + CPI deflation
python notebooks/03_real_wage_analysis.py

# Break-even model
python notebooks/04_breakeven_model.py

# Open dashboard (no server needed)
open docs/index.html
```

---

## 📈 Selected Charts

| | |
|---|---|
| ![Waterfall](assets/images/2A_waterfall.png) | ![Real Wage](assets/images/3A_nominal_vs_real.png) |
| **Earnings Waterfall** — Only 58.2% reaches the worker | **Real Wage Index** — −19.8% in purchasing power |
| ![Break-Even](assets/images/4A_breakeven_heatmap.png) | ![Platform Heatmap](assets/images/2H_platform_city_heatmap.png) |
| **Break-Even Grid** — Electric bikes break even in half the time | **Platform × City** — Zepto and Blinkit dominate |

---

## ⚠️ Methodology Notes

**Net Earnings Formula** (verified against all 18,000 rows, tolerance ≤ ₹1):
```
Net = Gross − Platform Commission − Fuel − Phone Data − Maintenance − Rain Income Loss
```

**Real Wage Deflation:** Monthly CPI linearly interpolated between annual RBI/MoSPI anchor points (2021 = 100). Formula: `real_net = nominal_net / CPI_monthly × 100`.

**Break-Even Model:** Fixed costs = fuel + phone + maintenance only. Platform commission is embedded in net earnings as a variable cost. Rain loss excluded from base scenario; monsoon toggle available.

**2025 petrol data:** Covers Jan–Aug 2025 only (8 months). Fuel analysis for 2025 uses available months.

**Dataset:** Synthetic, calibrated to real published averages from NITI Aayog gig worker surveys, IFMR Labour Economics research, and platform T&C disclosures. CPI values are official RBI/MoSPI figures.

---

## 🙋 About

**[Ajay Patel]** — Data Analyst, Mumbai
2.5 years experience · Python (pandas, NumPy) · SQL · Tableau · Excel

[LinkedIn](https://linkedin.com/in/ajay-patel-006may) · [Portfolio](https://your-portfolio.com) · [Email](ajaypatel006may@gmail.com)

---

## 📄 License

MIT — free for educational and portfolio use.
CPI data: © RBI / MoSPI (public domain). Platform commission rates: approximate, sourced from public T&Cs and industry reports.
