-- ═══════════════════════════════════════════════════════════════════
-- Query B: Monthly Earnings Trend 2021–2025
-- Project: Gig Worker Earnings Reality Check
--
-- Purpose: Full 60-month time series of avg gross/net, commission,
--          fuel, rain loss, hourly rate and MoM change.
--          Identifies structural decline and monsoon seasonality.
--
-- Key Findings:
--   Jun–Sep  → avg net drops ~₹1,800 vs surrounding months (monsoon)
--   Jan 2022 → commission jumped from 19.6% to 20.4% (biggest step)
--   Jan 2025 → commission at 23.2%, net at historical low
--   MoM swings of −12% (May→Jun monsoon onset) are the largest moves
-- ═══════════════════════════════════════════════════════════════════

WITH monthly_trend AS (
    SELECT
        me.year,
        me.month,
        CASE me.month
            WHEN 1  THEN 'Jan' WHEN 2  THEN 'Feb' WHEN 3  THEN 'Mar'
            WHEN 4  THEN 'Apr' WHEN 5  THEN 'May' WHEN 6  THEN 'Jun'
            WHEN 7  THEN 'Jul' WHEN 8  THEN 'Aug' WHEN 9  THEN 'Sep'
            WHEN 10 THEN 'Oct' WHEN 11 THEN 'Nov' WHEN 12 THEN 'Dec'
        END                                                   AS month_name,
        CASE WHEN me.month IN (6,7,8,9)
             THEN 'Monsoon' ELSE 'Non-Monsoon'
        END                                                   AS season,
        ROUND(AVG(me.gross_earnings_inr), 0)                  AS avg_gross,
        ROUND(AVG(me.net_earnings_inr), 0)                    AS avg_net,
        ROUND(AVG(me.platform_commission_pct), 2)             AS avg_commission_pct,
        ROUND(AVG(me.commission_deducted_inr), 0)             AS avg_commission_inr,
        ROUND(AVG(me.fuel_cost_inr), 0)                       AS avg_fuel,
        ROUND(AVG(me.phone_data_inr), 0)                      AS avg_phone,
        ROUND(AVG(me.vehicle_maintenance_inr), 0)             AS avg_maintenance,
        ROUND(AVG(me.rain_downtime_days), 2)                  AS avg_rain_days,
        ROUND(AVG(me.rain_income_loss_inr), 0)                AS avg_rain_loss,
        ROUND(AVG(me.effective_hourly_rate_inr), 1)           AS avg_hourly,
        ROUND(AVG(me.working_days), 1)                        AS avg_working_days,
        ROUND(AVG(me.idle_time_hrs), 2)                       AS avg_idle_hrs,
        COUNT(DISTINCT me.worker_id)                          AS active_workers
    FROM monthly_earnings me
    GROUP BY me.year, me.month
),
with_lag AS (
    SELECT
        mt.*,
        -- Month-over-month net change
        LAG(mt.avg_net) OVER (
            ORDER BY mt.year, mt.month
        )                                                     AS prev_month_net,
        ROUND(
            (mt.avg_net - LAG(mt.avg_net) OVER (ORDER BY mt.year, mt.month))
            * 100.0
            / NULLIF(LAG(mt.avg_net) OVER (ORDER BY mt.year, mt.month), 0),
            1
        )                                                     AS mom_net_pct,
        -- Year-over-year same month
        LAG(mt.avg_net, 12) OVER (
            ORDER BY mt.year, mt.month
        )                                                     AS same_month_prev_year,
        ROUND(
            (mt.avg_net - LAG(mt.avg_net, 12) OVER (ORDER BY mt.year, mt.month))
            * 100.0
            / NULLIF(LAG(mt.avg_net, 12) OVER (ORDER BY mt.year, mt.month), 0),
            1
        )                                                     AS yoy_net_pct,
        -- Running avg for trend line (12-month moving average)
        ROUND(
            AVG(mt.avg_net) OVER (
                ORDER BY mt.year, mt.month
                ROWS BETWEEN 5 PRECEDING AND 6 FOLLOWING
            ), 0
        )                                                     AS rolling_12m_avg_net
    FROM monthly_trend mt
)
SELECT
    year,
    month,
    month_name,
    season,
    avg_gross,
    avg_net,
    avg_commission_pct,
    avg_commission_inr,
    avg_fuel,
    avg_rain_loss,
    avg_rain_days,
    avg_hourly,
    avg_working_days,
    mom_net_pct,
    yoy_net_pct,
    rolling_12m_avg_net
FROM with_lag
ORDER BY year, month;

-- ── Yearly summary pivot ─────────────────────────────────────────────
/*
SELECT
    year,
    ROUND(AVG(avg_gross), 0)         AS yearly_avg_gross,
    ROUND(AVG(avg_net), 0)           AS yearly_avg_net,
    ROUND(AVG(avg_commission_pct),1) AS avg_commission_pct,
    ROUND(AVG(avg_fuel), 0)          AS avg_fuel,
    ROUND(AVG(avg_rain_loss), 0)     AS avg_rain_loss
FROM monthly_trend
GROUP BY year
ORDER BY year;
*/

-- ── Monsoon vs Non-Monsoon summary ─────────────────────────────────
/*
SELECT
    season,
    ROUND(AVG(avg_net), 0)   AS avg_net,
    ROUND(AVG(avg_gross), 0) AS avg_gross,
    ROUND(AVG(avg_rain_loss),0) AS avg_rain_loss
FROM monthly_trend
GROUP BY season;
*/
