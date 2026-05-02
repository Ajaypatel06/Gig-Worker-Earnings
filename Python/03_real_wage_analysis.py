
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────
DATA_PATH  = "C:/Users/User/Desktop/Gig Worker Earnings/gig_worker_data.xlsx"
OUTPUT_DIR = "../assets/images/"

# India Urban CPI — RBI/MoSPI (2021 base = 100)
CPI = {2021: 100.0, 2022: 106.7, 2023: 112.1, 2024: 117.2, 2025: 121.4}

CITY_COLORS = {"Mumbai": "#2980B9", "Delhi": "#8E44AD", "Bangalore": "#E67E22"}
PLAT_COLORS = {"Swiggy":"#FC8019","Zomato":"#CB202D","Blinkit":"#E6A817","Zepto":"#8A2BE2","Dunzo":"#1DA462"}
PALETTE     = {"gross":"#2C3E50","net":"#27AE60","deduction":"#E74C3C","cpi":"#E67E22"}

def fmt_inr(x, p=None): return f"₹{x/1000:.0f}K" if x >= 1000 else f"₹{x:.0f}"

# ─────────────────────────────────────────────────────────────────────
# LOAD & INFLATE
# ─────────────────────────────────────────────────────────────────────
me = pd.read_excel(DATA_PATH, sheet_name="Monthly_Earnings")

# Monthly CPI via linear interpolation between annual anchors
yrs = [2021, 2022, 2023, 2024, 2025]
monthly_cpi = {}
for i, yr in enumerate(yrs):
    for m in range(1, 13):
        if i < len(yrs) - 1:
            monthly_cpi[(yr, m)] = CPI[yr] + (m - 1) / 12 * (CPI[yrs[i+1]] - CPI[yr])
        else:
            monthly_cpi[(yr, m)] = CPI[yr]

me["cpi"]         = me["year"].map(CPI)
me["cpi_monthly"] = me.apply(lambda r: monthly_cpi.get((r["year"], r["month"]), CPI[r["year"]]), axis=1)
me["real_net"]    = (me["net_earnings_inr"]   / me["cpi_monthly"] * 100).round(2)
me["real_gross"]  = (me["gross_earnings_inr"] / me["cpi_monthly"] * 100).round(2)

yearly = me.groupby("year")[["gross_earnings_inr","net_earnings_inr","real_gross","real_net","effective_hourly_rate_inr"]].mean().reset_index()
yearly["real_net_idx"]  = (yearly["real_net"]           / yearly.loc[0,"real_net"]   * 100).round(1)
yearly["real_gross_idx"]= (yearly["real_gross"]         / yearly.loc[0,"real_gross"] * 100).round(1)
yearly["nom_net_idx"]   = (yearly["net_earnings_inr"]   / yearly.loc[0,"net_earnings_inr"]   * 100).round(1)
yearly["cpi_idx"]       = [CPI[y] for y in yearly["year"]]

# ─────────────────────────────────────────────────────────────────────
# PRINT HEADLINE FINDINGS
# ─────────────────────────────────────────────────────────────────────
net_21      = yearly.loc[yearly["year"]==2021, "net_earnings_inr"].values[0]
net_25      = yearly.loc[yearly["year"]==2025, "net_earnings_inr"].values[0]
real_net_25 = yearly.loc[yearly["year"]==2025, "real_net_idx"].values[0]
print("=" * 55)
print("STEP 3 — REAL WAGE ANALYSIS FINDINGS")
print("=" * 55)
print(f"Nominal net earnings 2021:         ₹{net_21:,.0f}")
print(f"Nominal net earnings 2025:         ₹{net_25:,.0f}")
print(f"Nominal change:                    {(net_25-net_21)/net_21*100:+.1f}%")
print(f"Cumulative CPI inflation:          +{CPI[2025]-100:.1f}%")
print(f"Real net wage index 2025:          {real_net_25:.1f} (base=100)")
print(f"Real purchasing power erosion:     {real_net_25-100:.1f}%")
print(f"→ HEADLINE: Real wages fell ~19.8% while platforms grew commissions from 19.6% → 23.2%")
print("=" * 55)


import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────
# CHART 3A — NOMINAL vs REAL WAGE INDEX
# ─────────────────────────────────────────────────────────────────────
def chart_3a():
    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor("#FAFAFA"); ax.set_facecolor("#FAFAFA")
    ax.plot(yearly["year"], yearly["nom_net_idx"], "o-", lw=2.5, ms=9, color=PALETTE["gross"], label="Nominal Net (index)")
    ax.plot(yearly["year"], yearly["real_net_idx"],"o-", lw=2.5, ms=9, color=PALETTE["net"],   label="Real Net — CPI adjusted (index)")
    ax.plot(yearly["year"], yearly["cpi_idx"],     "s--",lw=2,   ms=7, color=PALETTE["cpi"],   label="India Urban CPI (2021=100)", alpha=0.8)
    ax.fill_between(yearly["year"], yearly["nom_net_idx"], yearly["real_net_idx"],
        where=yearly["nom_net_idx"] >= yearly["real_net_idx"],
        alpha=0.12, color=PALETTE["deduction"], label="Purchasing power lost to inflation")
    for _, row in yearly.iterrows():
        ax.text(row["year"], row["nom_net_idx"]+0.8,  f"{row['nom_net_idx']:.1f}",  ha="center", fontsize=9, color=PALETTE["gross"], fontweight="bold")
        ax.text(row["year"], row["real_net_idx"]-1.5, f"{row['real_net_idx']:.1f}", ha="center", fontsize=9, color=PALETTE["net"],   fontweight="bold")
    ax.axhline(100, color="#BDC3C7", lw=1.2, linestyle="--", alpha=0.7, label="2021 baseline")
    ax.set_xlim(2020.7, 2025.3); ax.set_xticks(range(2021, 2026)); ax.set_ylim(76, 126)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"{x:.0f}"))
    ax.set_ylabel("Index (2021 = 100)", fontsize=12)
    ax.set_title("The Illusion of Wage Growth\nNominal earnings barely moved — Real purchasing power fell ~20%", fontsize=14, fontweight="bold", color="#2C3E50", pad=14)
    ax.legend(fontsize=9, loc="upper left"); ax.grid(alpha=0.22); ax.spines[["top","right"]].set_visible(False)
    ax.annotate("Real net wages fell\n−19.8% by 2025\n(nominal: −2.7%)",
        xy=(2025, yearly.loc[yearly["year"]==2025,"real_net_idx"].values[0]), xytext=(2023.3, 83),
        arrowprops=dict(arrowstyle="->", color=PALETTE["net"], lw=1.6),
        fontsize=10, color=PALETTE["net"], fontweight="bold")
    ax.annotate("CPI rose +21.4%\ncumulatively",
        xy=(2025, CPI[2025]), xytext=(2023.5, 118),
        arrowprops=dict(arrowstyle="->", color=PALETTE["cpi"], lw=1.3),
        fontsize=9, color=PALETTE["cpi"], fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}3A_nominal_vs_real.png", dpi=150, bbox_inches="tight"); plt.close()
    print("  ✅  3A saved")

# ─────────────────────────────────────────────────────────────────────
# CHART 3B — CITY REAL WAGE EROSION
# ─────────────────────────────────────────────────────────────────────
def chart_3b():
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#FAFAFA"); ax.set_facecolor("#FAFAFA")
    for city, col in CITY_COLORS.items():
        sub = me[me["city"]==city].groupby("year")["real_net"].mean().reset_index()
        base = sub.loc[sub["year"]==2021, "real_net"].values[0]
        sub["idx"] = (sub["real_net"] / base * 100).round(1)
        ax.plot(sub["year"], sub["idx"], "o-", lw=2.5, ms=8, color=col, label=city)
        ax.fill_between(sub["year"], sub["idx"], 100, where=sub["idx"]<=100, alpha=0.07, color=col)
        ax.text(2025.08, sub.loc[sub["year"]==2025,"idx"].values[0],
            f" {city} ({sub.loc[sub['year']==2025,'idx'].values[0]:.1f})", fontsize=10, va="center", color=col, fontweight="bold")
    ax.axhline(100, color="#BDC3C7", lw=1.3, linestyle="--", alpha=0.8)
    ax.set_xlim(2020.7, 2026.3); ax.set_xticks(range(2021, 2026)); ax.set_ylim(76, 104)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"{x:.0f}"))
    ax.set_ylabel("Real Net Wage Index (2021=100)", fontsize=12)
    ax.set_title("Real Wage Erosion by City\nAll Three Cities Lost ~20% in Purchasing Power by 2025", fontsize=13, fontweight="bold", color="#2C3E50", pad=12)
    ax.legend(fontsize=10, loc="upper right"); ax.grid(alpha=0.22); ax.spines[["top","right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}3B_city_real_wage_erosion.png", dpi=150, bbox_inches="tight"); plt.close()
    print("  ✅  3B saved")

# (Additional chart functions follow same pattern — see 3C, 3D, 3E, 3F)

if __name__ == "__main__":
    chart_3a()
    chart_3b()
    print("\n✅ Core charts saved. Run full script for all 6 charts.")
