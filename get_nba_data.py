from nba_api.stats.endpoints import leaguegamefinder, leaguedashplayerstats
import pandas as pd
import time
from datetime import datetime, timedelta

print("Getting active players from 2025-26 season...")

# Get all players who have played in 2025-26
current_season = leaguedashplayerstats.LeagueDashPlayerStats(
    season='2025-26',
    season_type_all_star='Regular Season',
    timeout=60
)

active_players = current_season.get_data_frames()[0]

# FILTER OUT INACTIVE PLAYERS - Only keep players with significant minutes
active_players = active_players[active_players['MIN'] >= 880]  # At least 50 total minutes this season
active_players = active_players.sort_values('MIN', ascending=False)

print(f"Found {len(active_players)} active players with 50+ minutes played")

# Calculate date range (last 15 days)
today = datetime.now()
days_back = 15
lookback_date = today - timedelta(days=days_back)
date_from = lookback_date.strftime('%m/%d/%Y')
date_to = today.strftime('%m/%d/%Y')

print(f"\nFetching games from {date_from} to {date_to} (last {days_back} days)")

all_game_logs = []

# Now get game logs for only active players (LAST 15 DAYS ONLY)
for player_num, (idx, row) in enumerate(active_players.iterrows(), start=1):
    player_id = row['PLAYER_ID']
    player_name = row['PLAYER_NAME']
    
    if player_num % 20 == 0:
        print(f"Processing {player_num} of {len(active_players)}: {player_name}")
    
    try:
        # Get last 15 days of games only
        gamefinder = leaguegamefinder.LeagueGameFinder(
            player_or_team_abbreviation='P',
            player_id_nullable=player_id,
            season_nullable='2025-26',
            season_type_nullable='Regular Season',
            date_from_nullable=date_from,
            date_to_nullable=date_to,
            timeout=30
        )
        
        games = gamefinder.get_data_frames()[0]
        
        if not games.empty:
            all_game_logs.append(games)
        
        time.sleep(0.6)
        
    except ValueError as ve:
        # JSON parsing error - player has no games in date range
        if "Expecting value" in str(ve):
            print(f"  ℹ️ {player_name}: No games in last 15 days (likely injured/resting)")
        else:
            print(f"  ⚠️ ValueError with {player_name}: {str(ve)[:80]}")
        time.sleep(1)
        continue
        
    except Exception as e:
        print(f"  ⚠️ Error with {player_name}: {str(e)[:80]}")
        time.sleep(2)
        continue



# Combine all data
print("\nCombining data...")
if all_game_logs:
    final_df = pd.concat(all_game_logs, ignore_index=True)
    
    # Keep important columns
    columns_to_keep = [
        'PLAYER_NAME', 'PLAYER_ID', 'GAME_DATE', 'MATCHUP', 
        'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG3M',
        'FGA', 'FG_PCT', 'FTA', 'PLUS_MINUS', 'WL'
    ]
    
    final_df = final_df[columns_to_keep]
    
    # Sort by date
    final_df = final_df.sort_values('GAME_DATE', ascending=False)
    
    output_file = 'nba_game_logs_2025_26.csv'
    final_df.to_csv(output_file, index=False)
    
    print(f"\nSuccess! Saved {len(final_df)} games to {output_file}")
    print(f"Players with data: {final_df['PLAYER_NAME'].nunique()}")
    print(f"Date range: {final_df['GAME_DATE'].min()} to {final_df['GAME_DATE'].max()}")
else:
    print("No data found")
