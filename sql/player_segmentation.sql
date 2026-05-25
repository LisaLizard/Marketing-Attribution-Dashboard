-- ────────────────── PLAYER SEGMENTATION ANALYSIS ─────────────────────────────
-- Business question: Who are our most valuable players by country, gender, device?


-- 1. Revenue and engagement by country
-- Finding: US has the highest avg revenue per paying user ($75.28) despite small audience.
-- Japan leads in conversion rate (4.90%) with high avg order value ($67.82).
-- Finland is the largest market (1,631 users) but lowest conversion (3.25%) and avg spend ($40.40).
-- NULL country users show surprisingly high conversion (5.44%) — likely VPN users from high-income markets.
SELECT
    u.country,
    COUNT(DISTINCT u.user_id)                                       AS total_users,
    COUNT(DISTINCT CASE WHEN u.is_paying THEN u.user_id END)        AS paying_users,
    ROUND(COUNT(DISTINCT CASE WHEN u.is_paying THEN u.user_id END)
          * 100.0 / COUNT(DISTINCT u.user_id), 2)                   AS paying_pct,
    ROUND(SUM(p.revenue_usd::numeric), 2)                           AS total_revenue,
    ROUND(SUM(p.revenue_usd::numeric) /
          NULLIF(COUNT(DISTINCT CASE WHEN u.is_paying THEN u.user_id END), 0), 2) AS avg_revenue_per_paying_user
FROM users u
LEFT JOIN purchases p ON u.user_id = p.user_id
GROUP BY u.country
ORDER BY avg_revenue_per_paying_user DESC NULLS LAST;

-- 2. Revenue and purchase type by gender
-- Finding: Female players spend 46% more on skins than male players ($1,521 vs $1,039).
-- Male players dominate battle pass revenue ($1,441 vs $856) and crystals.
-- Non-binary players show proportionally high skin preference similar to female players.
SELECT
    u.gender,
    COUNT(DISTINCT u.user_id)                 AS total_users,
    COUNT(DISTINCT p.purchase_id)             AS total_purchases,
    ROUND(SUM(p.revenue_usd::numeric), 2)     AS total_revenue,
    ROUND(SUM(CASE WHEN p.product_type = 'skin' 
               THEN p.revenue_usd END::numeric), 2)         AS skin_revenue,
    ROUND(SUM(CASE WHEN p.product_type = 'battle_pass' 
               THEN p.revenue_usd END::numeric), 2)         AS battle_pass_revenue,
    ROUND(SUM(CASE WHEN p.product_type = 'crystals' 
               THEN p.revenue_usd END::numeric), 2)         AS crystals_revenue
FROM users u
LEFT JOIN purchases p ON u.user_id = p.user_id
GROUP BY u.gender
ORDER BY total_revenue DESC;

-- 3. Engagement and revenue by device
-- Finding: iOS has more users (2,794 vs 2,206) but Android users show slightly 
-- higher conversion to paying (101 vs 99 paying users despite smaller base).
-- Session duration is nearly identical across platforms (24.0 vs 23.4 min),
-- suggesting platform does not affect engagement depth.
SELECT
    u.device,
    COUNT(DISTINCT u.user_id)                                    AS total_users,
    COUNT(DISTINCT s.session_id)                                 AS total_sessions,
    ROUND(AVG(s.session_duration_min::numeric), 1)               AS avg_session_duration,
    COUNT(DISTINCT CASE WHEN u.is_paying THEN u.user_id END)     AS paying_users,
    ROUND(SUM(p.revenue_usd::numeric), 2)                        AS total_revenue
FROM users u
LEFT JOIN sessions s ON u.user_id = s.user_id
LEFT JOIN purchases p ON u.user_id = p.user_id
GROUP BY u.device
ORDER BY total_revenue DESC;
