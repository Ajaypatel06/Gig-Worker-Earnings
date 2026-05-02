
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────
# CONFIG & LOAD
# ─────────────────────────────────────────────────────────────────────
DATA_PATH = "C:/Users/User/Desktop/Gig Worker Earnings/gig_worker_data.xlsx"

OUTPUT_DIR  = "../assets/images/"

PALETTE = {
    "gross":      "#2C3E50",
    "net":        "#27AE60",
    "deduction":  "#E74C3C",
    "neutral":    "#95A5A6",
    "Mumbai":     "#2980B9",
    "Delhi":      "#8E44AD",
    "Bangalore":  "#E67E22",
    "Electric Bike": "#27AE60",
    "CNG Bike":      "#F39C12",
    "Petrol Bike":   "#E74C3C",
    "Bicycle":       "#3498DB",
}

MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"]

def fmt_inr(x, pos=None):
    """Format axis labels as ₹ with K suffix."""
    if x >= 1000:
        return f"₹{x/1000:.0f}K"
    return f"₹{x:.0f}"

# Load data
sheets = pd.read_excel(DATA_PATH, sheet_name=None)
wp  = sheets["Worker_Profiles"]
me  = sheets["Monthly_Earnings"]
cys = sheets["City_Year_Summary"]
pcr = sheets["Platform_Commission_Rates"]
pp  = sheets["Petrol_Prices_Monthly"]

# Merge vehicle type into earnings
me_wp = me.merge(wp[["worker_id", "vehicle_type"]], on="worker_id")

print("Data loaded. Generating charts...\n")

# ─────────────────────────────────────────────────────────────────────
# CHART 2A — GROSS vs NET WATERFALL
# ─────────────────────────────────────────────────────────────────────
def chart_2a_waterfall():
    labels     = ["Gross\nEarnings", "Platform\nCommission", "Fuel\nCost",
                  "Phone\nData", "Vehicle\nMaintenance", "Rain\nIncome Loss", "Net\nEarnings"]
    values     = [26909, -5756, -2926, -400, -1300, -878, 15649]
    pct_labels = ["", "−21.4%", "−10.9%", "−1.5%", "−4.8%", "−3.3%", ""]

    # Running total for bar bottoms
    running = 0
    bottoms, bar_vals, colors = [], [], []
    for i, v in enumerate(values):
        if i == 0:
            bottoms.append(0); bar_vals.append(v)
            colors.append(PALETTE["gross"])
        elif i == len(values) - 1:
            bottoms.append(0); bar_vals.append(v)
            colors.append(PALETTE["net"])
        else:
            running += values[i - 1] if i == 1 else 0
            bottoms.append(running + sum(values[1:i]))
            bar_vals.append(abs(v))
            colors.append(PALETTE["deduction"])

    # Recompute properly
    bottoms, bar_vals, colors = [], [], []
    cumulative = 26909
    for i, (label, val) in enumerate(zip(labels, values)):
        if i == 0:
            bottoms.append(0)
            bar_vals.append(val)
            colors.append(PALETTE["gross"])
        elif i == len(labels) - 1:
            bottoms.append(0)
            bar_vals.append(val)
            colors.append(PALETTE["net"])
        else:
            cumulative += val
            bottoms.append(cumulative)
            bar_vals.append(abs(val))
            colors.append(PALETTE["deduction"])

    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    bars = ax.bar(labels, bar_vals, bottom=bottoms, color=colors,
                  width=0.6, edgecolor="white", linewidth=1.5, zorder=3)

    # Connector lines between deduction bars
    cumulative = 26909
    for i in range(1, len(values) - 1):
        top_prev = bottoms[i - 1] + bar_vals[i - 1] if i == 1 else cumulative + values[i]
        ax.plot([i - 0.3, i + 0.3], [cumulative, cumulative],
                color="#BDC3C7", linewidth=1, linestyle="--", zorder=2)
        cumulative += values[i]

    # Value labels on bars
    for i, (bot, bv, val, pct) in enumerate(zip(bottoms, bar_vals, values, pct_labels)):
        mid = bot + bv / 2
        ax.text(i, mid, f"₹{bv:,.0f}", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")
        if pct:
            ax.text(i, bot + bv + 350, pct, ha="center", va="bottom",
                    fontsize=9, color=PALETTE["deduction"], fontweight="bold")

    ax.set_ylim(0, 33000)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
    ax.set_ylabel("Monthly Earnings (INR)", fontsize=12, color="#2C3E50")
    ax.set_title("Where Does a Gig Worker's ₹26,909 Go?\nAverage Monthly Earnings Waterfall (2021–2025)",
                 fontsize=14, fontweight="bold", color="#2C3E50", pad=15)
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=10)

    # Annotation
    ax.annotate("Only 58.2% reaches\nthe worker's pocket",
                xy=(6, 15649), xytext=(4.8, 22000),
                arrowprops=dict(arrowstyle="->", color=PALETTE["net"], lw=1.5),
                fontsize=10, color=PALETTE["net"], fontweight="bold")

    legend_elements = [
        mpatches.Patch(color=PALETTE["gross"], label="Gross Earnings"),
        mpatches.Patch(color=PALETTE["deduction"], label="Deductions"),
        mpatches.Patch(color=PALETTE["net"], label="Net Take-Home"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", framealpha=0.9)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}2A_waterfall.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✅  2A — Waterfall saved")


# ─────────────────────────────────────────────────────────────────────
# CHART 2B — CITY COMPARISON
# ─────────────────────────────────────────────────────────────────────
def chart_2b_city_comparison():
    city_data = me.groupby("city").agg(
        gross=("gross_earnings_inr", "mean"),
        net=("net_earnings_inr", "mean"),
        hourly=("effective_hourly_rate_inr", "mean")
    ).reindex(["Mumbai", "Delhi", "Bangalore"])

    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    fig.patch.set_facecolor("#FAFAFA")
    fig.suptitle("City Comparison: Mumbai Leads, Delhi Trails\nAverage Monthly Metrics Across 300 Workers",
                 fontsize=14, fontweight="bold", color="#2C3E50", y=1.01)

    cities  = city_data.index.tolist()
    metrics = [("gross", "Avg Monthly Gross", fmt_inr),
               ("net",   "Avg Monthly Net",   fmt_inr),
               ("hourly","Avg Hourly Rate",   lambda x, p: f"₹{x:.0f}")]

    for ax, (col, title, fmt) in zip(axes, metrics):
        ax.set_facecolor("#FAFAFA")
        vals   = city_data[col].values
        colors = [PALETTE[c] for c in cities]
        bars   = ax.bar(cities, vals, color=colors, width=0.55, edgecolor="white", linewidth=1.5)

        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(vals) * 0.02,
                    fmt(v), ha="center", va="bottom", fontsize=11, fontweight="bold")

        ax.set_title(title, fontsize=12, color="#2C3E50", fontweight="bold")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt))
        ax.set_ylim(0, max(vals) * 1.18)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.grid(axis="y", alpha=0.25)
        ax.tick_params(axis="x", labelsize=11)
        ax.set_facecolor("#FAFAFA")

    # Delta annotation on net chart
    axes[1].annotate(f"Mumbai earns\n₹{city_data.loc['Mumbai','net']-city_data.loc['Delhi','net']:.0f}\nmore than Delhi",
                     xy=(0, city_data.loc["Mumbai", "net"]),
                     xytext=(1, city_data.loc["Mumbai", "net"] * 0.82),
                     fontsize=9, color="#2C3E50",
                     arrowprops=dict(arrowstyle="->", color="#2C3E50", lw=1))

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}2B_city_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✅  2B — City comparison saved")


# ─────────────────────────────────────────────────────────────────────
# CHART 2C + 2D — PLATFORM COMMISSION IMPACT
# ─────────────────────────────────────────────────────────────────────
def chart_2c_2d_platform_commission():
    fig = plt.figure(figsize=(16, 7))
    fig.patch.set_facecolor("#FAFAFA")
    gs = GridSpec(1, 2, figure=fig, wspace=0.35)

    # --- 2C: Grouped bar: Gross vs Net by platform ---
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#FAFAFA")

    plat_data = me.groupby("platform").agg(
        gross=("gross_earnings_inr", "mean"),
        net=("net_earnings_inr", "mean"),
        comm_pct=("platform_commission_pct", "mean")
    ).sort_values("net", ascending=False)

    platforms = plat_data.index.tolist()
    x = np.arange(len(platforms))
    w = 0.35

    b1 = ax1.bar(x - w/2, plat_data["gross"], w, color=PALETTE["gross"],
                 label="Gross", edgecolor="white", linewidth=1.2)
    b2 = ax1.bar(x + w/2, plat_data["net"], w, color=PALETTE["net"],
                 label="Net Take-Home", edgecolor="white", linewidth=1.2)

    for bar, row in zip(b2, plat_data.itertuples()):
        gap = row.gross - row.net
        pct = row.net / row.gross * 100
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 300,
                 f"{pct:.1f}%", ha="center", va="bottom",
                 fontsize=9, color=PALETTE["net"], fontweight="bold")

    ax1.set_xticks(x)
    ax1.set_xticklabels(platforms, fontsize=10)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
    ax1.set_ylabel("Monthly Earnings (INR)", fontsize=11)
    ax1.set_title("Platform Commission Impact on\nAvg Monthly Net Earnings", fontsize=12,
                  fontweight="bold", color="#2C3E50")
    ax1.legend(fontsize=10)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.grid(axis="y", alpha=0.25)
    ax1.set_ylim(0, 33000)

    # Annotation: Zomato is worst
    ax1.annotate("Zomato workers keep\nonly 56.1% of gross",
                 xy=(len(platforms)-1 + w/2, plat_data.loc["Zomato","net"]),
                 xytext=(len(platforms)-2.5, 19000),
                 arrowprops=dict(arrowstyle="->", color=PALETTE["deduction"], lw=1.3),
                 fontsize=9, color=PALETTE["deduction"], fontweight="bold")

    # --- 2D: Commission rate creep line chart ---
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#FAFAFA")

    plat_colors = {
        "Swiggy":  "#FC8019",
        "Zomato":  "#CB202D",
        "Blinkit": "#F9D423",
        "Zepto":   "#8A2BE2",
        "Dunzo":   "#1DA462",
    }
    for plat, grp in pcr.groupby("platform"):
        ax2.plot(grp["year"], grp["commission_rate_pct"],
                 marker="o", linewidth=2.2, markersize=6,
                 color=plat_colors.get(plat, "#999"),
                 label=plat)
        ax2.text(grp["year"].max() + 0.08,
                 grp.set_index("year").loc[2025, "commission_rate_pct"],
                 f" {plat} ({grp.set_index('year').loc[2025,'commission_rate_pct']}%)",
                 fontsize=9, va="center",
                 color=plat_colors.get(plat, "#999"), fontweight="bold")

    ax2.set_xlim(2020.8, 2026.2)
    ax2.set_xticks(range(2021, 2026))
    ax2.set_ylim(15, 28)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"{x:.0f}%"))
    ax2.set_title("Commission Rate Creep: Every Platform\nRaised Rates 2021–2025", fontsize=12,
                  fontweight="bold", color="#2C3E50")
    ax2.set_ylabel("Commission Rate (%)", fontsize=11)
    ax2.grid(alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)

    # Shade the "creep zone"
    ax2.fill_between([2020.8, 2025.2], 15, 28, alpha=0.04, color="red")
    ax2.annotate("+3–4pp increase\nacross all platforms",
                 xy=(2023, 22), fontsize=9, color="#E74C3C",
                 fontstyle="italic", ha="center")

    plt.suptitle("Platform Commission: The Biggest Leakage in Gig Worker Earnings",
                 fontsize=14, fontweight="bold", color="#2C3E50", y=1.02)
    plt.savefig(f"{OUTPUT_DIR}2C2D_platform_commission.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✅  2C + 2D — Platform commission charts saved")


# ─────────────────────────────────────────────────────────────────────
# CHART 2E — RAIN DOWNTIME SEASONALITY
# ─────────────────────────────────────────────────────────────────────
def chart_2e_rain_seasonality():
    rain_monthly = me.groupby("month").agg(
        avg_days=("rain_downtime_days", "mean"),
        avg_loss=("rain_income_loss_inr", "mean")
    ).reset_index()

    rain_city = me.groupby(["city", "month"])["rain_downtime_days"].mean().reset_index()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), gridspec_kw={"hspace": 0.45})
    fig.patch.set_facecolor("#FAFAFA")

    # Top: Bar chart of avg income loss per month
    monsoon_mask = rain_monthly["month"].isin([6, 7, 8, 9])
    colors = ["#2980B9" if m else "#AED6F1" for m in monsoon_mask]
    bars = ax1.bar(MONTH_LABELS, rain_monthly["avg_loss"],
                   color=colors, edgecolor="white", linewidth=1.2, width=0.65)

    for bar, (_, row) in zip(bars, rain_monthly.iterrows()):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 30,
                 f"₹{row['avg_loss']:.0f}", ha="center", va="bottom",
                 fontsize=8.5, fontweight="bold",
                 color="#2980B9" if row["month"] in [6,7,8,9] else "#7F8C8D")

    ax1.set_facecolor("#FAFAFA")
    ax1.set_ylabel("Avg Monthly Rain Income Loss (₹)", fontsize=11)
    ax1.set_title("Monsoon Season (Jun–Sep) Destroys Income\nAvg Rain-Related Income Loss per Month", 
                  fontsize=12, fontweight="bold", color="#2C3E50")
    ax1.spines[["top","right"]].set_visible(False)
    ax1.grid(axis="y", alpha=0.25)
    ax1.set_ylim(0, 2500)

    # Annotation
    ax1.annotate("5.5× more rain downtime\nduring monsoon months",
                 xy=(6.5, 1950), xytext=(9, 2200),
                 arrowprops=dict(arrowstyle="->", color="#2980B9", lw=1.4),
                 fontsize=10, color="#2980B9", fontweight="bold")

    # Shading
    ax1.axvspan(4.5, 8.5, alpha=0.08, color="#2980B9", label="Monsoon window (Jun–Sep)")
    ax1.legend(loc="upper right", fontsize=9)

    # Bottom: Line chart per city
    for city in ["Mumbai", "Delhi", "Bangalore"]:
        city_rain = rain_city[rain_city["city"] == city]
        ax2.plot(city_rain["month"], city_rain["avg_days"],
                 marker="o", linewidth=2.2, markersize=5,
                 color=PALETTE[city], label=city)

    ax2.set_facecolor("#FAFAFA")
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(MONTH_LABELS)
    ax2.set_ylabel("Avg Rain Downtime Days", fontsize=11)
    ax2.set_title("Rain Downtime Days by City — Mumbai & Bangalore Hit Hardest in Monsoon",
                  fontsize=12, fontweight="bold", color="#2C3E50")
    ax2.legend(fontsize=10)
    ax2.spines[["top","right"]].set_visible(False)
    ax2.grid(alpha=0.25)
    ax2.axvspan(5.5, 9.5, alpha=0.07, color="#2980B9")

    fig.suptitle("Rain Downtime Seasonality: The Hidden Earnings Killer",
                 fontsize=14, fontweight="bold", color="#2C3E50", y=1.01)
    plt.savefig(f"{OUTPUT_DIR}2E_rain_seasonality.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✅  2E — Rain seasonality saved")


# ─────────────────────────────────────────────────────────────────────
# CHART 2F — VEHICLE TYPE EFFICIENCY
# ─────────────────────────────────────────────────────────────────────
def chart_2f_vehicle_efficiency():
    veh = me_wp.groupby("vehicle_type").agg(
        gross=("gross_earnings_inr", "mean"),
        fuel=("fuel_cost_inr", "mean"),
        net=("net_earnings_inr", "mean"),
        hourly=("effective_hourly_rate_inr", "mean")
    ).reindex(["Electric Bike", "CNG Bike", "Bicycle", "Petrol Bike"])

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.patch.set_facecolor("#FAFAFA")
    fig.suptitle("Vehicle Type Efficiency: Electric Bikes Win — Lower Fuel, Higher Net",
                 fontsize=14, fontweight="bold", color="#2C3E50", y=1.02)

    vehicle_colors = [PALETTE[v] for v in veh.index]
    vehicles = veh.index.tolist()

    # Panel 1: Avg fuel cost
    ax = axes[0]
    ax.set_facecolor("#FAFAFA")
    bars = ax.barh(vehicles, veh["fuel"], color=vehicle_colors, edgecolor="white", linewidth=1.2)
    for bar, v in zip(bars, veh["fuel"]):
        ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
                f"₹{v:,.0f}", va="center", fontsize=10, fontweight="bold")
    ax.set_title("Avg Monthly Fuel Cost", fontsize=11, fontweight="bold")
    ax.set_xlabel("INR per month")
    ax.spines[["top","right"]].set_visible(False)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
    ax.set_xlim(0, 5000)

    # Panel 2: Avg net earnings
    ax = axes[1]
    ax.set_facecolor("#FAFAFA")
    bars = ax.barh(vehicles, veh["net"], color=vehicle_colors, edgecolor="white", linewidth=1.2)
    for bar, v in zip(bars, veh["net"]):
        ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                f"₹{v:,.0f}", va="center", fontsize=10, fontweight="bold")
    ax.set_title("Avg Monthly Net Earnings", fontsize=11, fontweight="bold")
    ax.set_xlabel("INR per month")
    ax.spines[["top","right"]].set_visible(False)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
    ax.set_xlim(0, 22000)

    # Add Electric Bike advantage callout
    elec_net = veh.loc["Electric Bike", "net"]
    petrol_net = veh.loc["Petrol Bike", "net"]
    axes[1].annotate(f"+₹{elec_net-petrol_net:,.0f}\nvs Petrol Bike",
                     xy=(elec_net, 0), xytext=(elec_net - 2000, 0.5),
                     arrowprops=dict(arrowstyle="->", color=PALETTE["Electric Bike"], lw=1.3),
                     fontsize=9, color=PALETTE["Electric Bike"], fontweight="bold")

    # Panel 3: Hourly rate
    ax = axes[2]
    ax.set_facecolor("#FAFAFA")
    bars = ax.barh(vehicles, veh["hourly"], color=vehicle_colors, edgecolor="white", linewidth=1.2)
    for bar, v in zip(bars, veh["hourly"]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f"₹{v:.1f}/hr", va="center", fontsize=10, fontweight="bold")
    ax.set_title("Avg Effective Hourly Rate", fontsize=11, fontweight="bold")
    ax.set_xlabel("INR per hour")
    ax.spines[["top","right"]].set_visible(False)
    ax.set_xlim(0, 115)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}2F_vehicle_efficiency.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✅  2F — Vehicle efficiency saved")


# ─────────────────────────────────────────────────────────────────────
# CHART 2G — YEAR-ON-YEAR TREND: GROSS RISES, NET STAGNATES
# ─────────────────────────────────────────────────────────────────────
def chart_2g_year_trend():
    yearly = me.groupby("year").agg(
        gross=("gross_earnings_inr", "mean"),
        net=("net_earnings_inr", "mean"),
        comm_pct=("platform_commission_pct", "mean")
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#FAFAFA")
    ax1.set_facecolor("#FAFAFA")

    ax1.fill_between(yearly["year"], yearly["gross"], yearly["net"],
                     alpha=0.15, color=PALETTE["deduction"], label="Deduction gap (growing)")
    ax1.plot(yearly["year"], yearly["gross"], "o-", linewidth=2.5, markersize=8,
             color=PALETTE["gross"], label="Avg Gross Earnings")
    ax1.plot(yearly["year"], yearly["net"], "o-", linewidth=2.5, markersize=8,
             color=PALETTE["net"], label="Avg Net Take-Home")

    for _, row in yearly.iterrows():
        ax1.text(row["year"], row["gross"] + 200, f"₹{row['gross']:,.0f}",
                 ha="center", fontsize=9, color=PALETTE["gross"], fontweight="bold")
        ax1.text(row["year"], row["net"] - 450, f"₹{row['net']:,.0f}",
                 ha="center", fontsize=9, color=PALETTE["net"], fontweight="bold")

    ax1.set_xlabel("Year", fontsize=12)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
    ax1.set_ylabel("Monthly Earnings (INR)", fontsize=12)
    ax1.set_xticks(range(2021, 2026))
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.grid(alpha=0.25)
    ax1.set_ylim(12000, 31000)

    # Overlay commission % on secondary axis
    ax2 = ax1.twinx()
    ax2.plot(yearly["year"], yearly["comm_pct"], "s--", linewidth=1.8, markersize=7,
             color="#E67E22", alpha=0.85, label="Avg Commission %")
    ax2.set_ylabel("Platform Commission (%)", fontsize=11, color="#E67E22")
    ax2.tick_params(axis="y", labelcolor="#E67E22")
    ax2.set_ylim(17, 27)
    ax2.spines[["top"]].set_visible(False)

    for _, row in yearly.iterrows():
        ax2.text(row["year"] + 0.08, row["comm_pct"] + 0.12,
                 f"{row['comm_pct']:.1f}%", ha="left", fontsize=9,
                 color="#E67E22", fontweight="bold")

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right", fontsize=9)

    gross_growth = (yearly["gross"].iloc[-1] - yearly["gross"].iloc[0]) / yearly["gross"].iloc[0] * 100
    net_growth   = (yearly["net"].iloc[-1]   - yearly["net"].iloc[0])   / yearly["net"].iloc[0] * 100

    ax1.set_title(
        f"Gross Grew {gross_growth:.1f}% (2021→2025) — Net Grew Only {net_growth:.1f}%\n"
        f"Commission Creep is Swallowing the Difference",
        fontsize=13, fontweight="bold", color="#2C3E50", pad=12
    )

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}2G_year_trend.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✅  2G — Year-on-year trend saved")


# ─────────────────────────────────────────────────────────────────────
# CHART 2H — BEST PLATFORM BY CITY HEATMAP
# ─────────────────────────────────────────────────────────────────────
def chart_2h_platform_city_heatmap():
    pivot = me.groupby(["city", "platform"])["net_earnings_inr"].mean().round(0).unstack()
    pivot = pivot.reindex(["Mumbai", "Delhi", "Bangalore"])

    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    import matplotlib.colors as mcolors
    cmap = plt.cm.RdYlGn
    norm = mcolors.Normalize(vmin=pivot.values.min(), vmax=pivot.values.max())

    for i, city in enumerate(pivot.index):
        for j, plat in enumerate(pivot.columns):
            val = pivot.loc[city, plat]
            color = cmap(norm(val))
            ax.add_patch(plt.Rectangle((j, i), 1, 1, color=color, ec="white", lw=2))
            ax.text(j + 0.5, i + 0.5, f"₹{val:,.0f}",
                    ha="center", va="center", fontsize=12, fontweight="bold",
                    color="white" if norm(val) < 0.3 or norm(val) > 0.75 else "#2C3E50")

            # Crown for best in each city
            if val == pivot.loc[city].max():
                ax.text(j + 0.5, i + 0.85, "👑", ha="center", va="center", fontsize=11)

    ax.set_xlim(0, len(pivot.columns))
    ax.set_ylim(0, len(pivot.index))
    ax.set_xticks([x + 0.5 for x in range(len(pivot.columns))])
    ax.set_xticklabels(pivot.columns, fontsize=12, fontweight="bold")
    ax.set_yticks([y + 0.5 for y in range(len(pivot.index))])
    ax.set_yticklabels(pivot.index, fontsize=12, fontweight="bold")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.75, pad=0.02)
    cbar.set_label("Avg Monthly Net Earnings (₹)", fontsize=10)

    ax.set_title("Best Platform by City — Zepto Tops Mumbai, Blinkit Leads Bangalore\n(Avg Monthly Net Earnings — 2021–2025)",
                 fontsize=13, fontweight="bold", color="#2C3E50", pad=40)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}2H_platform_city_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✅  2H — Platform × City heatmap saved")


# ─────────────────────────────────────────────────────────────────────
# COMBINED SUMMARY STATS PRINT
# ─────────────────────────────────────────────────────────────────────
def print_eda_summary():
    print("\n" + "="*60)
    print("EDA SUMMARY — KEY FINDINGS")
    print("="*60)

    avg_takehome = (me["net_earnings_inr"] / me["gross_earnings_inr"]).mean() * 100
    print(f"\n📌 Average take-home rate:          {avg_takehome:.1f}% of gross")

    best_city = me.groupby("city")["net_earnings_inr"].mean().idxmax()
    best_city_net = me.groupby("city")["net_earnings_inr"].mean().max()
    print(f"📌 Highest net earnings city:       {best_city} (₹{best_city_net:,.0f}/month)")

    worst_plat = me.groupby("platform")["net_earnings_inr"].mean().idxmin()
    worst_net   = me.groupby("platform")["net_earnings_inr"].mean().min()
    best_plat  = me.groupby("platform")["net_earnings_inr"].mean().idxmax()
    best_net   = me.groupby("platform")["net_earnings_inr"].mean().max()
    print(f"📌 Best platform (net):             {best_plat} (₹{best_net:,.0f}/month)")
    print(f"📌 Worst platform (net):            {worst_plat} (₹{worst_net:,.0f}/month)")

    rain_monsoon = me[me["month"].isin([6,7,8,9])]["rain_income_loss_inr"].mean()
    rain_other   = me[~me["month"].isin([6,7,8,9])]["rain_income_loss_inr"].mean()
    print(f"📌 Monsoon avg rain loss:           ₹{rain_monsoon:,.0f}/month")
    print(f"📌 Non-monsoon avg rain loss:       ₹{rain_other:,.0f}/month")
    print(f"📌 Monsoon multiplier:              {rain_monsoon/rain_other:.1f}×")

    elec_net   = me_wp[me_wp["vehicle_type"]=="Electric Bike"]["net_earnings_inr"].mean()
    petrol_net = me_wp[me_wp["vehicle_type"]=="Petrol Bike"]["net_earnings_inr"].mean()
    print(f"📌 Electric Bike net advantage:     ₹{elec_net-petrol_net:,.0f}/month vs Petrol Bike")

    gross_21 = me[me["year"]==2021]["gross_earnings_inr"].mean()
    gross_25 = me[me["year"]==2025]["gross_earnings_inr"].mean()
    net_21   = me[me["year"]==2021]["net_earnings_inr"].mean()
    net_25   = me[me["year"]==2025]["net_earnings_inr"].mean()
    print(f"📌 Gross growth 2021→2025:          +{(gross_25-gross_21)/gross_21*100:.1f}%")
    print(f"📌 Net growth 2021→2025:            +{(net_25-net_21)/net_21*100:.1f}%")
    print("="*60)


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating all EDA charts...\n")
    chart_2a_waterfall()
    chart_2b_city_comparison()
    chart_2c_2d_platform_commission()
    chart_2e_rain_seasonality()
    chart_2f_vehicle_efficiency()
    chart_2g_year_trend()
    chart_2h_platform_city_heatmap()
    print_eda_summary()
    print(f"\n✅ All charts saved to {OUTPUT_DIR}")
