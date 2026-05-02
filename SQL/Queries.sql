
CREATE DATABASE  gig_worker_analysis;
USE gig_worker_analysis;


-- ============================================================
-- QUERY 1: Highest Net Earnings Platform by City
-- ============================================================

WITH platform_city_stats AS (
    SELECT
        me.city,
        me.platform,
        ROUND(AVG(me.net_earnings_inr), 0) AS avg_net_earnings,
        ROUND(AVG(me.gross_earnings_inr), 0) AS avg_gross_earnings,
        ROUND(AVG(me.platform_commission_pct), 1) AS avg_commission_pct,
        ROUND(AVG(me.effective_hourly_rate_inr), 1) AS avg_hourly_rate,
        COUNT(DISTINCT me.worker_id) AS worker_count,
        ROUND(AVG(me.net_earnings_inr) * 100.0 / AVG(me.gross_earnings_inr), 1) AS take_home_pct,
        ROUND(AVG(me.commission_deducted_inr), 0) AS avg_commission_inr,
        ROUND(AVG(me.rain_income_loss_inr), 0) AS avg_rain_loss
    FROM monthly_earnings me
    GROUP BY me.city, me.platform
),

ranked AS (
    SELECT
        pcs.*,
        RANK() OVER (PARTITION BY pcs.city ORDER BY pcs.avg_net_earnings DESC) AS rank_in_city,
        MAX(pcs.avg_net_earnings) OVER (PARTITION BY pcs.city) AS city_best_net
    FROM platform_city_stats pcs
)

SELECT
    city,
    rank_in_city AS city_rank,
    platform,
    avg_net_earnings,
    avg_gross_earnings,
    avg_commission_inr,
    avg_commission_pct,
    take_home_pct,
    avg_hourly_rate,
    avg_rain_loss,
    worker_count,
    ROUND(avg_net_earnings - city_best_net, 0) AS gap_vs_best_inr
FROM ranked
ORDER BY city, rank_in_city;


-- ============================================================
-- QUERY 2: Monthly Trend Analysis
-- ============================================================

WITH monthly_trend AS (
    SELECT
        me.year,
        me.month,
        MONTHNAME(STR_TO_DATE(me.month, '%m')) AS month_name,
        CASE WHEN me.month IN (6,7,8,9) THEN 'Monsoon' ELSE 'Non-Monsoon' END AS season,

        ROUND(AVG(me.gross_earnings_inr), 0) AS avg_gross,
        ROUND(AVG(me.net_earnings_inr), 0) AS avg_net,
        ROUND(AVG(me.platform_commission_pct), 2) AS avg_commission_pct,
        ROUND(AVG(me.commission_deducted_inr), 0) AS avg_commission_inr,
        ROUND(AVG(me.fuel_cost_inr), 0) AS avg_fuel,
        ROUND(AVG(me.rain_income_loss_inr), 0) AS avg_rain_loss,
        ROUND(AVG(me.effective_hourly_rate_inr), 1) AS avg_hourly,
        ROUND(AVG(me.working_days), 1) AS avg_working_days,
        COUNT(DISTINCT me.worker_id) AS active_workers
    FROM monthly_earnings me
    GROUP BY me.year, me.month
),

with_lag AS (
    SELECT
        mt.*,
        ROUND(
            (mt.avg_net - LAG(mt.avg_net) OVER (ORDER BY mt.year, mt.month)) * 100.0 /
            NULLIF(LAG(mt.avg_net) OVER (ORDER BY mt.year, mt.month), 0),
            1
        ) AS mom_net_pct,

        ROUND(
            (mt.avg_net - LAG(mt.avg_net, 12) OVER (ORDER BY mt.year, mt.month)) * 100.0 /
            NULLIF(LAG(mt.avg_net, 12) OVER (ORDER BY mt.year, mt.month), 0),
            1
        ) AS yoy_net_pct,

        ROUND(
            AVG(mt.avg_net) OVER (
                ORDER BY mt.year, mt.month
                ROWS BETWEEN 5 PRECEDING AND 6 FOLLOWING
            ), 0
        ) AS rolling_12m_avg_net
    FROM monthly_trend mt
)

SELECT *
FROM with_lag
ORDER BY year, month;


-- ============================================================
-- QUERY 3: Rain Impact Analysis
-- ============================================================

WITH classified AS (
    SELECT
        me.*,
        CASE WHEN me.month IN (6,7,8,9) THEN 'Monsoon' ELSE 'Non-Monsoon' END AS season,
        CASE
            WHEN me.rain_downtime_days = 0 THEN 'No Rain'
            WHEN me.rain_downtime_days BETWEEN 1 AND 3 THEN 'Light'
            WHEN me.rain_downtime_days BETWEEN 4 AND 6 THEN 'Heavy'
            ELSE 'Extreme'
        END AS rain_bucket
    FROM monthly_earnings me
),

city_bucket AS (
    SELECT
        city,
        season,
        rain_bucket,
        COUNT(*) AS records,
        ROUND(AVG(rain_downtime_days), 2) AS avg_rain_days,
        ROUND(AVG(rain_income_loss_inr), 0) AS avg_rain_loss,
        ROUND(AVG(net_earnings_inr), 0) AS avg_net,
        ROUND(AVG(gross_earnings_inr), 0) AS avg_gross,
        ROUND(AVG(rain_income_loss_inr) * 100.0 / AVG(gross_earnings_inr), 1) AS rain_pct_of_gross,
        ROUND(AVG(effective_hourly_rate_inr), 1) AS avg_hourly
    FROM classified
    GROUP BY city, season, rain_bucket
)

SELECT *
FROM city_bucket
ORDER BY city, season DESC, rain_bucket;


-- ============================================================
-- QUERY 4: Top 10 Earners
-- ============================================================

WITH worker_aggregates AS (
    SELECT
        me.worker_id,
        me.worker_name,
        me.city,
        me.platform,
        ROUND(AVG(me.net_earnings_inr), 0) AS avg_monthly_net,
        ROUND(SUM(me.net_earnings_inr), 0) AS total_net_lifetime
    FROM monthly_earnings me
    GROUP BY me.worker_id, me.worker_name, me.city, me.platform
),

ranked AS (
    SELECT
        wa.*,
        RANK() OVER (ORDER BY wa.avg_monthly_net DESC) AS overall_rank
    FROM worker_aggregates wa
)

SELECT *
FROM ranked
WHERE overall_rank <= 10
ORDER BY overall_rank;


-- ============================================================
-- QUERY 5: Worker Retention (Platform Loyalty)
-- ============================================================

SELECT
    worker_type,
    COUNT(*) AS workers
FROM (
    SELECT
        worker_id,
        CASE 
            WHEN COUNT(DISTINCT platform) = 1 THEN 'Single Platform'
            ELSE 'Multi Platform'
        END AS worker_type
    FROM monthly_earnings
    GROUP BY worker_id
) t
GROUP BY worker_type;


-- ============================================================
-- QUERY 6: Cost Breakdown (Profit Drivers)
-- ============================================================

SELECT
    city,
    platform,
    ROUND(AVG(fuel_cost_inr),0) AS avg_fuel,
    ROUND(AVG(platform_commission_pct),1) AS avg_commission_pct,
    ROUND(AVG(rain_income_loss_inr),0) AS avg_rain_loss,
    ROUND(AVG(net_earnings_inr),0) AS avg_net,
    ROUND(AVG(fuel_cost_inr) * 100 / AVG(gross_earnings_inr),1) AS fuel_pct,
    ROUND(AVG(rain_income_loss_inr) * 100 / AVG(gross_earnings_inr),1) AS rain_pct
FROM monthly_earnings
GROUP BY city, platform
ORDER BY avg_net DESC;


-- ============================================================
-- QUERY 7: What Drives High Earnings
-- ============================================================

SELECT
    CASE 
        WHEN effective_hourly_rate_inr >= 150 THEN 'High Efficiency'
        ELSE 'Low Efficiency'
    END AS efficiency_group,
    ROUND(AVG(net_earnings_inr),0) AS avg_net,
    ROUND(AVG(working_days),1) AS avg_days,
    ROUND(AVG(idle_time_hrs),1) AS avg_idle,
    ROUND(AVG(platform_commission_pct),1) AS avg_commission
FROM monthly_earnings
GROUP BY efficiency_group;