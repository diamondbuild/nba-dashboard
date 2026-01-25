import requests
import pandas as pd
from datetime import datetime
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
# TEAM DATA
# ============================================================================

TEAM_PPG = {
    'Boston Celtics': 119.2, 'BOS': 119.2,
    'Cleveland Cavaliers': 118.5, 'CLE': 118.5,
    'New York Knicks': 115.8, 'NYK': 115.8,
    'Orlando Magic': 112.3, 'ORL': 112.3,
    'Miami Heat': 111.5, 'MIA': 111.5,
    'Milwaukee Bucks': 117.2, 'MIL': 117.2,
    'Philadelphia 76ers': 111.8, 'PHI': 111.8,
    'Indiana Pacers': 120.1, 'IND': 120.1,
    'Chicago Bulls': 113.6, 'CHI': 113.6,
    'Atlanta Hawks': 116.4, 'ATL': 116.4,
    'Brooklyn Nets': 108.9, 'BKN': 108.9,
    'Charlotte Hornets': 107.2, 'CHO': 107.2,
    'Toronto Raptors': 109.5, 'TOR': 109.5,
    'Detroit Pistons': 110.3, 'DET': 110.3,
    'Washington Wizards': 105.8, 'WAS': 105.8,
    'Oklahoma City Thunder': 117.6, 'OKC': 117.6,
    'Denver Nuggets': 116.8, 'DEN': 116.8,
    'Minnesota Timberwolves': 114.7, 'MIN': 114.7,
    'Sacramento Kings': 118.3, 'SAC': 118.3,
    'Phoenix Suns': 115.9, 'PHX': 115.9,
    'Los Angeles Lakers': 115.2, 'LAL': 115.2,
    'Golden State Warriors': 113.9, 'GSW': 113.9,
    'Dallas Mavericks': 116.5, 'DAL': 116.5,
    'LA Clippers': 112.7, 'LAC': 112.7,
    'Houston Rockets': 113.4, 'HOU': 113.4,
    'Memphis Grizzlies': 114.1, 'MEM': 114.1,
    'New Orleans Pelicans': 110.6, 'NOP': 110.6,
    'Los Angeles Clippers': 112.7,
    'Utah Jazz': 109.8, 'UTA': 109.8,
    'San Antonio Spurs': 108.5, 'SAS': 108.5,
    'Portland Trail Blazers': 106.9, 'POR': 106.9,
}

TEAM_OPP_PPG = {
    'Boston Celtics': 108.5, 'BOS': 108.5,
    'Cleveland Cavaliers': 109.2, 'CLE': 109.2,
    'Orlando Magic': 107.8, 'ORL': 107.8,
    'Minnesota Timberwolves': 106.9, 'MIN': 106.9,
    'Oklahoma City Thunder': 108.1, 'OKC': 108.1,
    'Milwaukee Bucks': 110.3, 'MIL': 110.3,
    'Miami Heat': 109.8, 'MIA': 109.8,
    'New York Knicks': 110.5, 'NYK': 110.5,
    'Philadelphia 76ers': 111.2, 'PHI': 111.2,
    'LA Clippers': 111.8, 'LAC': 111.8,
    'Los Angeles Clippers': 111.8,
    'Dallas Mavericks': 112.1, 'DAL': 112.1,
    'Denver Nuggets': 112.5, 'DEN': 112.5,
    'Golden State Warriors': 113.2, 'GSW': 113.2,
    'Los Angeles Lakers': 113.6, 'LAL': 113.6,
    'Indiana Pacers': 117.8, 'IND': 117.8,
    'Memphis Grizzlies': 113.9, 'MEM': 113.9,
    'Houston Rockets': 114.2, 'HOU': 114.2,
    'Chicago Bulls': 114.5, 'CHI': 114.5,
    'Phoenix Suns': 115.1, 'PHX': 115.1,
    'Atlanta Hawks': 116.3, 'ATL': 116.3,
    'Toronto Raptors': 116.8, 'TOR': 116.8,
    'Sacramento Kings': 117.2, 'SAC': 117.2,
    'Brooklyn Nets': 117.9, 'BKN': 117.9,
    'New Orleans Pelicans': 118.4, 'NOP': 118.4,
    'Detroit Pistons': 118.9, 'DET': 118.9,
    'Utah Jazz': 119.5, 'UTA': 119.5,
    'San Antonio Spurs': 120.1, 'SAS': 120.1,
    'Charlotte Hornets': 120.8, 'CHO': 120.8,
    'Washington Wizards': 122.5, 'WAS': 122.5,
    'Portland Trail Blazers': 121.3, 'POR': 121.3,
}

HOME_COURT_ADVANTAGE = 2.5

print(f"\n{'='*70}")
print(f"NBA SPREADS & TOTALS EDGE FINDER v2.0")
print(f"Started: {datetime.now().strftime('%B %d, %Y at %I:%M %p EST')}")
print(f"{'='*70}\n")

print("[1/4] Loading team data...")
print(f"      [OK] 30 teams loaded with offense/defense stats")

# === FETCH GAMES ===
print(f"\n[2/4] Fetching today's games...")

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
    print(f"      [OK] Found {len(events)} NBA games")

except Exception as e:
    print(f"      [ERROR] {e}")
    exit()

if len(events) == 0:
    print("      [INFO] No games scheduled")
    msg = f"🏀 <b>NBA Spreads & Totals</b>\n\nNo games scheduled.\n\n<i>{datetime.now().strftime('%I:%M %p EST')}</i>"
    send_telegram_message(msg)
    exit()

# === BUILD PROJECTIONS ===
print(f"\n[3/4] Building projections...")

game_projections = []

for event in events:
    away_team = event['away_team']
    home_team = event['home_team']

    away_ppg = TEAM_PPG.get(away_team, 110)
    home_ppg = TEAM_PPG.get(home_team, 110)
    away_def = TEAM_OPP_PPG.get(away_team, 113)
    home_def = TEAM_OPP_PPG.get(home_team, 113)

    away_proj = (away_ppg + home_def) / 2
    home_proj = ((home_ppg + away_def) / 2) + HOME_COURT_ADVANTAGE

    proj_total = away_proj + home_proj
    proj_spread = home_proj - away_proj

    game_projections.append({
        'game': f"{away_team} @ {home_team}",
        'away_team': away_team,
        'home_team': home_team,
        'away_proj': round(away_proj, 1),
        'home_proj': round(home_proj, 1),
        'total_proj': round(proj_total, 1),
        'spread_proj': round(proj_spread, 1)
    })

    print(f"      -> {away_team} @ {home_team}")
    print(f"         Total: {proj_total:.1f} | Spread: {home_team} by {proj_spread:.1f}")

# === FETCH LINES & FIND EDGES ===
print(f"\n[4/4] Fetching lines and finding edges...")

edges = []

for game_proj in game_projections:
    away_team = game_proj['away_team']
    home_team = game_proj['home_team']

    event = next((e for e in events if e['away_team'] == away_team and e['home_team'] == home_team), None)
    if not event:
        continue

    event_id = event['id']

    try:
        odds_response = requests.get(
            f'https://api.the-odds-api.com/v4/sports/basketball_nba/events/{event_id}/odds',
            params={
                'apiKey': API_KEY,
                'regions': 'us',
                'markets': 'spreads,totals',
                'bookmakers': 'fanduel',
                'oddsFormat': 'american'
            },
            timeout=30
        )

        if odds_response.status_code != 200:
            continue

        odds_data = odds_response.json()

        if 'bookmakers' not in odds_data or len(odds_data['bookmakers']) == 0:
            continue

        for bookmaker in odds_data['bookmakers']:
            if bookmaker['key'] != 'fanduel':
                continue

            for market in bookmaker['markets']:
                if market['key'] == 'totals':
                    for outcome in market['outcomes']:
                        if outcome['name'] == 'Over':
                            fd_total = outcome['point']
                            over_odds = outcome['price']
                            edge = game_proj['total_proj'] - fd_total

                            if ONLY_OVERS and edge >= MIN_EDGE and edge <= MAX_EDGE:
                                edges.append({
                                    'TYPE': 'TOTAL',
                                    'GAME': game_proj['game'],
                                    'BET': f"OVER {fd_total}",
                                    'FD_LINE': fd_total,
                                    'PROJECTION': game_proj['total_proj'],
                                    'EDGE': round(edge, 1),
                                    'ODDS': over_odds
                                })

                elif market['key'] == 'spreads':
                    home_line = None
                    away_line = None
                    home_odds = None
                    away_odds = None

                    for outcome in market['outcomes']:
                        if outcome['name'] == home_team:
                            home_line = outcome['point']
                            home_odds = outcome['price']
                        elif outcome['name'] == away_team:
                            away_line = outcome['point']
                            away_odds = outcome['price']

                    if home_line and away_line:
                        if home_line < 0:
                            fd_margin = abs(home_line)
                            proj_margin = game_proj['spread_proj']
                            edge = fd_margin - proj_margin

                            if edge >= MIN_EDGE and edge <= MAX_EDGE:
                                edges.append({
                                    'TYPE': 'SPREAD',
                                    'GAME': game_proj['game'],
                                    'BET': f"{away_team} {away_line:+.1f}",
                                    'FD_LINE': away_line,
                                    'PROJECTION': -proj_margin,
                                    'EDGE': round(edge, 1),
                                    'ODDS': away_odds
                                })

        print(f"      -> {game_proj['game']}: Analyzed")

    except Exception as e:
        print(f"      -> {game_proj['game']}: Error {e}")
        continue

print(f"\n      [OK] Found {len(edges)} edges")

# === SAVE & SEND TO TELEGRAM ===
today = datetime.now().strftime('%Y-%m-%d')
output_file = f'edges_spreads_totals_{today}.csv'

if edges:
    edges_df = pd.DataFrame(edges).sort_values('EDGE', ascending=False)
    edges_df.to_csv(output_file, index=False)
    print(f"      [OK] Saved {len(edges)} edges to {output_file}")

    totals_count = len([e for e in edges if e['TYPE'] == 'TOTAL'])
    spreads_count = len([e for e in edges if e['TYPE'] == 'SPREAD'])

    message = f"📊 <b>NBA SPREADS & TOTALS - {len(edges)} EDGES FOUND</b>\n\n"

    if totals_count > 0:
        message += f"🎯 <b>Totals (OVERS): {totals_count}</b>\n"
        totals = [e for e in edges if e['TYPE'] == 'TOTAL']
        for edge in totals[:3]:
            message += f"  • {edge['GAME']}\n"
            message += f"    {edge['BET']} (+{edge['EDGE']}) @ {edge['ODDS']}\n"
        message += "\n"

    if spreads_count > 0:
        message += f"📈 <b>Spreads: {spreads_count}</b>\n"
        spreads = [e for e in edges if e['TYPE'] == 'SPREAD']
        for edge in spreads[:3]:
            message += f"  • {edge['BET']}\n"
            message += f"    (+{edge['EDGE']}) @ {edge['ODDS']}\n"

    message += f"\n<i>Generated: {datetime.now().strftime('%I:%M %p EST')}</i>"

    send_telegram_message(message)
    send_telegram_file(output_file, f"📎 {len(edges)} edges")
    print(f"      [OK] Sent to Telegram")

else:
    print("      [INFO] No edges found")
    pd.DataFrame(columns=['TYPE', 'GAME', 'BET', 'FD_LINE', 'PROJECTION', 'EDGE', 'ODDS']).to_csv(output_file, index=False)

    message = f"📊 <b>NBA Spreads & Totals</b>\n\nNo edges found (2-6 range).\n\n<i>{datetime.now().strftime('%I:%M %p EST')}</i>"
    send_telegram_message(message)
    print(f"      [OK] Sent to Telegram")

print(f"\n{'='*70}")
print(f"COMPLETE - {datetime.now().strftime('%I:%M %p EST')}")
print(f"Result: {len(edges)} edges found")
print(f"{'='*70}\n")
