import pandas as pd
from datetime import datetime

# Read the results history
df = pd.read_csv('results_history.csv')

print(f"📊 Current database: {len(df)} total bets\n")

# Show date breakdown
df['DATE'] = pd.to_datetime(df['DATE'])
date_counts = df.groupby(df['DATE'].dt.date).size()
print("Bets by date:")
for date, count in date_counts.items():
    print(f"  {date}: {count} bets")

# Filter to keep ONLY 2026-01-25 and later
cutoff_date = pd.to_datetime('2026-01-25')
cleaned_df = df[df['DATE'] >= cutoff_date]

print(f"\n✂️ Removing {len(df) - len(cleaned_df)} bets before Jan 25, 2026")
print(f"📊 New database: {len(cleaned_df)} bets\n")

# Save cleaned data
cleaned_df.to_csv('results_history.csv', index=False)
print("✅ Saved cleaned results_history.csv")

# Show stats
valid = cleaned_df[cleaned_df['RESULT'] != 'VOID']
wins = len(valid[valid['RESULT'] == 'WIN'])
losses = len(valid[valid['RESULT'] == 'LOSS'])
win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

print(f"\n📈 Fresh Stats:")
print(f"   Record: {wins}-{losses}")
print(f"   Win Rate: {win_rate:.1f}%")
