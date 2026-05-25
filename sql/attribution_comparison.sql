
-- ────────────────────────── ATTRIBUTION COMPARISON ───────────────────────────
-- Business question: Does attribution model change how we evaluate channels?
-- Last-click gives 100% credit to the channel of the last session before purchase.


-- 1. Last-click attribution: credit goes to acquisition channel
-- Finding: compare these results with linear attribution below to see which channels are over- or under-valued under last-click model.
SELECT
    u.acquisition_channel,
    COUNT(DISTINCT p.purchase_id)             AS purchases,
    ROUND(SUM(p.revenue_usd::numeric), 2)     AS attributed_revenue,
    ROUND(AVG(p.revenue_usd::numeric), 2)     AS avg_order_value
FROM purchases p
JOIN users u ON p.user_id = u.user_id
GROUP BY u.acquisition_channel
ORDER BY attributed_revenue DESC;

-- 2. Linear attribution: credit split equally across all user sessions
-- Each session gets an equal share of the user's total revenue.
-- This better reflects the full player journey, not just the acquisition channel.
WITH user_stats AS (
    SELECT
        u.user_id,
        u.acquisition_channel,
        COUNT(DISTINCT s.session_id)          AS total_sessions,
        ROUND(SUM(p.revenue_usd::numeric), 2) AS total_revenue
    FROM users u
    JOIN sessions s ON u.user_id = s.user_id
    LEFT JOIN purchases p ON u.user_id = p.user_id
    WHERE u.is_paying = true
    GROUP BY u.user_id, u.acquisition_channel
)
SELECT
    acquisition_channel,
    COUNT(DISTINCT user_id)                                        AS paying_users,
    ROUND(SUM(total_revenue::numeric), 2)                         AS total_revenue,
    ROUND(SUM(total_revenue::numeric) / SUM(total_sessions), 4)  AS revenue_per_session,
    ROUND(AVG(total_sessions), 1)                                 AS avg_sessions_per_user
FROM user_stats
GROUP BY acquisition_channel
ORDER BY revenue_per_session DESC;

-- 3. Attribution comparison: channel share under each model (%)
-- Finding: Email is undervalued by 2ppt under last-click attribution.
-- Google Ads undervalued by 2.5ppt — participates more in the player journey.
-- Organic overvalued by 4.6ppt — users convert faster, fewer sessions before purchase.
-- TikTok is neutral — consistent performance across both models.
WITH last_click AS (
    SELECT
        u.acquisition_channel,
        ROUND(SUM(p.revenue_usd::numeric), 2) AS lc_revenue
    FROM purchases p
    JOIN users u ON p.user_id = u.user_id
    GROUP BY u.acquisition_channel
),
linear AS (
    SELECT
        u.acquisition_channel,
        COUNT(DISTINCT s.session_id) AS total_sessions
    FROM users u
    JOIN sessions s ON u.user_id = s.user_id
    WHERE u.is_paying = true
    GROUP BY u.acquisition_channel
)
SELECT
    lc.acquisition_channel,
    lc.lc_revenue,
    ROUND(lc.lc_revenue * 100.0 / SUM(lc.lc_revenue) OVER (), 1) AS lc_share_pct,
    li.total_sessions,
    ROUND(li.total_sessions * 100.0 / SUM(li.total_sessions) OVER (), 1) AS linear_share_pct,
    ROUND(li.total_sessions * 100.0 / SUM(li.total_sessions) OVER () -
          lc.lc_revenue * 100.0 / SUM(lc.lc_revenue) OVER (), 1) AS difference_ppt
FROM last_click lc
JOIN linear li ON lc.acquisition_channel = li.acquisition_channel
ORDER BY difference_ppt DESC;
