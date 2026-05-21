-- How many duplicate session_ids exist?
SELECT 
    session_id,
    COUNT(*) as occurrences
FROM sessions
GROUP BY session_id
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;

-- Users with missing country (~3% expected)
SELECT 
    COUNT(*) as total_users,
    COUNT(country) as users_with_country,
    COUNT(*) - COUNT(country) as null_country,
    ROUND((COUNT(*) - COUNT(country)) * 100.0 / COUNT(*), 2) as null_pct
FROM users;

-- Find missing dates in ad_spend
SELECT generate_series::date as missing_date
FROM generate_series('2024-01-01'::date, '2024-12-31'::date, '1 day') 
WHERE generate_series::date NOT IN (
    SELECT DISTINCT date FROM ad_spend
);
