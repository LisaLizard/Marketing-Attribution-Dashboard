-- ───────────────────── CHANNEL PERFORMANCE ANALYSIS ──────────────────────────
-- Business question: Which acquisition channel delivers the most value?
-- Key finding: Organic is the most profitable channel (zero spend, highest volume).
-- Email has the highest ROI among paid channels (0.06) but smallest audience.
-- TikTok brings engaged users (19.3 sessions/user) but lowest conversion to paying.

-- 1. Overview: sessions, conversions and revenue by acquisition channel
-- Finding: Google Ads has the highest paying user rate (4.59%) among paid channels.

SELECT
    u.acquisition_channel,
    COUNT(DISTINCT u.user_id)                                    AS total_users,
    COUNT(DISTINCT s.session_id)                                 AS total_sessions,
    ROUND(COUNT(DISTINCT s.session_id)::numeric / 
          COUNT(DISTINCT u.user_id), 1)                          AS sessions_per_user,
    COUNT(DISTINCT CASE WHEN u.is_paying THEN u.user_id END)     AS paying_users,
    ROUND(COUNT(DISTINCT CASE WHEN u.is_paying THEN u.user_id END)::numeric / 
          COUNT(DISTINCT u.user_id) * 100, 2)                    AS paying_pct,
    ROUND(SUM(p.revenue_usd)::numeric, 2)                        AS total_revenue,
    ROUND(SUM(p.revenue_usd)::numeric / 
          NULLIF(COUNT(DISTINCT u.user_id), 0), 2)               AS revenue_per_user
FROM users u
LEFT JOIN sessions s ON u.user_id = s.user_id
LEFT JOIN purchases p ON u.user_id = p.user_id
GROUP BY u.acquisition_channel
ORDER BY total_revenue DESC;


-- 2. Channel ROI: revenue vs ad spend
-- NOTE: 'installs' for email channel is excluded from cost_per_install calculation.
-- Email is a re-engagement channel, not an acquisition channel.
-- Its 'installs' metric reflects click-throughs, not new user installs.
-- Finding: All paid channels have ROI < 1, typical for a game in its first year.

WITH channel_revenue AS (
    SELECT
        u.acquisition_channel,
        COUNT(DISTINCT u.user_id)             AS total_users,
        ROUND(SUM(p.revenue_usd::numeric), 2) AS total_revenue
    FROM users u
    LEFT JOIN purchases p ON p.user_id = u.user_id
    GROUP BY u.acquisition_channel
),
channel_spend AS (
    SELECT
        channel,
        ROUND(SUM(spend_usd::numeric), 2) AS total_spend,
        CASE 
            WHEN channel = 'email' THEN NULL
            ELSE SUM(installs)
        END AS total_installs
    FROM ad_spend
    GROUP BY channel
)
SELECT
    r.acquisition_channel,
    r.total_users,
    r.total_revenue,
    COALESCE(s.total_spend, 0)                               AS total_spend,
    s.total_installs,
    CASE
        WHEN s.total_installs IS NULL OR s.total_installs = 0 THEN NULL
        ELSE ROUND(s.total_spend::numeric / s.total_installs, 2)
    END                                                       AS cost_per_install,
    CASE
        WHEN COALESCE(s.total_spend, 0) = 0 THEN NULL
        ELSE ROUND(r.total_revenue / s.total_spend, 2)
    END                                                       AS roi
FROM channel_revenue r
LEFT JOIN channel_spend s ON r.acquisition_channel = s.channel
ORDER BY cost_per_install NULLS LAST;

-- 3. Monthly revenue and sessions trend by channel
-- Finding: TikTok appears in April 2024 (campaign launch), December spike visible across all channels.

SELECT
    TO_CHAR(s.session_date::date, 'YYYY-MM')  AS month,
    u.acquisition_channel,
    COUNT(DISTINCT s.session_id)              AS total_sessions,
    COUNT(DISTINCT p.purchase_id)             AS total_purchases,
    ROUND(SUM(p.revenue_usd::numeric), 2)     AS monthly_revenue
FROM sessions s
JOIN users u ON s.user_id = u.user_id
LEFT JOIN purchases p ON s.session_id = p.session_id
GROUP BY 1, 2
ORDER BY 1, 2;
