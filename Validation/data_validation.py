
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
DATA_PATH = "C:/Users/User/Desktop/Gig Worker Earnings/gig_worker_data.xlsx"

EXPECTED = {
    "Worker_Profiles":        {"rows": 300,   "cols": 12},
    "Monthly_Earnings":       {"rows": 18000, "cols": 18},
    "City_Year_Summary":      {"rows": 15,    "cols": 9},
    "Platform_Commission_Rates": {"rows": 25, "cols": 5},
    "Petrol_Prices_Monthly":  {"rows": 56,    "cols": 6},
}

CITIES     = {"Mumbai", "Delhi", "Bangalore"}
PLATFORMS  = {"Swiggy", "Zomato", "Blinkit", "Zepto", "Dunzo"}
VEHICLES   = {"Petrol Bike", "Electric Bike", "CNG Bike", "Bicycle"}
YEARS      = set(range(2021, 2026))

# ─────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────
print("=" * 65)
print("GIG WORKER EARNINGS — DATA VALIDATION REPORT")
print("=" * 65)

sheets = pd.read_excel(DATA_PATH, sheet_name=None)
wp  = sheets["Worker_Profiles"]
me  = sheets["Monthly_Earnings"]
cys = sheets["City_Year_Summary"]
pcr = sheets["Platform_Commission_Rates"]
pp  = sheets["Petrol_Prices_Monthly"]

issues = []

def check(label, condition, detail=""):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"  {status}  {label}")
    if not condition:
        issues.append(f"{label}: {detail}")

# ─────────────────────────────────────────────
# Sheet presence & shape
# ─────────────────────────────────────────────
print("\n[1] SHEET PRESENCE & SHAPE")
for name, exp in EXPECTED.items():
    df = sheets[name]
    check(
        f"{name}: {df.shape[0]} rows × {df.shape[1]} cols",
        df.shape == (exp["rows"], exp["cols"]),
        f"Expected ({exp['rows']}, {exp['cols']}), got {df.shape}"
    )

# ─────────────────────────────────────────────
#  Null values across all sheets
# ─────────────────────────────────────────────
print("\n[2] NULL VALUE CHECK")
for name, df in sheets.items():
    nulls = df.isnull().sum().sum()
    check(f"{name}: zero nulls", nulls == 0, f"{nulls} nulls found")

# ─────────────────────────────────────────────
#  Referential integrity
# ─────────────────────────────────────────────
print("\n[3] REFERENTIAL INTEGRITY")
wp_ids = set(wp["worker_id"])
me_ids = set(me["worker_id"])
check("All Monthly_Earnings worker_ids exist in Worker_Profiles",
      me_ids.issubset(wp_ids),
      f"Orphaned IDs: {me_ids - wp_ids}")
check("All Worker_Profiles IDs appear in Monthly_Earnings",
      wp_ids.issubset(me_ids),
      f"Missing IDs: {wp_ids - me_ids}")

# ─────────────────────────────────────────────
#  Domain values
# ─────────────────────────────────────────────
print("\n[4] DOMAIN VALUE CHECKS")
check("Worker_Profiles cities valid",
      set(wp["city"]).issubset(CITIES),
      f"Bad values: {set(wp['city']) - CITIES}")
check("Worker_Profiles platforms valid",
      set(wp["platform"]).issubset(PLATFORMS),
      f"Bad values: {set(wp['platform']) - PLATFORMS}")
check("Worker_Profiles vehicle_type valid",
      set(wp["vehicle_type"]).issubset(VEHICLES),
      f"Bad values: {set(wp['vehicle_type']) - VEHICLES}")
check("Worker_Profiles age range [18–65]",
      wp["age"].between(18, 65).all(),
      f"Out-of-range ages: {wp[~wp['age'].between(18,65)]['age'].tolist()}")
check("Monthly_Earnings years are 2021–2025",
      set(me["year"]).issubset(YEARS),
      f"Unexpected years: {set(me['year']) - YEARS}")
check("Monthly_Earnings months are 1–12",
      me["month"].between(1, 12).all())
check("Platform_Commission_Rates platforms valid",
      set(pcr["platform"]).issubset(PLATFORMS),
      f"Bad values: {set(pcr['platform']) - PLATFORMS}")

# ─────────────────────────────────────────────
#  Monthly_Earnings coverage (300 workers × 60 months)
# ─────────────────────────────────────────────
print("\n[5] MONTHLY_EARNINGS COVERAGE")
expected_rows = 300 * 5 * 12  # 18,000
check(f"Row count equals 300 workers × 60 months = {expected_rows}",
      len(me) == expected_rows)

per_worker = me.groupby("worker_id").size()
check("Every worker has exactly 60 month-rows",
      (per_worker == 60).all(),
      f"Workers with ≠60 rows: {per_worker[per_worker != 60].to_dict()}")

# ─────────────────────────────────────────────
#  Net earnings formula integrity
# ─────────────────────────────────────────────
print("\n[6] NET EARNINGS FORMULA INTEGRITY")
me["_computed_net"] = (
    me["gross_earnings_inr"]
    - me["commission_deducted_inr"]
    - me["fuel_cost_inr"]
    - me["phone_data_inr"]
    - me["vehicle_maintenance_inr"]
    - me["rain_income_loss_inr"]
)
diff = (me["net_earnings_inr"] - me["_computed_net"]).abs()
check(f"net_earnings = gross − all deductions (tolerance ≤ ₹1)",
      (diff <= 1).all(),
      f"{(diff > 1).sum()} rows exceed ₹1 tolerance. Max diff: ₹{diff.max():.0f}")
me.drop(columns=["_computed_net"], inplace=True)

# Commission deducted consistency
me["_exp_comm"] = (me["gross_earnings_inr"] * me["platform_commission_pct"] / 100).round()
comm_diff = (me["commission_deducted_inr"] - me["_exp_comm"]).abs()
check("commission_deducted ≈ gross × commission_pct (tolerance ≤ ₹10)",
      (comm_diff <= 10).all(),
      f"{(comm_diff > 10).sum()} rows exceed ₹10 tolerance")
me.drop(columns=["_exp_comm"], inplace=True)

# ─────────────────────────────────────────────
#  No negative values where impossible
# ─────────────────────────────────────────────
print("\n[7] NEGATIVE VALUE CHECK")
non_neg_cols = [
    "gross_earnings_inr", "fuel_cost_inr", "phone_data_inr",
    "vehicle_maintenance_inr", "rain_downtime_days", "rain_income_loss_inr",
    "net_earnings_inr", "effective_hourly_rate_inr"
]
for col in non_neg_cols:
    neg_count = (me[col] < 0).sum()
    check(f"{col} has no negative values", neg_count == 0, f"{neg_count} negatives")

# ─────────────────────────────────────────────
#  Commission rate consistency across sheets
# ─────────────────────────────────────────────
print("\n[8] COMMISSION RATE CROSS-SHEET CONSISTENCY")
me_comm = me.groupby(["platform", "year"])["platform_commission_pct"].mean().reset_index()
merged = me_comm.merge(pcr[["platform", "year", "commission_rate_pct"]], on=["platform", "year"])
merged["diff"] = (merged["platform_commission_pct"] - merged["commission_rate_pct"]).abs()
check("Commission rates in Monthly_Earnings match Platform_Commission_Rates",
      (merged["diff"] < 0.01).all(),
      f"Mismatches:\n{merged[merged['diff'] >= 0.01]}")

# ─────────────────────────────────────────────
#  Petrol prices coverage
# ─────────────────────────────────────────────
print("\n[9] PETROL PRICES COVERAGE")
for yr in range(2021, 2026):
    yr_months = sorted(pp[pp["year"] == yr]["month"].tolist())
    if yr == 2025:
        check(f"Year {yr}: 8 months (Jan–Aug, partial year expected)",
              yr_months == list(range(1, 9)),
              f"Got months: {yr_months}")
    else:
        check(f"Year {yr}: all 12 months present",
              yr_months == list(range(1, 13)),
              f"Got months: {yr_months}")

# ─────────────────────────────────────────────
#  City_Year_Summary real wage index
# ─────────────────────────────────────────────
print("\n[10] REAL WAGE INDEX SANITY")
base_vals = cys[cys["year"] == 2021]["real_wage_index_2021_100"]
check("All 3 cities start at index = 100.0 in 2021",
      (base_vals == 100.0).all(),
      f"Base year values: {base_vals.tolist()}")

end_vals = cys[cys["year"] == 2025]["real_wage_index_2021_100"]
check("All cities show real wage erosion by 2025 (index < 100)",
      (end_vals < 100).all(),
      f"2025 index values: {end_vals.tolist()}")

worst_city = cys[cys["year"] == 2025].set_index("city")["real_wage_index_2021_100"].idxmin()
worst_val  = cys[(cys["year"] == 2025) & (cys["city"] == worst_city)]["real_wage_index_2021_100"].values[0]
print(f"\n  📌 Worst real wage erosion: {worst_city} → index {worst_val} (−{100-worst_val:.1f}%)")

# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
print("\n" + "=" * 65)
if issues:
    print(f"⚠️  VALIDATION COMPLETE — {len(issues)} issue(s) found:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
else:
    print("✅  VALIDATION COMPLETE — All checks passed. Data is clean.")
print("=" * 65)

# ─────────────────────────────────────────────
# QUICK SUMMARY STATS for README
# ─────────────────────────────────────────────
print("\n📊 DATASET SNAPSHOT (for README):")
print(f"  Workers:         {len(wp):,}")
print(f"  Total rows:      {len(me):,}")
print(f"  Time period:     2021–2025 (5 years × 12 months)")
print(f"  Cities:          {sorted(CITIES)}")
print(f"  Platforms:       {sorted(PLATFORMS)}")
print(f"  Vehicle types:   {sorted(wp['vehicle_type'].unique())}")
print(f"  Avg gross/month: ₹{me['gross_earnings_inr'].mean():,.0f}")
print(f"  Avg net/month:   ₹{me['net_earnings_inr'].mean():,.0f}")
avg_take_home_pct = (me['net_earnings_inr'] / me['gross_earnings_inr']).mean() * 100
print(f"  Avg take-home %: {avg_take_home_pct:.1f}%")
print(f"  Avg commission:  {me['platform_commission_pct'].mean():.1f}%")
print(f"  Mumbai real wage index 2025: {cys[(cys['city']=='Mumbai')&(cys['year']==2025)]['real_wage_index_2021_100'].values[0]}")
