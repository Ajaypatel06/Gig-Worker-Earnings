-- ═══════════════════════════════════════════════════════════════════
-- Query D: Top 10 Earners — Full Profile Deep Dive
-- Project: Gig Worker Earnings Reality Check
--
-- Purpose: Identify the highest-earning gig workers, enrich with
--          full demographic and vehicle profile, and surface the
--          combination of factors (city + platform + vehicle) that
--          drives top performance.
--
-- Key Finding: ALL top 10 are Mumbai + Electric Bike + Zepto/Blinkit
--              → City × Vehicle × Platform trifecta matters more
--                than individual work effort or seniority
-- ═══════════════════════════════════════════════════════════════════

WITH worker_aggregates AS (
    SELECT
        me.worker_id,
        me.worker_name,
        me.city,
        me.platform,
        -- Earnings summary
        COUNT(*)                                              AS months_recorded,
        COUNT(DISTINCT me.year)                              AS years_active,
        ROUND(AVG(me.gross_earnings_inr), 0)                 AS avg_monthly_gross,
        ROUND(AVG(me.net_earnings_inr), 0)                   AS avg_monthly_net,
        ROUND(SUM(me.net_earnings_inr), 0)                   AS total_net_lifetime,
        ROUND(MIN(me.net_earnings_inr), 0)                   AS worst_month_net,
        ROUND(MAX(me.net_earnings_inr), 0)                   AS best_month_net,
        -- Efficiency metrics
        ROUND(AVG(me.effective_hourly_rate_inr), 1)          AS avg_hourly_rate,
        ROUND(AVG(me.working_days), 1)                       AS avg_working_days,
        ROUND(AVG(me.idle_time_hrs), 2)                      AS avg_idle_hrs,
        -- Cost structure
        ROUND(AVG(me.platform_commission_pct), 1)            AS avg_commission_pct,
        ROUND(AVG(me.commission_deducted_inr), 0)            AS avg_commission_inr,
        ROUND(AVG(me.fuel_cost_inr), 0)                      AS avg_fuel_cost,
        ROUND(
            AVG(me.net_earnings_inr) * 100.0
            / AVG(me.gross_earnings_inr), 1
        )                                                     AS take_home_pct,
        -- Rain exposure
        ROUND(AVG(me.rain_downtime_days), 1)                 AS avg_rain_days,
        ROUND(SUM(me.rain_income_loss_inr), 0)               AS total_rain_loss,
        -- Trend: is 2025 net higher than 2021?
        ROUND(
            AVG(CASE WHEN me.year = 2025 THEN me.net_earnings_inr END)
          - AVG(CASE WHEN me.year = 2021 THEN me.net_earnings_inr END),
            0
        )                                                     AS net_change_2021_to_2025
    FROM monthly_earnings me
    GROUP BY me.worker_id, me.worker_name, me.city, me.platform
),
enriched AS (
    SELECT
        wa.*,
        wp.gender,
        wp.age,
        wp.zone,
        wp.vehicle_type,
        wp.vehicle_cc_or_watt,
        wp.years_on_platform,
        wp.joined_year,
        wp.phone_model,
        -- Rank by avg monthly net
        RANK() OVER (
            ORDER BY wa.avg_monthly_net DESC
        )                                                     AS overall_rank,
        -- Rank within city
        RANK() OVER (
            PARTITION BY wa.city
            ORDER BY wa.avg_monthly_net DESC
        )                                                     AS city_rank
    FROM worker_aggregates wa
    JOIN worker_profiles wp ON wa.worker_id = wp.worker_id
)
SELECT
    overall_rank                                              AS rank,
    city_rank,
    worker_id,
    worker_name,
    age,
    gender,
    city,
    zone,
    platform,
    vehicle_type,
    vehicle_cc_or_watt                                        AS engine,
    years_on_platform,
    joined_year,
    months_recorded,
    avg_monthly_gross,
    avg_monthly_net,
    avg_commission_pct,
    take_home_pct,
    avg_fuel_cost,
    avg_hourly_rate,
    avg_working_days,
    avg_idle_hrs,
    avg_rain_days,
    total_rain_loss,
    best_month_net,
    worst_month_net,
    total_net_lifetime,
    net_change_2021_to_2025
FROM enriched
WHERE overall_rank <= 10
ORDER BY overall_rank;

-- ── Profile pattern analysis of top 10 ──────────────────────────────
/*
SELECT
    city, platform, vehicle_type,
    COUNT(*) AS workers_in_top10,
    ROUND(AVG(avg_monthly_net), 0) AS avg_net
FROM enriched
WHERE overall_rank <= 10
GROUP BY city, platform, vehicle_type
ORDER BY workers_in_top10 DESC;
*/

-- ── Contrast: bottom 10 earners ──────────────────────────────────────
/*
SELECT
    RANK() OVER (ORDER BY avg_monthly_net ASC) AS bottom_rank,
    worker_name, age, city, platform, vehicle_type,
    avg_monthly_net, avg_commission_pct, take_home_pct, avg_fuel_cost
FROM enriched
ORDER BY avg_monthly_net ASC
LIMIT 10;
*/
