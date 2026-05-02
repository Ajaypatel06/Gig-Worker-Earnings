-- ═══════════════════════════════════════════════════════════════════
-- Query A: Highest Net Earnings Platform by City
-- Project: Gig Worker Earnings Reality Check
--
-- Purpose: Rank all platforms within each city by avg monthly net
--          earnings, including commission rates and take-home %.
--
-- Key Findings:
--   Mumbai  → Zepto #1 (₹18,211 net, 19% commission)
--   Delhi   → Zepto #1 (₹14,990 net, 19% commission)
--   Bangalore→ Blinkit #1 (₹16,384 net, 20% commission)
--   Zomato  → last in every city (23.2% commission)
-- ═══════════════════════════════════════════════════════════════════

WITH platform_city_stats AS (
    SELECT
        me.city,
        me.platform,
        ROUND(AVG(me.net_earnings_inr), 0)               AS avg_net_earnings,
        ROUND(AVG(me.gross_earnings_inr), 0)              AS avg_gross_earnings,
        ROUND(AVG(me.platform_commission_pct), 1)         AS avg_commission_pct,
        ROUND(AVG(me.effective_hourly_rate_inr), 1)       AS avg_hourly_rate,
        COUNT(DISTINCT me.worker_id)                      AS worker_count,
        ROUND(
            AVG(me.net_earnings_inr) * 100.0
            / AVG(me.gross_earnings_inr), 1
        )                                                 AS take_home_pct,
        ROUND(AVG(me.commission_deducted_inr), 0)         AS avg_commission_inr,
        ROUND(AVG(me.rain_income_loss_inr), 0)            AS avg_rain_loss,
        -- Best year (highest avg net for this platform-city combo)
        MAX(CASE WHEN me.year = 2025
                 THEN ROUND(me.net_earnings_inr, 0) END)  AS sample_net_2025,
        MIN(CASE WHEN me.year = 2021
                 THEN ROUND(me.net_earnings_inr, 0) END)  AS sample_net_2021
    FROM monthly_earnings me
    GROUP BY me.city, me.platform
),
ranked AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY city
            ORDER BY avg_net_earnings DESC
        ) AS rank_in_city,
        -- Gap vs best platform in that city
        AVG(avg_net_earnings) OVER (PARTITION BY city)   AS city_avg_net,
        MAX(avg_net_earnings) OVER (PARTITION BY city)   AS city_best_net
    FROM platform_city_stats
)
SELECT
    city,
    rank_in_city                                         AS city_rank,
    platform,
    avg_net_earnings,
    avg_gross_earnings,
    avg_commission_inr,
    avg_commission_pct,
    take_home_pct,
    avg_hourly_rate,
    avg_rain_loss,
    worker_count,
    ROUND(avg_net_earnings - city_best_net, 0)           AS gap_vs_best_inr
FROM ranked
ORDER BY city, rank_in_city;

-- ── Pivot view: best platform per city at a glance ──────────────────
-- SELECT city, platform AS best_platform, avg_net_earnings, avg_commission_pct
-- FROM ranked WHERE rank_in_city = 1 ORDER BY avg_net_earnings DESC;
