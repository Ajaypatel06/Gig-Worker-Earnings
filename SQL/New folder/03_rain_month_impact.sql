-- ═══════════════════════════════════════════════════════════════════
-- Query C: Rain Month Impact Analysis
-- Project: Gig Worker Earnings Reality Check
--
-- Purpose: Quantify how rain downtime affects net earnings across
--          cities, seasons and rain intensity buckets.
--
-- Key Findings:
--   Extreme rain months (7+ days): net falls to ₹12,465–₹15,225
--   (vs ₹15,045–₹17,817 in rain-free months) → up to -17% income
--   Rain-loss % of gross reaches 9.2–10.5% in extreme rain months
--   All 3 cities hit symmetrically in Jun–Sep monsoon window
-- ═══════════════════════════════════════════════════════════════════

WITH classified AS (
    SELECT
        me.city,
        me.platform,
        me.year,
        me.month,
        me.worker_id,
        me.net_earnings_inr,
        me.gross_earnings_inr,
        me.rain_downtime_days,
        me.rain_income_loss_inr,
        me.effective_hourly_rate_inr,
        me.working_days,
        -- Season flag
        CASE
            WHEN me.month IN (6,7,8,9) THEN 'Monsoon (Jun–Sep)'
            ELSE 'Non-Monsoon'
        END AS season,
        -- Rain intensity bucket
        CASE
            WHEN me.rain_downtime_days = 0              THEN '0. No Rain'
            WHEN me.rain_downtime_days BETWEEN 1 AND 3  THEN '1. Light  (1–3d)'
            WHEN me.rain_downtime_days BETWEEN 4 AND 6  THEN '2. Heavy  (4–6d)'
            ELSE                                             '3. Extreme (7+d)'
        END AS rain_bucket,
        -- Income lost per rain day (productivity metric)
        CASE
            WHEN me.rain_downtime_days > 0
            THEN ROUND(me.rain_income_loss_inr * 1.0 / me.rain_downtime_days, 0)
            ELSE 0
        END AS loss_per_rain_day
    FROM monthly_earnings me
),

-- ── Section 1: City × Season summary ────────────────────────────────
city_season AS (
    SELECT
        city,
        season,
        COUNT(*)                                              AS month_records,
        ROUND(AVG(rain_downtime_days), 2)                    AS avg_rain_days,
        ROUND(AVG(rain_income_loss_inr), 0)                  AS avg_rain_loss_inr,
        ROUND(AVG(net_earnings_inr), 0)                      AS avg_net,
        ROUND(AVG(gross_earnings_inr), 0)                    AS avg_gross,
        ROUND(AVG(effective_hourly_rate_inr), 1)             AS avg_hourly,
        ROUND(
            AVG(rain_income_loss_inr) * 100.0
            / AVG(gross_earnings_inr), 1
        )                                                     AS rain_loss_pct_of_gross,
        ROUND(AVG(loss_per_rain_day), 0)                     AS avg_loss_per_rain_day
    FROM classified
    GROUP BY city, season
),

-- ── Section 2: City × Rain bucket detail ────────────────────────────
city_bucket AS (
    SELECT
        city,
        season,
        rain_bucket,
        COUNT(*)                                              AS records,
        ROUND(AVG(rain_downtime_days), 2)                    AS avg_rain_days,
        ROUND(AVG(rain_income_loss_inr), 0)                  AS avg_rain_loss,
        ROUND(AVG(net_earnings_inr), 0)                      AS avg_net,
        ROUND(AVG(gross_earnings_inr), 0)                    AS avg_gross,
        ROUND(
            AVG(rain_income_loss_inr) * 100.0
            / AVG(gross_earnings_inr), 1
        )                                                     AS rain_pct_of_gross,
        ROUND(AVG(effective_hourly_rate_inr), 1)             AS avg_hourly
    FROM classified
    GROUP BY city, season, rain_bucket
)

-- Main output: city × season × rain bucket
SELECT
    city,
    season,
    rain_bucket,
    records,
    avg_rain_days,
    avg_rain_loss                                             AS avg_rain_loss_inr,
    rain_pct_of_gross                                         AS rain_loss_pct_gross,
    avg_net,
    avg_gross,
    avg_hourly
FROM city_bucket
ORDER BY city, season DESC, rain_bucket;

-- ── Supplementary: worst rain months (worker-level) ─────────────────
/*
SELECT
    me.worker_id,
    wp.worker_name,
    me.city,
    me.platform,
    me.year,
    me.month,
    me.rain_downtime_days,
    me.rain_income_loss_inr,
    me.net_earnings_inr,
    ROUND(me.rain_income_loss_inr * 100.0 / me.gross_earnings_inr, 1) AS rain_pct_gross
FROM monthly_earnings me
JOIN worker_profiles wp ON me.worker_id = wp.worker_id
WHERE me.rain_downtime_days >= 7
ORDER BY me.rain_income_loss_inr DESC
LIMIT 20;
*/

-- ── Rain-adjusted vs unadjusted net by year ─────────────────────────
/*
SELECT
    year,
    ROUND(AVG(net_earnings_inr), 0)                    AS avg_net_nominal,
    ROUND(AVG(net_earnings_inr - rain_income_loss_inr), 0) AS avg_net_rain_adjusted,
    ROUND(AVG(rain_income_loss_inr), 0)                AS avg_rain_cost
FROM monthly_earnings
GROUP BY year
ORDER BY year;
*/
