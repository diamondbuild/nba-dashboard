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
# EDGE THRESHOLDS
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
