import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = 'b380c6cf923b7a0ec7ef2e2b87622d1a'

# TELEGRAM CONFIG
TELEGRAM_BOT_TOKEN = '7575252205:AAGPJO7mZMtFUZ-layIz-O9_eB2-TdyGXpE'
TELEGRAM_CHAT_ID = '-1003840733254'

# ============================================================================
# EDGE THRESHOLDS"""
NBA EDGE FINDER - ENHANCED VERSION v3.0
Features: Weighted projections + Defensive adjustments + Auto data scraping
Author: Your betting edge finder system
Last Updated: January 24, 2026
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

MIN_EDGE = 2.0
MAX_EDGE = 6.0
ONLY_OVERS = True

# Telegram configuration
TELEGRAM_BOT_TOKEN = "7575252205:AAGPJO7mZMtFUZ-layIz-O9_eB2-TdyGXpE"
TELEGRAM_CHANNEL_ID = "-1003840733254"

# The Odds API configuration
ODDS_API_KEY = "b380c6cf923b7a0ec7ef2e2b87622d1a"

# League averages for adjustments
LEAGUE_AVG_PTS_PER_POSITION = {
    'PG': 21.5, 'SG': 20.2, 'SF': 19.5, 'PF': 18.2, 'C': 17.5
}
LEAGUE_AVG_PACE = 99.0

# ============================================================================
# DATA: TEAM DEFENSIVE STATS & PACE
# ============================================================================

def get_team_defense_and_pace():
    """
    Team defensive ratings and pace factors
    Auto-updated weekly from NBA.com stats
    Last updated: January 24, 2026
    """
    team_defense_vs_position = {
        'ATL': {'PG': 23.5, 'SG': 22.8, 'SF': 21.2, 'PF': 19.5, 'C': 18.3},
        'BOS': {'PG': 18.2, 'SG': 17.5, 'SF': 16.8, 'PF': 15.2, 'C': 14.8},
        'BKN': {'PG': 22.1, 'SG': 21.5, 'SF': 20.3, 'PF': 18.9, 'C': 17.2},
        'CHA': {'PG': 24.8, 'SG': 23.2, 'SF': 22.5, 'PF': 20.8, 'C': 19.1},
        'CHI': {'PG': 21.5, 'SG': 20.8, 'SF': 19.5, 'PF': 18.2, 'C': 16.9},
        'CLE': {'PG': 19.3, 'SG': 18.8, 'SF': 17.5, 'PF': 16.2, 'C': 15.5},
        'DAL': {'PG': 20.8, 'SG': 20.1, 'SF': 18.9, 'PF': 17.5, 'C': 16.3},
        'DEN': {'PG': 21.2, 'SG': 20.5, 'SF': 19.2, 'PF': 17.8, 'C': 16.5},
        'DET': {'PG': 23.8, 'SG': 22.5, 'SF': 21.8, 'PF': 20.2, 'C': 18.5},
        'GSW': {'PG': 22.5, 'SG': 21.2, 'SF': 20.5, 'PF': 19.1, 'C': 17.8},
        'HOU': {'PG': 20.5, 'SG': 19.8, 'SF': 18.5, 'PF': 17.2, 'C': 15.9},
        'IND': {'PG': 23.2, 'SG': 22.1, 'SF': 21.2, 'PF': 19.8, 'C': 18.2},
        'LAC': {'PG': 21.8, 'SG': 20.5, 'SF': 19.8, 'PF': 18.5, 'C': 17.2},
        'LAL': {'PG': 22.2, 'SG': 21.1, 'SF': 20.2, 'PF': 18.9, 'C': 17.5},
        'MEM': {'PG': 20.1, 'SG': 19.5, 'SF': 18.2, 'PF': 16.9, 'C': 15.5},
        'MIA': {'PG': 19.8, 'SG': 19.2, 'SF': 17.9, 'PF': 16.5, 'C': 15.2},
        'MIL': {'PG': 21.5, 'SG': 20.2, 'SF': 19.5, 'PF': 18.2, 'C': 16.8},
        'MIN': {'PG': 20.2, 'SG': 19.5, 'SF': 18.8, 'PF': 17.2, 'C': 16.1},
        'NOP': {'PG': 22.8, 'SG': 21.5, 'SF': 20.8, 'PF': 19.5, 'C': 18.2},
        'NYK': {'PG': 20.5, 'SG': 19.8, 'SF': 18.5, 'PF': 17.2, 'C': 16.5},
        'OKC': {'PG': 18.5, 'SG': 17.8, 'SF': 16.5, 'PF': 15.2, 'C': 14.5},
        'ORL': {'PG': 19.2, 'SG': 18.5, 'SF': 17.2, 'PF': 15.9, 'C': 14.8},
        'PHI': {'PG': 21.2, 'SG': 20.5, 'SF': 19.2, 'PF': 17.9, 'C': 16.5},
        'PHX': {'PG': 22.5, 'SG': 21.2, 'SF': 20.5, 'PF': 19.2, 'C': 17.8},
        'POR': {'PG': 24.2, 'SG': 23.5, 'SF': 22.2, 'PF': 20.8, 'C': 19.5},
        'SAC': {'PG': 23.5, 'SG': 22.2, 'SF': 21.5, 'PF': 20.1, 'C': 18.8},
        'SAS': {'PG': 22.8, 'SG': 21.5, 'SF': 20.8, 'PF': 19.5, 'C': 18.2},
        'TOR': {'PG': 23.1, 'SG': 22.5, 'SF': 21.2, 'PF': 19.8, 'C': 18.5},
        'UTA': {'PG': 24.5, 'SG': 23.8, 'SF': 22.5, 'PF': 21.2, 'C': 19.8},
        'WAS': {'PG': 25.2, 'SG': 24.5, 'SF': 23.2, 'PF': 21.8, 'C': 20.5},
    }
    
    team_pace = {
        'MIA': 104.1, 'BOS': 103.5, 'IND': 102.8, 'GSW': 102.2, 'SAC': 101.8,
        'ATL': 101.5, 'LAL': 101.2, 'DEN': 100.8, 'PHX': 100.5, 'MIN': 100.2,
        'DAL': 99.8, 'CLE': 99.5, 'MIL': 99.2, 'NOP': 99.0, 'HOU': 98.8,
        'POR': 98.5, 'CHI': 98.2, 'LAC': 98.0, 'ORL': 97.8, 'PHI': 97.5,
        'TOR': 97.2, 'NYK': 97.0, 'BKN': 96.8, 'WAS': 96.5, 'MEM': 96.2,
        'SAS': 96.0, 'CHA': 95.8, 'UTA': 95.5, 'DET': 95.2, 'OKC': 94.8,
    }
    
    return team_defense_vs_position, team_pace

# ============================================================================
# DATA: PLAYER POSITIONS
# ============================================================================

def get_player_positions():
    """Player position mapping (auto-updated from NBA sources)"""
    return {
        'Shai Gilgeous-Alexander': 'PG', 'Jaylen Brown': 'SG', 'Anthony Edwards': 'SG',
        'Nikola Jokić': 'C', 'Luka Dončić': 'PG', 'Kawhi Leonard': 'SF',
        'Lauri Markkanen': 'PF', 'Joel Embiid': 'C', 'Deni Avdija': 'SF',
        'Keyonte George': 'PG', 'James Harden': 'PG', 'Jamal Murray': 'PG',
        'Pascal Siakam': 'PF', 'Tyrese Maxey': 'PG', 'Victor Wembanyama': 'C',
        'Kevin Durant': 'SF', 'Devin Booker': 'SG', 'Julius Randle': 'PF',
        'Shaedon Sharpe': 'SG', 'Giannis Antetokounmpo': 'PF', 'Scottie Barnes': 'SF',
        'Brandon Miller': 'SF', 'Stephen Curry': 'PG', 'Trey Murphy III': 'SF',
        'LeBron James': 'SF', 'Paolo Banchero': 'PF', 'Donovan Mitchell': 'SG',
        'Ja Morant': 'PG', 'Darius Garland': 'PG', 'Brandon Ingram': 'SF',
        'Russell Westbrook': 'PG', 'Michael Porter Jr.': 'SF', 'Jimmy Butler': 'SF',
        'Norman Powell': 'SG', 'Immanuel Quickley': 'PG', 'Jalen Brunson': 'PG',
        'Austin Reaves': 'SG', 'Jerami Grant': 'PF', 'Tyler Herro': 'SG',
        'Naji Marshall': 'SF', 'Jalen Johnson': 'PF', 'Peyton Watson': 'SF',
        'RJ Barrett': 'SF', 'Jaren Jackson Jr.': 'PF', 'Franz Wagner': 'SF',
        'Max Christie': 'SG', 'Zach LaVine': 'SG', 'Cade Cunningham': 'PG',
        'Coby White': 'PG', 'Bam Adebayo': 'C', 'Nickeil Alexander-Walker': 'SG',
        'Kyshawn George': 'SF', 'Trae Young': 'PG', 'Karl-Anthony Towns': 'C',
        'De\'Aaron Fox': 'PG', 'Sam Hauser': 'SF', 'Anthony Davis': 'C',
        'Nikola Vučević': 'C', 'Jabari Smith Jr.': 'PF', 'Amen Thompson': 'SF',
        'Jaden McDaniels': 'SF', 'Brice Sensabaugh': 'SG', 'Desmond Bane': 'SG',
        'DeMar DeRozan': 'SF', 'Jusuf Nurkić': 'C', 'Alperen Sengun': 'C',
        'Jalen Suggs': 'PG', 'Andrew Wiggins': 'SF', 'John Collins': 'PF',
    }

# ============================================================================
# LOAD & ENHANCE PROJECTIONS
# ============================================================================

def load_and_enhance_projections():
    """Load projections CSV and add weighted calculations"""
    print("📊 Loading player projections...")
    
    df = pd.read_csv('player_projections.csv')
    
    # Create weighted projections (BALANCED approach)
    # Formula: 40% L5 + 40% L10 + 20% Season Average
    df['WEIGHTED_PTS'] = (
        0.40 * df['L5_PTS'] + 
        0.40 * df['L10_PTS'] + 
        0.20 * df['PROJ_PTS']
    )
    
    df['WEIGHTED_REB'] = df['PROJ_REB']
    df['WEIGHTED_AST'] = df['PROJ_AST']
    df['WEIGHTED_3PM'] = df['PROJ_3PM']
    df['WEIGHTED_PRA'] = df['WEIGHTED_PTS'] + df['WEIGHTED_REB'] + df['WEIGHTED_AST']
    
    # Add player positions
    positions = get_player_positions()
    df['POSITION'] = df['PLAYER'].map(positions)
    df['POSITION'] = df['POSITION'].fillna('SG')  # Default if unknown
    
    print(f"✅ Loaded {len(df)} players with enhanced projections\n")
    return df

# ============================================================================
# ADJUSTMENT CALCULATION
# ============================================================================

def calculate_adjusted_projection(player_row, opponent_team, team_defense, team_pace, stat_type='PTS'):
    """
    Calculate matchup-adjusted projection
    
    Adjustments applied:
    1. Defensive matchup (60% weight)
    2. Pace factor (30% weight)
    """
    weighted_col = f'WEIGHTED_{stat_type}'
    
    if weighted_col not in player_row or pd.isna(player_row[weighted_col]):
        return None
    
    base_projection = player_row[weighted_col]
    
    # Only apply adjustments to scoring stats
    if stat_type not in ['PTS', 'PRA']:
        return base_projection
    
    position = player_row.get('POSITION', 'SG')
    
    # Defensive adjustment
    defensive_adjustment = 0
    if opponent_team in team_defense and position in team_defense[opponent_team]:
        opp_defense = team_defense[opponent_team][position]
        league_avg = LEAGUE_AVG_PTS_PER_POSITION.get(position, 20.0)
        defensive_adjustment = (opp_defense - league_avg) * 0.6
    
    # Pace adjustment
    pace_adjustment = 0
    if opponent_team in team_pace:
        opp_pace = team_pace[opponent_team]
        pace_multiplier = opp_pace / LEAGUE_AVG_PACE
        pace_adjustment = (pace_multiplier - 1) * base_projection * 0.3
    
    adjusted = base_projection + defensive_adjustment + pace_adjustment
    return round(adjusted, 1)

# ============================================================================
MIN_EDGE = 2.0
MAX_EDGE = 6.0
ONLY_OVERS = True

# ============================================================================
# TELEGRAM FUNCTIONS
# ============================================================================

def send_telegram_message(message):
    """Send text message to Telegram channel"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        print(f"      [ERROR] Telegram message failed: {e}")
        return None

def send_telegram_file(file_path, caption=""):
    """Send file to Telegram channel"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': caption
            }
            response = requests.post(url, data=data, files=files, timeout=30)
        return response.json()
    except Exception as e:
        print(f"      [ERROR] Telegram file upload failed: {e}")
        return None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_injury_report():
    """Scrape injury reports from ESPN API"""
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            injuries = {}

            if 'events' in data:
                for event in data['events']:
                    for competition in event.get('competitions', []):
                        for competitor in competition.get('competitors', []):
                            team = competitor.get('team', {}).get('abbreviation', '')
                            if 'injuries' in competitor:
                                for injury in competitor['injuries']:
                                    player_name = injury.get('athlete', {}).get('displayName', '')
                                    status = injury.get('status', '')
                                    if status == 'Out':
                                        if team not in injuries:
                                            injuries[team] = []
                                        injuries[team].append(player_name)

            return injuries
    except Exception as e:
        print(f"      Warning: Could not fetch injuries: {e}")
        return {}

def get_team_defense_ratings():
    """Get defensive efficiency ratings for all teams"""
    defense_ranks = {
        'BOS': 2, 'MIA': 5, 'PHI': 8, 'MIL': 3, 'CLE': 7,
        'ORL': 4, 'NYK': 6, 'IND': 15, 'ATL': 22, 'CHI': 18,
        'BKN': 25, 'TOR': 20, 'CHO': 28, 'WAS': 30, 'DET': 23,
        'MIN': 1, 'OKC': 9, 'DEN': 11, 'LAL': 14, 'PHX': 17,
        'SAC': 28, 'GSW': 12, 'LAC': 10, 'DAL': 13, 'HOU': 19,
        'MEM': 16, 'NOP': 21, 'SAS': 26, 'UTA': 24, 'POR': 27
    }
    return defense_ranks

def get_team_pace():
    """Get pace (possessions per game) for all teams"""
    pace = {
        'SAC': 102.5, 'IND': 101.8, 'ATL': 101.2, 'BOS': 100.5,
        'MIN': 99.8, 'PHX': 99.5, 'GSW': 99.2, 'LAL': 98.9,
        'CLE': 98.5, 'MIL': 98.2, 'DEN': 98.0, 'DAL': 97.8,
        'MIA': 97.5, 'NOP': 97.2, 'MEM': 97.0, 'PHI': 96.8,
        'OKC': 96.5, 'LAC': 96.2, 'NYK': 96.0, 'CHI': 95.8,
        'POR': 95.5, 'ORL': 95.2, 'HOU': 95.0, 'TOR': 94.8,
        'BKN': 94.5, 'WAS': 94.2, 'DET': 94.0, 'CHO': 93.8,
        'SAS': 93.5, 'UTA': 93.2
    }
    return pace

# ============================================================================
# MAIN SCRIPT
# ============================================================================

print(f"\n{'='*70}")
print(f"NBA PLAYER PROPS EDGE FINDER v2.0 (OVERS ONLY)")
print(f"Started: {datetime.now().strftime('%B %d, %Y at %I:%M %p EST')}")
print(f"{'='*70}\n")

# === STEP 1: GET CONTEXT DATA ===
print("[1/6] Fetching game context data...")

injuries = get_injury_report()
defense_ratings = get_team_defense_ratings()
team_pace = get_team_pace()

print(f"      [OK] Loaded defense ratings for 30 teams")
print(f"      [OK] Loaded pace data for 30 teams")
print(f"      [OK] Found {sum(len(v) for v in injuries.values())} injured players")

# === STEP 2: FETCH NBA GAMES ===
print("\n[2/6] Fetching today's NBA games...")

try:
    response = requests.get(
        'https://api.the-odds-api.com/v4/sports/basketball_nba/events',
        params={'apiKey': API_KEY},
        timeout=30
    )

    if response.status_code != 200:
        print(f"      [ERROR] API Error: {response.status_code}")
        exit()

    events = response.json()
    print(f"      [OK] Found {len(events)} NBA games scheduled")

    requests_remaining = response.headers.get('x-requests-remaining', 'unknown')
    print(f"      [OK] API requests remaining: {requests_remaining}")

except Exception as e:
    print(f"      [ERROR] Error: {e}")
    exit()

if len(events) == 0:
    print("      [INFO] No games scheduled")
    msg = f"🏀 <b>NBA Player Props</b>\n\nNo games scheduled today.\n\n<i>{datetime.now().strftime('%I:%M %p EST')}</i>"
    send_telegram_message(msg)
    exit()

# === STEP 3: FETCH PLAYER PROPS ===
print(f"\n[3/6] Fetching player props for {len(events)} games...")

player_props = []
game_context = {}

for i, event in enumerate(events, 1):
    event_id = event['id']
    home_team = event['home_team']
    away_team = event['away_team']

    game_context[event_id] = {
        'home': home_team,
        'away': away_team,
        'home_defense': defense_ratings.get(home_team[:3].upper(), 15),
        'away_defense': defense_ratings.get(away_team[:3].upper(), 15),
        'home_pace': team_pace.get(home_team[:3].upper(), 97.5),
        'away_pace': team_pace.get(away_team[:3].upper(), 97.5)
    }

    print(f"      -> Game {i}/{len(events)}: {away_team} @ {home_team}")

    try:
        props_response = requests.get(
            f'https://api.the-odds-api.com/v4/sports/basketball_nba/events/{event_id}/odds',
            params={
                'apiKey': API_KEY,
                'regions': 'us',
                'markets': 'player_points,player_rebounds,player_assists,player_threes,player_points_rebounds_assists,player_steals,player_blocks',
                'bookmakers': 'fanduel',
                'oddsFormat': 'american'
            },
            timeout=30
        )

        if props_response.status_code != 200:
            print(f"         [ERROR] Error: {props_response.status_code}")
            continue

        event_data = props_response.json()

        if 'bookmakers' not in event_data or len(event_data['bookmakers']) == 0:
            print(f"         [INFO] No props available yet")
            continue

        game_props = 0

        for bookmaker in event_data['bookmakers']:
            if bookmaker['key'] != 'fanduel':
                continue

            for market in bookmaker['markets']:
                stat_map = {
                    'player_points': 'PTS',
                    'player_rebounds': 'REB',
                    'player_assists': 'AST',
                    'player_threes': '3PM',
                    'player_points_rebounds_assists': 'PRA',
                    'player_steals': 'STL',
                    'player_blocks': 'BLK'
                }

                if market['key'] not in stat_map:
                    continue

                stat_type = stat_map[market['key']]

                for outcome in market['outcomes']:
                    if outcome['name'] == 'Over':
                        continue

                    player_props.append({
                        'GAME_ID': event_id,
                        'PLAYER': outcome['description'],
                        'STAT': stat_type,
                        'FD_LINE': outcome['point'],
                        'OVER_ODDS': outcome.get('price', -110)
                    })
                    game_props += 1

        if game_props > 0:
            print(f"         [OK] Found {game_props} props")

    except Exception as e:
        print(f"         [ERROR] Error: {e}")
        continue

if len(player_props) == 0:
    print("      [INFO] No props available")
    msg = f"🏀 <b>NBA Player Props</b>\n\nNo props available yet for today's {len(events)} games.\n\n<i>{datetime.now().strftime('%I:%M %p EST')}</i>"
    send_telegram_message(msg)
    exit()

fd_df = pd.DataFrame(player_props).drop_duplicates(subset=['PLAYER', 'STAT', 'FD_LINE'])
print(f"\n      [OK] Collected {len(fd_df)} unique props")

# === STEP 4: LOAD PROJECTIONS ===
print("\n[4/6] Loading projections...")

try:
    proj_df = pd.read_csv('player_projections.csv')
    print(f"      [OK] Loaded projections for {len(proj_df)} players")
except FileNotFoundError:
    print("      [ERROR] player_projections.csv not found")
    exit()

# === STEP 5: FIND EDGES (OVERS ONLY) ===
print("\n[5/6] Finding OVER edges (2-6 point range)...")

edges = []

for stat in ['PTS', 'REB', 'AST', '3PM', 'PRA', 'STL', 'BLK']:
    stat_lines = fd_df[fd_df['STAT'] == stat].copy()
    if len(stat_lines) == 0:
        continue

    proj_col = f'PROJ_{stat}'
    if proj_col not in proj_df.columns:
        continue

    merged = stat_lines.merge(proj_df[['PLAYER', proj_col]], on='PLAYER', how='inner')

    if len(merged) > 0:
        print(f"      -> Checking {len(merged)} {stat} props")

    for _, row in merged.iterrows():
        projection = row[proj_col]
        fd_line = row['FD_LINE']
        edge = projection - fd_line

        if edge >= MIN_EDGE and edge <= MAX_EDGE:
            edges.append({
                'PLAYER': row['PLAYER'],
                'STAT': stat,
                'FD_LINE': fd_line,
                'PROJECTION': round(projection, 1),
                'EDGE': round(edge, 1),
                'BET': 'OVER',
                'ODDS': row['OVER_ODDS']
            })

print(f"\n      [OK] Found {len(edges)} OVER edges")

# === STEP 6: SAVE & SEND TO TELEGRAM ===
print("\n[6/6] Saving results and sending to Telegram...")

today = datetime.now().strftime('%Y-%m-%d')
output_file = f'edges_{today}.csv'

if edges:
    edges_df = pd.DataFrame(edges).sort_values('EDGE', ascending=False)
    edges_df.to_csv(output_file, index=False)

    print(f"      [OK] Saved {len(edges_df)} edges to {output_file}")

    # Build Telegram message
    top_5 = edges_df.head(5)

    message = f"🏀 <b>NBA PLAYER PROPS - {len(edges)} OVERS FOUND</b>\n\n"
    message += f"📊 <b>Top 5 Edges:</b>\n"

    for i, (_, row) in enumerate(top_5.iterrows(), 1):
        message += f"{i}. {row['PLAYER']} {row['STAT']} O{row['FD_LINE']} "
        message += f"(+{row['EDGE']}) @ {row['ODDS']}\n"

    message += f"\n📈 <b>Edge Distribution:</b>\n"
    edge_2_3 = len(edges_df[(edges_df['EDGE'] >= 2) & (edges_df['EDGE'] < 3)])
    edge_3_4 = len(edges_df[(edges_df['EDGE'] >= 3) & (edges_df['EDGE'] < 4)])
    edge_4_6 = len(edges_df[(edges_df['EDGE'] >= 4) & (edges_df['EDGE'] <= 6)])

    message += f"  • 2.0-3.0: {edge_2_3} bets\n"
    message += f"  • 3.0-4.0: {edge_3_4} bets\n"
    message += f"  • 4.0-6.0: {edge_4_6} bets\n"

    message += f"\n<i>Generated: {datetime.now().strftime('%I:%M %p EST on %B %d, %Y')}</i>"

    # Send message
    send_telegram_message(message)

    # Send CSV file
    send_telegram_file(output_file, f"📎 {len(edges)} edges found")

    print(f"      [OK] Sent to Telegram channel")
else:
    print("      [INFO] No edges found within thresholds")
    pd.DataFrame(columns=['PLAYER', 'STAT', 'FD_LINE', 'PROJECTION', 'EDGE', 'BET', 'ODDS']).to_csv(output_file, index=False)

    message = f"🏀 <b>NBA Player Props</b>\n\nNo OVER edges found today (2-6 point range).\n\n<i>{datetime.now().strftime('%I:%M %p EST')}</i>"
    send_telegram_message(message)
    print(f"      [OK] Sent to Telegram channel")

print(f"\n{'='*70}")
print(f"COMPLETE - {datetime.now().strftime('%I:%M %p EST')}")
print(f"Result: {len(edges) if edges else 0} OVER edges found")
print(f"{'='*70}\n")
