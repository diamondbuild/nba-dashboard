from nba_api.stats.endpoints import leaguegamefinder, leaguedashplayerstats
import pandas as pd
import time

print("Getting active players from 2025-26 season...")

# Get all players who have played in 2025-26 (much faster!)
current_season = leaguedashplayerstats.LeagueDashPlayerStats(
    season='2025-26',
    season_type_all_star='Regular Season',
    timeout=60
)

active_players = current_season.get_data_frames()[0]
print(f"Found {len(active_players)} active players in 2025-26")

all_game_logs = []

# Now get game logs for only these active players
for idx, row in active_players.iterrows():
    player_id = row['PLAYER_ID']
    player_name = row['PLAYER_NAME']
    
    if idx % 20 == 0:
        print(f"Processing {idx + 1} of {len(active_players)}: {player_name}")
    
    try:
        # Get 2025-26 games
        gamefinder = leaguegamefinder.LeagueGameFinder(
            player_or_team_abbreviation='P',
            player_id_nullable=player_id,
            season_nullable='2025-26',
            season_type_nullable='Regular Season',
            timeout=60
        )
        
        games = gamefinder.get_data_frames()[0]
        
        if not games.empty:
            all_game_logs.append(games)
        
        time.sleep(0.6)
        
    except Exception as e:
        print(f"  Error with {player_name}: {str(e)[:50]}")
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
