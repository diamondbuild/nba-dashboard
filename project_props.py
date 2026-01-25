import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load your game log data
print("Loading game data...")
df = pd.read_csv('nba_game_logs_2025_26.csv')

# Convert date and minutes to proper format
df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
df['MIN'] = pd.to_numeric(df['MIN'], errors='coerce')
df = df[df['MIN'].notna() & (df['MIN'] > 0)]  # Remove games with no minutes

# Sort by player and date
df = df.sort_values(['PLAYER_NAME', 'GAME_DATE'])

print(f"Loaded {len(df)} games for {df['PLAYER_NAME'].nunique()} players")

# Calculate per-minute stats
df['PTS_per_min'] = df['PTS'] / df['MIN']
df['REB_per_min'] = df['REB'] / df['MIN']
df['AST_per_min'] = df['AST'] / df['MIN']
df['FG3M_per_min'] = df['FG3M'] / df['MIN']

# Calculate opponent defensive stats
print("\nCalculating opponent defensive stats...")
df['is_home'] = df['MATCHUP'].str.contains('vs.')
df['opponent'] = df['MATCHUP'].str.split(' ').str[-1]

opponent_stats = df.groupby('opponent').agg({
    'PTS': 'mean',
    'REB': 'mean',
    'AST': 'mean',
    'FG3M': 'mean'
}).reset_index()

opponent_stats.columns = ['team', 'opp_pts_allowed', 'opp_reb_allowed', 'opp_ast_allowed', 'opp_3pm_allowed']
print(f"Calculated defensive stats for {len(opponent_stats)} teams")

# Build projection for each active player
print("\nBuilding player projections...")

projections = []

for player_name in df['PLAYER_NAME'].unique():
    player_df = df[df['PLAYER_NAME'] == player_name].copy()
    
    # Need at least 5 games to make a projection
    if len(player_df) < 5:
        continue
    
    games_played = len(player_df)
    
    # Calculate averages for available games
    last_3_games = player_df.tail(min(3, games_played))
    last_5_games = player_df.tail(min(5, games_played))
    last_10_games = player_df.tail(min(10, games_played))
    
    # Last 3 games averages
    l3_pts = last_3_games['PTS'].mean()
    l3_reb = last_3_games['REB'].mean()
    l3_ast = last_3_games['AST'].mean()
    l3_3pm = last_3_games['FG3M'].mean()
    l3_min = last_3_games['MIN'].mean()
    l3_pts_pm = last_3_games['PTS_per_min'].mean()
    l3_reb_pm = last_3_games['REB_per_min'].mean()
    l3_ast_pm = last_3_games['AST_per_min'].mean()
    l3_3pm_pm = last_3_games['FG3M_per_min'].mean()
    
    # Last 5 games averages
    l5_pts = last_5_games['PTS'].mean()
    l5_reb = last_5_games['REB'].mean()
    l5_ast = last_5_games['AST'].mean()
    l5_3pm = last_5_games['FG3M'].mean()
    l5_min = last_5_games['MIN'].mean()
    l5_pts_pm = last_5_games['PTS_per_min'].mean()
    l5_reb_pm = last_5_games['REB_per_min'].mean()
    l5_ast_pm = last_5_games['AST_per_min'].mean()
    l5_3pm_pm = last_5_games['FG3M_per_min'].mean()
    
    # Last 10 games averages
    l10_pts = last_10_games['PTS'].mean()
    l10_reb = last_10_games['REB'].mean()
    l10_ast = last_10_games['AST'].mean()
    l10_3pm = last_10_games['FG3M'].mean()
    l10_min = last_10_games['MIN'].mean()
    l10_pts_pm = last_10_games['PTS_per_min'].mean()
    l10_reb_pm = last_10_games['REB_per_min'].mean()
    l10_ast_pm = last_10_games['AST_per_min'].mean()
    l10_3pm_pm = last_10_games['FG3M_per_min'].mean()
    
    # Blend: 40% last 3, 30% last 5, 30% last 10
    blended_pts_per_min = 0.4 * l3_pts_pm + 0.3 * l5_pts_pm + 0.3 * l10_pts_pm
    blended_reb_per_min = 0.4 * l3_reb_pm + 0.3 * l5_reb_pm + 0.3 * l10_reb_pm
    blended_ast_per_min = 0.4 * l3_ast_pm + 0.3 * l5_ast_pm + 0.3 * l10_ast_pm
    blended_3pm_per_min = 0.4 * l3_3pm_pm + 0.3 * l5_3pm_pm + 0.3 * l10_3pm_pm
    
    # Blend minutes: 70% last 5, 30% last 10
    blended_minutes = 0.7 * l5_min + 0.3 * l10_min
    
    # Base projections
    proj_pts = blended_pts_per_min * blended_minutes
    proj_reb = blended_reb_per_min * blended_minutes
    proj_ast = blended_ast_per_min * blended_minutes
    proj_3pm = blended_3pm_per_min * blended_minutes
    
    projections.append({
        'PLAYER': player_name,
        'PROJ_MIN': round(blended_minutes, 1),
        'PROJ_PTS': round(proj_pts, 1),
        'PROJ_REB': round(proj_reb, 1),
        'PROJ_AST': round(proj_ast, 1),
        'PROJ_3PM': round(proj_3pm, 1),
        'PROJ_PRA': round(proj_pts + proj_reb + proj_ast, 1),
        'L3_PTS': round(l3_pts, 1),
        'L5_PTS': round(l5_pts, 1),
        'L10_PTS': round(l10_pts, 1),
        'games_played': games_played
    })

# Convert to DataFrame and sort
proj_df = pd.DataFrame(projections)
proj_df = proj_df.sort_values('PROJ_PTS', ascending=False)

# Save to CSV
output_file = 'player_projections.csv'
proj_df.to_csv(output_file, index=False)

print(f"\nSuccess! Created projections for {len(proj_df)} players")
print(f"Saved to: {output_file}")

# Show top 20 projected scorers
print("\n=== TOP 20 PROJECTED SCORERS ===")
print(proj_df[['PLAYER', 'PROJ_MIN', 'PROJ_PTS', 'PROJ_REB', 'PROJ_AST', 'PROJ_3PM', 'PROJ_PRA']].head(20).to_string(index=False))

# Show some high-profile players
print("\n=== SAMPLE STAR PLAYERS ===")
sample_players = ['LeBron James', 'Stephen Curry', 'Nikola Jokic', 'Giannis Antetokounmpo', 
                  'Luka Doncic', 'Joel Embiid', 'Kevin Durant', 'Jayson Tatum']

for player in sample_players:
    player_row = proj_df[proj_df['PLAYER'] == player]
    if not player_row.empty:
        print(f"\n{player}:")
        print(f"  Projected: {player_row['PROJ_PTS'].values[0]} PTS | {player_row['PROJ_REB'].values[0]} REB | {player_row['PROJ_AST'].values[0]} AST | {player_row['PROJ_3PM'].values[0]} 3PM")
        print(f"  PRA: {player_row['PROJ_PRA'].values[0]} | Based on {player_row['games_played'].values[0]} games")
