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

## Project structure
- `generate_dataset.py` — synthetic dataset generation script
- `sql/data_quality_check.sql` — data quality checks before analysis
- `sql/channel_performance.sql` — channel overview, ROI analysis, monthly trends
- `sql/attribution_comparison.sql` — last-click vs linear attribution analysis
- `sql/player_segmentation.sql` — revenue and engagement by country, gender, device

## Key findings
- Organic is the most profitable channel: zero spend, highest user volume
- Email has the highest ROI among paid channels (0.06) despite smallest audience
- TikTok attracts engaged users but has the lowest conversion to paying (3.75%)
- All paid channels have ROI < 1 — typical for a mobile game in its first year
- Email is undervalued by 2ppt under last-click attribution — players from email 
  actively play before purchasing, but credit goes to other channels
- Google Ads is undervalued by 2.5ppt — participates more in the player journey 
  than last-click suggests
- Organic is overvalued by 4.6ppt — users convert faster with fewer sessions 
  before purchase
- TikTok is neutral — consistent performance across both attribution models
- - US has the highest avg revenue per paying user ($75.28); Japan leads in conversion rate (4.90%)
- Finland is the largest market but has the lowest conversion rate (3.25%)
- Female players spend 46% more on skins than male players
- Male players dominate battle pass and crystals revenue
- Android users show slightly higher conversion despite smaller audience
