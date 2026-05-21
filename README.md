# Marketing-Attribution-Dashboard
Marketing attribution analysis for a mobile RPG game — SQL, Power BI, Excel VBA | Portfolio project

## Project status
In progress

## Data
Synthetic dataset simulating a mobile RPG game (2024, 12 months).
Generated with Python — see `generate_dataset.py`.

## Tables
- `users.csv` — 5,000 users with demographics and acquisition channel
- `sessions.csv` — ~95,000 game sessions (incl. intentional duplicates for DQ check)
- `purchases.csv` — in-app purchases by paying users (4%)
- `ad_spend.csv` — daily ad spend across Google Ads, TikTok, Email, Organic

## Known data quality issues (intentional)
- ~3% null values in `country` column
- ~2% duplicate sessions (tracker bug simulation)
- 3 missing days in `ad_spend` (pipeline failure simulation)
