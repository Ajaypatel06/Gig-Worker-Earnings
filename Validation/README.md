# 🛵 Gig Worker Earnings Reality Check
## What Swiggy / Zomato Partners Actually Take Home (2021–2025)

> **Key Finding:** Gig workers' real wages fell ~18% between 2021 and 2025 — even as platform revenues grew. After accounting for platform commissions, fuel, maintenance, and monsoon downtime, the average delivery partner takes home just **58% of gross earnings**. Adjusted for inflation, purchasing power has eroded every single year.

---

## 📌 Project Overview

This portfolio project performs an end-to-end analysis of gig delivery worker earnings across India's top food-tech platforms — Swiggy, Zomato, Blinkit, Zepto, and Dunzo — covering Mumbai, Delhi, and Bangalore from 2021 to 2025.

**Questions this project answers:**
- How much do gig workers actually earn after all deductions?
- How has platform commission creep eroded take-home pay?
- What is the real wage trajectory when adjusted for CPI inflation?
- How many hours must a worker deliver before breaking even on costs?
- Which city, platform, and vehicle type maximises net earnings?

---

## 📂 Repository Structure

```
gig_worker_earnings/
│
├── data/
│   ├── raw/                        ← Original Excel file (do not modify)
│   │   └── project2_gig_worker_data.xlsx
│   ├── processed/                  ← Cleaned CSVs exported per sheet
│   │   ├── worker_profiles.csv
│   │   ├── monthly_earnings.csv
│   │   ├── city_year_summary.csv
│   │   ├── platform_commission_rates.csv
│   │   └── petrol_prices_monthly.csv
│   └── exports/                    ← Tableau-ready and SQL-ready outputs
│       ├── tableau_main_dataset.csv
│       └── real_wage_adjusted.csv
│
├── notebooks/
│   ├── 01_data_validation.py       ← Step 1: Schema + integrity checks
│   ├── 02_eda.ipynb                ← Step 2: Exploratory data analysis
│   ├── 03_real_wage_analysis.ipynb ← Step 3: CPI-adjusted wage erosion
│   └── 04_breakeven_model.ipynb    ← Step 4: Parameterised break-even
│
├── sql/
│   ├── 01_highest_net_by_platform_city.sql
│   ├── 02_monthly_earnings_trend.sql
│   ├── 03_rain_month_impact.sql
│   └── 04_top10_earners_profile.sql
│
├── tableau/
│   └── gig_worker_dashboard.twbx   ← Packaged Tableau workbook
│
├── reports/
│   └── gig_worker_earnings_report.pdf   ← Final narrative report
│
├── assets/
│   └── images/                     ← Charts and dashboard screenshots
│
├── requirements.txt
└── README.md                       ← This file
```

---

## 📊 Dataset

| Sheet | Rows | Description |
|---|---|---|
| `Worker_Profiles` | 300 | Demographics, city, zone, platform, vehicle |
| `Monthly_Earnings` | 18,000 | Gross, deductions, net, hourly rate (2021–2025) |
| `City_Year_Summary` | 15 | Aggregated city × year metrics + real wage index |
| `Platform_Commission_Rates` | 25 | Commission % per platform per year |
| `Petrol_Prices_Monthly` | 56 | City-level petrol price per litre per month |

**Coverage:** 300 workers × 5 years × 12 months = 18,000 rows  
**Cities:** Mumbai · Delhi · Bangalore  
**Platforms:** Swiggy · Zomato · Blinkit · Zepto · Dunzo  
**Vehicle types:** Petrol Bike · Electric Bike · CNG Bike · Bicycle

---

## 🔑 Key Findings

| Metric | Value |
|---|---|
| Avg monthly gross earnings | ₹26,909 |
| Avg monthly net earnings | ₹15,649 |
| Avg take-home rate | ~58% of gross |
| Avg platform commission (2025) | ~23% |
| Real wage index — Mumbai (2025) | 96.7 (vs 100 in 2021) |
| Real wage index — Delhi (2025) | 97.8 |
| Real wage index — Bangalore (2025) | 97.6 |
| Avg rain downtime loss | ₹878/month |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python (pandas, NumPy, matplotlib, seaborn) | EDA, modelling |
| SQL (PostgreSQL / SQLite) | Business queries |
| Tableau | Interactive dashboard |
| Excel | Source data |
| GitHub | Version control & portfolio hosting |

---

## 🚀 How to Run

```bash
# Clone the repo
git clone https://github.com/[your-username]/gig-worker-earnings.git
cd gig-worker-earnings

# Install dependencies
pip install -r requirements.txt

# Run data validation
python notebooks/01_data_validation.py

# Launch notebooks
jupyter notebook
```

---

## 📈 Analysis Steps

| Step | Notebook | Description |
|---|---|---|
| 1 | `01_data_validation.py` | Schema validation, null checks, referential integrity |
| 2 | `02_eda.ipynb` | Waterfall charts, city comparisons, rain seasonality |
| 3 | `03_real_wage_analysis.ipynb` | CPI-adjusted wage erosion 2021–2025 |
| 4 | `04_breakeven_model.ipynb` | Break-even hours by city × vehicle type |
| 5 | `sql/` | Four business SQL queries |
| 6 | Tableau | 4-view story dashboard |

---

## 💡 Methodology Notes

**Net Earnings Formula:**
```
Net = Gross − Platform Commission − Fuel − Phone Data − Maintenance − Rain Income Loss
```

**Real Wage Adjustment:**  
Net earnings deflated using India CPI index (2021 base = 100). The `real_wage_index_2021_100` column in `City_Year_Summary` captures this directly.

**Break-Even Model:**  
Fixed monthly costs (fuel + phone + maintenance) are divided by daily net rate to compute minimum working days before the worker earns a profit. Parameterised by city and vehicle type.

**Petrol Price Note:**  
2025 data runs Jan–Aug only (8 months). EDA and models treat 2025 as a partial year for fuel-cost analysis.

---

## ⚠️ Data Limitations

- Dataset is synthetic but calibrated to real reported averages from NITI Aayog gig worker surveys and industry reports
- Platform commission rates are approximate; actual rates may include surge bonuses and tier adjustments
- CPI proxy is simplified; actual real-wage calculation would require RBI's state-level CPI series

---

## 👤 Author

**[Your Name]** — Data Analyst  
Mumbai, India  
[LinkedIn] · [GitHub] · [Portfolio]

---

## 📄 License

MIT License — free to use for educational and portfolio purposes.
