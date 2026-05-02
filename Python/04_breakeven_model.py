
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────
DATA_PATH  = "C:/Users/User/Desktop/Gig Worker Earnings/gig_worker_data.xlsx"
OUTPUT_DIR = "../assets/images/"

PALETTE = {
    "gross": "#2C3E50", "net": "#27AE60", "deduction": "#E74C3C",
    "breakeven": "#F39C12", "profit": "#27AE60", "loss": "#E74C3C",
    "Mumbai": "#2980B9", "Delhi": "#8E44AD", "Bangalore": "#E67E22",
    "Electric Bike": "#27AE60", "CNG Bike": "#F39C12",
    "Petrol Bike": "#E74C3C", "Bicycle": "#3498DB",
}
CITIES   = ["Mumbai", "Delhi", "Bangalore"]
VEHICLES = ["Electric Bike", "CNG Bike", "Bicycle", "Petrol Bike"]

def fmt_inr(x, p=None): return f"₹{x/1000:.0f}K" if x >= 1000 else f"₹{x:.0f}"

# ─────────────────────────────────────────────────────────────────────
# LOAD & ENGINEER FEATURES
# ─────────────────────────────────────────────────────────────────────
sheets = pd.read_excel(DATA_PATH, sheet_name=None)
wp = sheets["Worker_Profiles"]
me = sheets["Monthly_Earnings"]

# Engineer vehicle_cc_or_watt into two clean columns
wp["engine_type"] = wp["vehicle_cc_or_watt"].apply(
    lambda x: "Electric (W)" if str(x).endswith("W") else "ICE (CC)"
)
wp["engine_value"] = wp["vehicle_cc_or_watt"].apply(
    lambda x: int(str(x).replace("W", "")) if str(x).endswith("W")
    else int(str(x)) if str(x).isdigit() else np.nan
)

me_wp = me.merge(wp[["worker_id", "vehicle_type"]], on="worker_id")
me_wp["fixed_costs"]       = me_wp["fuel_cost_inr"] + me_wp["phone_data_inr"] + me_wp["vehicle_maintenance_inr"]
me_wp["net_per_day"]       = me_wp["net_earnings_inr"]   / me_wp["working_days"]
me_wp["gross_per_day"]     = me_wp["gross_earnings_inr"] / me_wp["working_days"]
me_wp["breakeven_days"]    = me_wp["fixed_costs"] / me_wp["net_per_day"]
me_wp["is_monsoon"]        = me_wp["month"].isin([6, 7, 8, 9])
me_wp["net_per_day_rain"]  = (me_wp["net_earnings_inr"] - me_wp["rain_income_loss_inr"]) / me_wp["working_days"]
me_wp["breakeven_rain_adj"]= me_wp["fixed_costs"] / me_wp["net_per_day_rain"].clip(lower=0.01)


# ─────────────────────────────────────────────────────────────────────
# CORE FUNCTION: parameterised_breakeven()
# ─────────────────────────────────────────────────────────────────────
def parameterised_breakeven(
    city: str,
    vehicle_type: str,
    year: int = 2025,
    platform: str = None,
    monsoon: bool = False,
    custom_commission_pct: float = None,
    custom_fuel_cost: float = None,
    custom_daily_hours: float = 8.0,
) -> dict:
    """
    Compute break-even days for a gig worker given city, vehicle, and year.

    Parameters
    ----------
    city               : "Mumbai" | "Delhi" | "Bangalore"
    vehicle_type       : "Electric Bike" | "Petrol Bike" | "CNG Bike" | "Bicycle"
    year               : 2021–2025 (default 2025)
    platform           : optional — filter to specific platform
    monsoon            : bool — apply monsoon rain-loss adjustment
    custom_commission_pct : override observed avg commission (%)
    custom_fuel_cost   : override observed avg fuel cost (INR/month)
    custom_daily_hours : assumed working hours per day (for hourly calc)

    Returns
    -------
    dict with all computed metrics + a text summary
    """
    mask = (
        (me_wp["city"]         == city) &
        (me_wp["vehicle_type"] == vehicle_type) &
        (me_wp["year"]         == year)
    )
    if platform:
        mask &= (me_wp["platform"] == platform)

    subset = me_wp[mask]
    if subset.empty:
        return {"error": f"No data for {city} / {vehicle_type} / {year} / {platform}"}

    avg_gross    = subset["gross_earnings_inr"].mean()
    avg_comm_pct = custom_commission_pct if custom_commission_pct else subset["platform_commission_pct"].mean()
    avg_fuel     = custom_fuel_cost      if custom_fuel_cost      else subset["fuel_cost_inr"].mean()
    avg_phone    = subset["phone_data_inr"].mean()
    avg_maint    = subset["vehicle_maintenance_inr"].mean()
    avg_rain     = subset["rain_income_loss_inr"].mean() if monsoon else 0
    avg_net      = subset["net_earnings_inr"].mean()
    avg_days     = subset["working_days"].mean()
    avg_hourly   = subset["effective_hourly_rate_inr"].mean()

    fixed_costs  = avg_fuel + avg_phone + avg_maint
    commission   = avg_gross * avg_comm_pct / 100
    net_minus_rain = avg_net - avg_rain
    net_per_day  = max(net_minus_rain / avg_days, 0.01)

    breakeven_days  = fixed_costs / net_per_day
    breakeven_hours = breakeven_days * custom_daily_hours
    profit_days     = avg_days - breakeven_days
    profit_window   = profit_days / avg_days * 100     # % of month in profit
    monthly_profit  = net_minus_rain - fixed_costs

    summary = (
        f"[{year}] {city} | {vehicle_type}{' | ' + platform if platform else ''}"
        f"{'  [MONSOON]' if monsoon else ''}\n"
        f"  Avg gross/month:      ₹{avg_gross:>8,.0f}\n"
        f"  Platform commission:  ₹{commission:>8,.0f}  ({avg_comm_pct:.1f}%)\n"
        f"  ─── Fixed costs ──────────────────\n"
        f"  Fuel:                 ₹{avg_fuel:>8,.0f}\n"
        f"  Phone data:           ₹{avg_phone:>8,.0f}\n"
        f"  Maintenance:          ₹{avg_maint:>8,.0f}\n"
        f"  Total fixed costs:    ₹{fixed_costs:>8,.0f}\n"
        f"  ─── Rain (monsoon) ───────────────\n"
        f"  Rain income loss:     ₹{avg_rain:>8,.0f}\n"
        f"  ─── Earnings ─────────────────────\n"
        f"  Net (adj):            ₹{net_minus_rain:>8,.0f}\n"
        f"  Net per working day:  ₹{net_per_day:>8,.0f}\n"
        f"  ─── Break-Even ───────────────────\n"
        f"  Working days/month:   {avg_days:>8.1f}\n"
        f"  ⚡ Break-even at:      {breakeven_days:>8.1f} days  ({breakeven_hours:.0f} hrs @ {custom_daily_hours}hr/day)\n"
        f"  ✅ Profit window:      {profit_days:>8.1f} days  ({profit_window:.0f}% of month)\n"
        f"  Monthly net profit:   ₹{monthly_profit:>8,.0f}\n"
        f"  Effective hourly:     ₹{avg_hourly:>8.1f}/hr"
    )

    return {
        "city": city, "vehicle_type": vehicle_type, "year": year,
        "platform": platform, "monsoon": monsoon,
        "avg_gross": avg_gross, "avg_net": avg_net,
        "commission_pct": avg_comm_pct, "commission_inr": commission,
        "fuel": avg_fuel, "phone": avg_phone, "maintenance": avg_maint,
        "rain_loss": avg_rain, "fixed_costs": fixed_costs,
        "net_per_day": net_per_day, "working_days": avg_days,
        "breakeven_days": breakeven_days, "breakeven_hours": breakeven_hours,
        "profit_days": profit_days, "profit_window_pct": profit_window,
        "monthly_profit": monthly_profit, "hourly_rate": avg_hourly,
        "summary": summary,
    }


# ─────────────────────────────────────────────────────────────────────
# EXAMPLE CALLS
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 57)
    print("BREAK-EVEN MODEL — EXAMPLE CALLS")
    print("=" * 57)

    scenarios = [
        ("Mumbai", "Electric Bike", 2025, None, False),
        ("Mumbai", "Petrol Bike",   2025, None, False),
        ("Delhi",  "Petrol Bike",   2025, None, False),
        ("Delhi",  "Electric Bike", 2025, None, False),
        ("Bangalore","CNG Bike",    2025, None, False),
        ("Mumbai", "Petrol Bike",   2025, None, True),   # monsoon
        ("Mumbai", "Petrol Bike",   2021, None, False),  # baseline year
        ("Mumbai", "Petrol Bike",   2025, "Zomato", False),
    ]

    for city, veh, yr, plat, mon in scenarios:
        r = parameterised_breakeven(city, veh, yr, plat, mon)
        print("\n" + r["summary"])

    # ── Full grid table ──────────────────────────────────────────────
    print("\n" + "=" * 57)
    print("FULL BREAK-EVEN GRID — 2025 (days)")
    print("=" * 57)
    rows = []
    for city in CITIES:
        for veh in VEHICLES:
            r     = parameterised_breakeven(city, veh, 2025)
            r_mon = parameterised_breakeven(city, veh, 2025, monsoon=True)
            rows.append({
                "City": city, "Vehicle": veh,
                "Fixed Costs (₹)": f"₹{r['fixed_costs']:,.0f}",
                "Net/Day (₹)":     f"₹{r['net_per_day']:,.0f}",
                "Breakeven Days":  f"{r['breakeven_days']:.1f}",
                "Breakeven (Monsoon)": f"{r_mon['breakeven_rain_adj'] if 'breakeven_rain_adj' in r_mon else r_mon['breakeven_days']:.1f}",
                "Profit Window": f"{r['profit_window_pct']:.0f}%",
                "Monthly Profit (₹)": f"₹{r['monthly_profit']:,.0f}",
            })
    grid = pd.DataFrame(rows)
    print(grid.to_string(index=False))

    # Run chart generation
    exec(open("04_breakeven_charts.py").read())
