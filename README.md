# 🛵 Gig Worker Earnings Reality Check
### Modelling What Delivery Partners Actually Take Home (2021–2025)

<br>

> **Note:** this project uses a **synthetic dataset**, generated to match publicly
> reported averages (NITI Aayog gig worker surveys, industry commission reports)
> and official CPI figures. It models a plausible earnings pattern for delivery
> partners across Swiggy, Zomato, Blinkit, Zepto and Dunzo — it is not scraped or
> real worker data. Read this as a methodology and analysis project, not a
> factual claim about any specific platform or worker.

<br>

> **Modelled finding:** in this dataset, real (inflation-adjusted) net earnings fall
> **19.8%** between 2021 and 2025, even though nominal earnings barely move (−2.7%).
> Over the same period, modelled platform commission rises from 19.6% to 23.2%,
> and take-home share of gross earnings falls from 60.1% to 56.6%.

<br>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![pandas](https://img.shields.io/badge/pandas-2.0-150458?style=flat-square&logo=pandas)](https://pandas.pydata.org)
[![SQL](https://img.shields.io/badge/SQL-MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Dashboard](https://img.shields.io/badge/Dashboard-Power%20BI-F2C811?style=flat-square&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## 📌 Project Overview

An end-to-end analysis of a modelled gig delivery earnings dataset covering
Mumbai, Delhi and Bangalore, 2021–2025, across five platforms and four
vehicle types.

**Questions this project answers:**
- After platform commission, fuel, maintenance and monsoon downtime, how much
  of gross earnings does a worker actually keep?
- How does commission creep compare with inflation in eroding real income?
- How many working days does a worker need each month to cover fixed costs,
  and how does that vary by city and vehicle type?
- Which combination of city, platform and vehicle produces the best modelled
  outcome?

---

## 🔑 Key Findings (modelled)

| Finding | Value |
|---|---|
| Real net wage change, 2021→2025 | **−19.8%** |
| Nominal net earnings change | −2.7% |
| Cumulative CPI (2021 base) | +21.4% |
| Commission creep, all platforms | 19.6% → 23.2% |
| Take-home share of gross, 2021 vs 2025 | 60.1% → 56.6% |
| Fastest break-even, 2025 | 2.9 days (Mumbai, electric bike) |
| Slowest break-even, 2025 | 6.0 days (Delhi, petrol bike) |
| Monsoon (Jun–Sep) rain-loss vs rest of year | 5.5× higher |
| Electric bike vs petrol bike, net/month | +₹2,639 |

*Break-even and real-wage figures were recomputed after fixing two errors in
the original scripts (a double-counted break-even cost, and a CPI method that
didn't match the −19.8% headline) — see Methodology Notes.*

---

## 📊 Dataset

| Sheet | Rows | Description |
|---|---|---|
| `Worker_Profiles` | 300 | Demographics · city · zone · platform · vehicle type |
| `Monthly_Earnings` | 18,000 | Gross · all deductions · net · hourly rate (2021–2025) |
| `City_Year_Summary` | 15 | Aggregated city × year metrics |
| `Platform_Commission_Rates` | 25 | Commission % per platform per year |
| `Petrol_Prices_Monthly` | 56 | City-level petrol price per litre per month |
| `Date_Table` | 60 | Date dimension for Power BI |

**Coverage:** 300 workers × 5 years × 12 months = 18,000 rows
**Cities:** Mumbai · Delhi · Bangalore
**Platforms:** Swiggy · Zomato · Blinkit · Zepto · Dunzo
**Vehicle types:** Electric Bike · Petrol Bike · CNG Bike · Bicycle

---

## 📂 Repository Structure

> ⚠️ **Fill this in with your real folder/file names before pushing** — this is
> a best guess based on the files you've shared with me. If a file below lives
> somewhere else in your repo, move it or edit this tree to match reality.

```
Gig-Worker-Earnings/
│
├── Python/
│   ├── data_validation.py          ← Step 1: validation checks
│   ├── eda.py                      ← Step 2: EDA charts
│   ├── 03_real_wage_analysis.py    ← Step 3: CPI-adjusted wage erosion (fixed)
│   └── 04_breakeven_model.py       ← Step 4: break-even model (fixed)
│
├── SQL/
│   └── Queries.sql                 ← 7 business queries (MySQL)
│
├── Power BI/
│   ├── Gig_Worker_Earnings.pbix    ← Dashboard file
│   └── PowerBI_Build_Guide.pdf     ← Build guide, 20 DAX measures
│
├── Validation/
│   └── (validation outputs, if any)
│
├── EDA/
│   └── (EDA outputs/charts, if any)
│
├── gig_worker_data.xlsx            ← Source data, all sheets
├── requirements.txt
└── README.md
```

---

## 🔍 Analysis Steps

### Step 1 — Data Validation (`Python/data_validation.py`)
28 automated checks: shape validation, null checks, referential integrity,
domain values, net-earnings formula verification, commission cross-sheet
consistency, petrol price coverage.

### Step 2 — Exploratory Data Analysis (`Python/eda.py`)
Charts covering the gross-to-net breakdown, city and platform comparisons,
rain seasonality, and vehicle-type efficiency.

### Step 3 — Real Wage Analysis (`Python/03_real_wage_analysis.py`)
Net earnings deflated using annual CPI (2021 = 100).
```
Nominal net 2021 → 2025:   ₹15,912 → ₹15,487   (−2.7%)
Cumulative CPI:            +21.4%
Real wage index 2025:      80.2   (−19.8% in 2021 purchasing power)
```
All three cities and all five platforms land at a real wage index of
79–81 by 2025 — the erosion is structural (commission + inflation), not
specific to one city or platform.

### Step 4 — Break-Even Model (`Python/04_breakeven_model.py`)
```
breakeven_days = fixed_costs / contribution_per_day
contribution_per_day = (gross − commission − rain_loss) / working_days
```
| Scenario | Break-Even | Monthly Net |
|---|---|---|
| Mumbai · Electric Bike · 2025 | **2.9 days** | ₹18,697 |
| Mumbai · Petrol Bike · 2025 | 5.6 days | ₹15,698 |
| Delhi · Petrol Bike · 2025 | 6.0 days | ₹13,524 |
| Mumbai · Petrol Bike · 2021 | 5.1 days | — |

The same Mumbai petrol-bike worker went from 5.1 to 5.6 break-even days
between 2021 and 2025 — a direct, quantifiable consequence of commission
creep.

### Step 5 — SQL Analysis (`SQL/Queries.sql`)
Seven queries (MySQL), covering platform ranking by city, monthly trend with
`LAG()`, rain-impact bucketing, top-10 earners, worker retention, cost
breakdown, and an efficiency split.

### Step 6 — Power BI Dashboard (`Power BI/Gig_Worker_Earnings.pbix`)
Four pages: Earnings Overview, City & Platform, Real Wage Erosion, Break-Even
Calculator. Built on 6 CSVs with 20 DAX measures — see
`PowerBI_Build_Guide.pdf` for the full build steps.

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Data wrangling | Python · pandas · NumPy |
| Visualisation | matplotlib |
| Database | MySQL |
| Dashboard | Power BI |
| Version control | Git · GitHub |
| Source data | Excel (openpyxl) |

---

## 🚀 Quick Start

```bash
git clone https://github.com/Ajaypatel06/Gig-Worker-Earnings.git
cd Gig-Worker-Earnings
pip install -r requirements.txt

python Python/data_validation.py
python Python/eda.py
python Python/03_real_wage_analysis.py
python Python/04_breakeven_model.py
```

Open `Gig_Worker_Earnings.pbix` in Power BI Desktop to view the dashboard.

---

## ⚠️ Methodology Notes

**Net Earnings Formula** (verified against all 18,000 rows, tolerance ≤ ₹1):
```
Net = Gross − Platform Commission − Fuel − Phone Data − Maintenance − Rain Income Loss
```

**Real Wage Deflation:** annual CPI (2021 = 100). `real_net = nominal_net / CPI_year × 100`.
CPI values are placeholders — replace with the exact published series and
source before treating this as final.

**Break-Even Model:** contribution per day = (gross − commission − rain loss) /
working days. Fixed costs = fuel + phone + maintenance. Break-even days =
fixed costs / contribution per day. Monthly net matches `net_earnings_inr`
exactly — it is not reduced a second time.

**2025 petrol data:** covers Jan–Aug only (8 months).

**Dataset:** synthetic, calibrated to publicly reported averages. Not real
worker or platform data.

---

## 🙋 About

**Ajay Patel** — Data Analyst, Mumbai
~3.5 years of experience · Python (pandas, NumPy) · SQL · Power BI · Excel

[LinkedIn](https://linkedin.com/in/ajay-patel-006may) · [GitHub](https://github.com/Ajaypatel06) · [Email](mailto:ajaypatel006may@gmail.com)

---

## 📄 License

MIT — free for educational and portfolio use.
