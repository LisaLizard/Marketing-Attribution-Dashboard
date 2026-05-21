import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

# ── Configuration ──────────────────────────────────────────────────────────────
START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2024, 12, 31)
N_USERS    = 5000
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Reference tables ───────────────────────────────────────────────────────────

COUNTRIES = {
    "Finland":        {"weight": 0.35, "ltv_mult": 1.0},
    "Germany":        {"weight": 0.13, "ltv_mult": 1.1},
    "Sweden":         {"weight": 0.13, "ltv_mult": 1.05},
    "United Kingdom": {"weight": 0.13, "ltv_mult": 1.1},
    "United States":  {"weight": 0.10, "ltv_mult": 1.6},
    "Japan":          {"weight": 0.06, "ltv_mult": 1.7},
    "Brazil":         {"weight": 0.05, "ltv_mult": 0.6},
    "Other":          {"weight": 0.05, "ltv_mult": 0.7},
}

GENDERS = {
    "Male":                 0.52,
    "Female":               0.33,
    "Non-binary":           0.05,
    "Prefer not to answer": 0.10,
}

DEVICES = {
    "iOS":     0.55,
    "Android": 0.45,
}

AGE_GROUPS = {
    "13-17": 0.15,
    "18-24": 0.25,
    "25-34": 0.30,
    "35-44": 0.18,
    "45-54": 0.08,
    "55+":   0.04,
}

CHANNELS = ["google_ads", "tiktok_ads", "email", "organic"]

# Purchase types with base price ranges (USD)
PURCHASE_TYPES = {
    "crystals":    {"min": 0.99,  "max": 9.99,  "weight": 0.55},
    "battle_pass": {"min": 4.99,  "max": 9.99,  "weight": 0.25},
    "skin":        {"min": 2.99,  "max": 19.99, "weight": 0.20},
}

# Gender-based purchase type preference multipliers
# Female players lean toward skins; male players lean toward battle pass
GENDER_PURCHASE_PREFS = {
    "Male":                 {"crystals": 1.0, "battle_pass": 1.3, "skin": 0.8},
    "Female":               {"crystals": 1.0, "battle_pass": 0.9, "skin": 1.5},
    "Non-binary":           {"crystals": 1.0, "battle_pass": 1.0, "skin": 1.1},
    "Prefer not to answer": {"crystals": 1.0, "battle_pass": 1.0, "skin": 1.0},
}

# Monthly seasonal multipliers — December holiday event causes a big spike
MONTHLY_SESSION_MULT = {
    1: 1.0, 2: 0.95, 3: 1.0, 4: 1.05, 5: 1.0,  6: 0.9,
    7: 0.85, 8: 0.9, 9: 1.0, 10: 1.1, 11: 1.2, 12: 1.5,
}
MONTHLY_CONVERSION_MULT = {
    1: 1.0, 2: 0.9, 3: 1.0, 4: 1.0, 5: 0.95, 6: 0.85,
    7: 0.8, 8: 0.85, 9: 1.0, 10: 1.1, 11: 1.25, 12: 2.0,
}

# Weekday multiplier for sessions (0=Monday, 5=Saturday)
WEEKDAY_MULT = {0: 0.85, 1: 0.85, 2: 0.90, 3: 0.90, 4: 1.0, 5: 1.25, 6: 1.20}


# ── Helper functions ───────────────────────────────────────────────────────────

def weighted_choice(options_dict):
    """Pick a key from a dict based on 'weight' sub-key or direct float values."""
    if isinstance(list(options_dict.values())[0], dict):
        keys    = list(options_dict.keys())
        weights = [v["weight"] for v in options_dict.values()]
    else:
        keys    = list(options_dict.keys())
        weights = list(options_dict.values())
    return random.choices(keys, weights=weights, k=1)[0]


def random_date(start, end):
    """Return a random datetime between start and end."""
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def registration_date_for_user(user_index):
    """
    Simulate organic game growth across the year.
    First 10% = early adopters in January.
    April spike = TikTok campaign launch.
    December spike = holiday season new installs.
    """
    if user_index < N_USERS * 0.10:
        return random_date(datetime(2024, 1, 1), datetime(2024, 1, 31))
    month_weights = [5, 5, 6, 14, 8, 7, 7, 8, 9, 9, 10, 12]
    month = random.choices(range(1, 13), weights=month_weights, k=1)[0]
    start = datetime(2024, month, 1)
    end   = datetime(2024, 12, 31) if month == 12 else datetime(2024, month + 1, 1) - timedelta(days=1)
    return random_date(start, end)


def channel_for_user(reg_date):
    """
    TikTok was not active before April 2024.
    Email weight is low — it is mainly a re-engagement channel, not acquisition.
    """
    if reg_date < datetime(2024, 4, 1):
        weights = [0.40, 0.00, 0.05, 0.55]
    else:
        weights = [0.30, 0.30, 0.05, 0.35]
    return random.choices(CHANNELS, weights=weights, k=1)[0]


# ── 1. Generate users ──────────────────────────────────────────────────────────
print("Generating users...")

users = []
for i in range(N_USERS):
    reg_date = registration_date_for_user(i)
    country  = weighted_choice(COUNTRIES)
    gender   = weighted_choice(GENDERS)

    # DATA QUALITY ISSUE #1: ~3% null country (VPN / geolocation denied)
    if random.random() < 0.03:
        country = None

    users.append({
        "user_id":             f"U{str(i+1).zfill(5)}",
        "registration_date":   reg_date.date(),
        "country":             country,
        "gender":              gender,
        "device":              weighted_choice(DEVICES),
        "age_group":           weighted_choice(AGE_GROUPS),
        "acquisition_channel": channel_for_user(reg_date),
        "is_paying":           False,  # updated after purchase generation
    })

users_df = pd.DataFrame(users)
print(f"  {len(users_df):,} users created")


# ── 2. Generate sessions ───────────────────────────────────────────────────────
print("Generating sessions...")

# Mark 4% of users as paying before session loop
paying_user_ids = set(users_df.sample(frac=0.04, random_state=42)["user_id"].tolist())
users_df["is_paying"] = users_df["user_id"].isin(paying_user_ids)

sessions       = []
session_counter = 1

for _, user in users_df.iterrows():
    reg_dt = datetime.combine(pd.to_datetime(user["registration_date"]).date(), datetime.min.time())

    # Paying users play more sessions on average
    n_sessions = random.randint(20, 120) if user["is_paying"] else random.randint(5, 40)

    for _ in range(n_sessions):
        if reg_dt >= END_DATE:
            break
        session_date = random_date(reg_dt, END_DATE)
        month        = session_date.month
        weekday      = session_date.weekday()

        # Skip session probabilistically based on seasonality and weekday
        prob = MONTHLY_SESSION_MULT[month] * WEEKDAY_MULT[weekday] / 1.5
        if random.random() > prob:
            continue

        # Paying users have longer sessions
        if user["is_paying"]:
            duration = round(np.random.lognormal(mean=3.2, sigma=0.5))
        else:
            duration = round(np.random.lognormal(mean=2.8, sigma=0.6))
        duration = max(1, min(duration, 240))

        # Conversion: only possible for paying users, boosted by season
        base_conv = 0.08 if user["is_paying"] else 0.0
        converted = random.random() < (base_conv * MONTHLY_CONVERSION_MULT[month])

        sessions.append({
            "session_id":           f"S{str(session_counter).zfill(7)}",
            "user_id":              user["user_id"],
            "session_date":         session_date.date(),
            "session_duration_min": duration,
            "level_reached":        random.randint(1, 80),
            "converted":            converted,
        })
        session_counter += 1

sessions_df = pd.DataFrame(sessions)

# DATA QUALITY ISSUE #2: ~2% duplicate sessions (event tracker bug)
n_dupes     = int(len(sessions_df) * 0.02)
dupes       = sessions_df.sample(n=n_dupes, random_state=1).copy()
sessions_df = pd.concat([sessions_df, dupes], ignore_index=True)
sessions_df = sessions_df.sample(frac=1, random_state=99).reset_index(drop=True)

print(f"  {len(sessions_df):,} sessions created (including {n_dupes:,} duplicates)")


# ── 3. Generate purchases ──────────────────────────────────────────────────────
print("Generating purchases...")

purchases        = []
purchase_counter = 1

# Only sessions that converted AND belong to a paying user
converted_sessions = sessions_df[
    (sessions_df["converted"] == True) &
    (sessions_df["user_id"].isin(paying_user_ids))
].copy()

for _, session in converted_sessions.iterrows():
    user_row = users_df[users_df["user_id"] == session["user_id"]].iloc[0]
    gender   = user_row["gender"]
    country  = user_row["country"] if pd.notna(user_row["country"]) else "Other"
    ltv_mult = COUNTRIES.get(country, {"ltv_mult": 0.7})["ltv_mult"]

    # Product type weighted by gender preference
    pt_keys    = list(PURCHASE_TYPES.keys())
    pt_weights = [PURCHASE_TYPES[pt]["weight"] * GENDER_PURCHASE_PREFS[gender][pt] for pt in pt_keys]
    product_type = random.choices(pt_keys, weights=pt_weights, k=1)[0]

    pt_info  = PURCHASE_TYPES[product_type]
    revenue  = round(random.uniform(pt_info["min"], pt_info["max"]) * ltv_mult, 2)

    purchases.append({
        "purchase_id":   f"P{str(purchase_counter).zfill(6)}",
        "user_id":       session["user_id"],
        "session_id":    session["session_id"],
        "purchase_date": session["session_date"],
        "product_type":  product_type,
        "revenue_usd":   revenue,
    })
    purchase_counter += 1

purchases_df = pd.DataFrame(purchases)
print(f"  {len(purchases_df):,} purchases created")


# ── 4. Generate ad_spend ───────────────────────────────────────────────────────
print("Generating ad spend...")

CHANNEL_BASE_SPEND   = {"google_ads": 180, "tiktok_ads": 150, "email": 20,  "organic": 0}
CHANNEL_CPM          = {"google_ads": 8.0, "tiktok_ads": 5.0, "email": 0.5, "organic": 0.0}
CHANNEL_CTR          = {"google_ads": 0.04,"tiktok_ads": 0.03,"email": 0.18,"organic": 0.0}
CHANNEL_INSTALL_RATE = {"google_ads": 0.12,"tiktok_ads": 0.06,"email": 0.30,"organic": 0.0}

all_dates = [START_DATE + timedelta(days=i) for i in range((END_DATE - START_DATE).days + 1)]

# DATA QUALITY ISSUE #3: 3 random days missing from ad_spend (pipeline failure)
missing_days = set(random.sample(all_dates[30:], 3))

ad_spend_rows = []
for date in all_dates:
    if date in missing_days:
        continue

    month   = date.month
    weekday = date.weekday()
    seas    = MONTHLY_SESSION_MULT[month]
    wday    = WEEKDAY_MULT[weekday]

    for channel in CHANNELS:
        if channel == "tiktok_ads" and date < datetime(2024, 4, 1):
            continue  # TikTok not running before April

        base_spend = CHANNEL_BASE_SPEND[channel]

        if base_spend == 0:
            # Organic: no spend, but track estimated installs
            ad_spend_rows.append({
                "date":        date.date(),
                "channel":     channel,
                "spend_usd":   0.0,
                "impressions": 0,
                "clicks":      0,
                "installs":    int(np.random.poisson(lam=15 * seas * wday)),
            })
            continue

        spend       = round(base_spend * seas * random.uniform(0.8, 1.2), 2)
        impressions = int((spend / CHANNEL_CPM[channel]) * 1000) if CHANNEL_CPM[channel] > 0 else 0
        clicks      = int(impressions * CHANNEL_CTR[channel])
        installs    = int(clicks * CHANNEL_INSTALL_RATE[channel])

        ad_spend_rows.append({
            "date":        date.date(),
            "channel":     channel,
            "spend_usd":   spend,
            "impressions": impressions,
            "clicks":      clicks,
            "installs":    installs,
        })

ad_spend_df = pd.DataFrame(ad_spend_rows)
print(f"  {len(ad_spend_df):,} ad spend rows created ({len(missing_days)} days missing — intentional)")


# ── 5. Save CSV files ──────────────────────────────────────────────────────────
print("\nSaving CSV files...")

users_df.to_csv(f"{OUTPUT_DIR}/users.csv", index=False)
sessions_df.to_csv(f"{OUTPUT_DIR}/sessions.csv", index=False)
purchases_df.to_csv(f"{OUTPUT_DIR}/purchases.csv", index=False)
ad_spend_df.to_csv(f"{OUTPUT_DIR}/ad_spend.csv", index=False)

print(f"  Saved to /{OUTPUT_DIR}/")
print("\n── Summary ───────────────────────────────────────────────────────────────────")
print(f"  Users:                {len(users_df):,}")
print(f"  Paying users:         {users_df['is_paying'].sum():,}  ({users_df['is_paying'].mean()*100:.1f}%)")
print(f"  Sessions:             {len(sessions_df):,}  (incl. duplicates)")
print(f"  Purchases:            {len(purchases_df):,}")
print(f"  Total revenue:        ${purchases_df['revenue_usd'].sum():,.2f}")
print(f"  Ad spend rows:        {len(ad_spend_df):,}")
print(f"  Total ad spend:       ${ad_spend_df['spend_usd'].sum():,.2f}")
print("\n── Intentional data quality issues ───────────────────────────────────────────")
print(f"  Null country:         {users_df['country'].isna().sum()} users (~3%)")
print(f"  Duplicate sessions:   {n_dupes:,} rows (~2%)")
print(f"  Missing ad_spend days:{len(missing_days)} days")
print("\nDone! All files ready in /data/")