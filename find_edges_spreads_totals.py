import requests
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import sys

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = 'b380c6cf923b7a0ec7ef2e2b87622d1a'
SENDER_EMAIL = 'joey19154@gmail.com'
SENDER_PASSWORD = 'qchyceomnnqujkkr'
RECIPIENT_EMAIL = 'joey19154@gmail.com'

MIN_EDGE = 2.0
MAX_EDGE = 6.0
ONLY_OVERS = True

# ============================================================================
# TEAM SEASON AVERAGES (2025-26 Season - Points Per Game)
# ============================================================================

TEAM_PPG = {
    # Eastern Conference
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

    # Western Conference
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

# Opponent Points Allowed Per Game (Defense)
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

# Home court advantage (points)
HOME_COURT_ADVANTAGE = 2.5

# Pace adjustments (possessions per game)
TEAM_PACE = {
    'Sacramento Kings': 102.5, 'SAC': 102.5,
    'Indiana Pacers': 101.8, 'IND': 101.8,
    'Atlanta Hawks': 101.2, 'ATL': 101.2,
    'Boston Celtics': 100.5, 'BOS': 100.5,
    'Minnesota Timberwolves': 99.8, 'MIN': 99.8,
    'Phoenix Suns': 99.5, 'PHX': 99.5,
    'Golden State Warriors': 99.2, 'GSW': 99.2,
    'Los Angeles Lakers': 98.9, 'LAL': 98.9,
    'Cleveland Cavaliers': 98.5, 'CLE': 98.5,
    'Milwaukee Bucks': 98.2, 'MIL': 98.2,
    'Denver Nuggets': 98.0, 'DEN': 98.0,
    'Dallas Mavericks': 97.8, 'DAL': 97.8,
    'Miami Heat': 97.5, 'MIA': 97.5,
    'Memphis Grizzlies': 97.0, 'MEM': 97.0,
    'Philadelphia 76ers': 96.8, 'PHI': 96.8,
    'Oklahoma City Thunder': 96.5, 'OKC': 96.5,
    'LA Clippers': 96.2, 'LAC': 96.2,
    'Los Angeles Clippers': 96.2,
    'New York Knicks': 96.0, 'NYK': 96.0,
    'Chicago Bulls': 95.8, 'CHI': 95.8,
    'Orlando Magic': 95.2, 'ORL': 95.2,
    'Houston Rockets': 95.0, 'HOU': 95.0,
    'Toronto Raptors': 94.8, 'TOR': 94.8,
    'Brooklyn Nets': 94.5, 'BKN': 94.5,
    'Washington Wizards': 94.2, 'WAS': 94.2,
    'Detroit Pistons': 94.0, 'DET': 94.0,
    'Charlotte Hornets': 93.8, 'CHO': 93.8,
    'San Antonio Spurs': 93.5, 'SAS': 93.5,
    'Utah Jazz': 93.2, 'UTA': 93.2,
    'New Orleans Pelicans': 97.2, 'NOP': 97.2,
    'Portland Trail Blazers': 95.5, 'POR': 95.5,
}

print(f"\n{'='*70}")
print(f"NBA SPREADS & TOTALS EDGE FINDER v2.0")
print(f"Started: {datetime.now().strftime('%B %d, %Y at %I:%M %p EST')}")
print(f"{'='*70}\n")

print("[1/5] Loading team data...")
print(f"      [OK] {len(set([k for k in TEAM_PPG.keys() if len(k) > 3]))} teams loaded")
print(f"      [OK] Offense, defense, pace, home court factors ready")

# === STEP 2: GET INJURY DATA ===
print("\n[2/5] Fetching injury data...")

injuries = {}
try:
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        data = response.json()
        if 'events' in data:
            for event in data['events']:
                for competition in event.get('competitions', []):
                    for competitor in competition.get('competitors', []):
                        team = competitor.get('team', {}).get('displayName', '')
                        if 'injuries' in competitor:
                            key_injuries = []
                            for injury in competitor['injuries']:
                                player = injury.get('athlete', {}).get('displayName', '')
                                status = injury.get('status', '')
                                if status == 'Out':
                                    key_injuries.append(player)
                            if key_injuries:
                                injuries[team] = key_injuries

        print(f"      [OK] Found {len(injuries)} teams with key injuries")
        for team, players in injuries.items():
            print(f"           {team}: {', '.join(players)}")
    else:
        print(f"      [INFO] Could not fetch injuries")
except Exception as e:
    print(f"      [INFO] Injury fetch failed: {e}")

# === STEP 3: FETCH TODAY'S GAMES ===
print(f"\n[3/5] Fetching today's games...")

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
    exit()

# === STEP 4: BUILD PROJECTIONS WITH CONTEXT ===
print(f"\n[4/5] Building context-adjusted projections...")

game_projections = []

for event in events:
    away_team = event['away_team']
    home_team = event['home_team']

    # Get base stats
    away_ppg = TEAM_PPG.get(away_team, 110)
    home_ppg = TEAM_PPG.get(home_team, 110)

    away_def = TEAM_OPP_PPG.get(away_team, 113)
    home_def = TEAM_OPP_PPG.get(home_team, 113)

    away_pace = TEAM_PACE.get(away_team, 97)
    home_pace = TEAM_PACE.get(home_team, 97)

    # Calculate projected scores
    # Away team projection = (their offense + home team defense) / 2, adjusted for pace
    avg_pace = 97.5
    game_pace = (away_pace + home_pace) / 2
    pace_factor = game_pace / avg_pace

    # Project away team score
    away_proj_base = (away_ppg + home_def) / 2
    away_proj = away_proj_base * pace_factor

    # Project home team score (with home court advantage)
    home_proj_base = (home_ppg + away_def) / 2
    home_proj = (home_proj_base * pace_factor) + HOME_COURT_ADVANTAGE

    # Injury adjustments
    injury_notes = []
    if away_team in injuries:
        away_proj *= 0.95  # 5% reduction for key injuries
        injury_notes.append(f"{away_team}: {', '.join(injuries[away_team])} OUT")

    if home_team in injuries:
        home_proj *= 0.95
        injury_notes.append(f"{home_team}: {', '.join(injuries[home_team])} OUT")

    # Calculate totals and spread
    proj_total = away_proj + home_proj
    proj_spread = home_proj - away_proj  # Positive = home favored

    game_projections.append({
        'game': f"{away_team} @ {home_team}",
        'away_team': away_team,
        'home_team': home_team,
        'away_proj': round(away_proj, 1),
        'home_proj': round(home_proj, 1),
        'total_proj': round(proj_total, 1),
        'spread_proj': round(proj_spread, 1),
        'pace_factor': round(pace_factor, 3),
        'injuries': injury_notes
    })

    print(f"      -> {away_team} @ {home_team}")
    print(f"         Projected: {away_team} {away_proj:.1f}, {home_team} {home_proj:.1f}")
    print(f"         Total: {proj_total:.1f} | Spread: {home_team} by {proj_spread:.1f}")
    if injury_notes:
        for note in injury_notes:
            print(f"         Injuries: {note}")

# === STEP 5: FETCH FD LINES & FIND EDGES ===
print(f"\n[5/5] Fetching FanDuel lines and finding edges...")

edges = []

for game_proj in game_projections:
    away_team = game_proj['away_team']
    home_team = game_proj['home_team']

    # Find event
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
                # TOTALS
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
                                    'ODDS': over_odds,
                                    'DETAIL': f"{away_team} {game_proj['away_proj']} + {home_team} {game_proj['home_proj']}"
                                })

                # SPREADS
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
                        # Home is favorite (negative line)
                        if home_line < 0:
                            fd_margin = abs(home_line)
                            proj_margin = game_proj['spread_proj']
                            edge = fd_margin - proj_margin

                            # If edge > 2, bet the dog (away)
                            if edge >= MIN_EDGE and edge <= MAX_EDGE:
                                edges.append({
                                    'TYPE': 'SPREAD',
                                    'GAME': game_proj['game'],
                                    'BET': f"{away_team} {away_line:+.1f}",
                                    'FD_LINE': away_line,
                                    'PROJECTION': -proj_margin,
                                    'EDGE': round(edge, 1),
                                    'ODDS': away_odds,
                                    'DETAIL': f"FD: {home_team} by {fd_margin:.1f}, Proj: {home_team} by {proj_margin:.1f}"
                                })

                        # Away is favorite (positive home line)
                        else:
                            fd_margin = home_line  # Home is dog by this much
                            proj_margin = game_proj['spread_proj']  # Positive = home favored

                            # If home is projected to win but is dog, edge exists
                            if proj_margin > 0:
                                edge = fd_margin + proj_margin
                                if edge >= MIN_EDGE and edge <= MAX_EDGE:
                                    edges.append({
                                        'TYPE': 'SPREAD',
                                        'GAME': game_proj['game'],
                                        'BET': f"{home_team} {home_line:+.1f}",
                                        'FD_LINE': home_line,
                                        'PROJECTION': proj_margin,
                                        'EDGE': round(edge, 1),
                                        'ODDS': home_odds,
                                        'DETAIL': f"FD: {away_team} favored, Proj: {home_team} by {proj_margin:.1f}"
                                    })

        print(f"      -> {game_proj['game']}: Lines analyzed")

    except Exception as e:
        print(f"      -> {game_proj['game']}: Error {e}")
        continue

print(f"\n      [OK] Found {len(edges)} edges")
print(f"           Totals (OVERS): {len([e for e in edges if e['TYPE'] == 'TOTAL'])}")
print(f"           Spreads: {len([e for e in edges if e['TYPE'] == 'SPREAD'])}")

# === STEP 6: SAVE & EMAIL ===
print(f"\n[6/6] Saving results...")

today = datetime.now().strftime('%Y-%m-%d')
output_file = f'edges_spreads_totals_{today}.csv'

if edges:
    edges_df = pd.DataFrame(edges).sort_values('EDGE', ascending=False)
    edges_df.to_csv(output_file, index=False)
    print(f"      [OK] Saved {len(edges)} edges to {output_file}")

    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>NBA Spreads & Totals: {len(edges)} Edges Found</h2>

        <div style="background-color: #27ae60; color: white; padding: 15px; border-radius: 5px;">
            <h3 style="margin: 0;">Context-Adjusted Projections</h3>
            <p style="margin: 5px 0;">Includes: Pace, Defense, Home Court, Injuries</p>
        </div>

        <h3>Edges:</h3>
        {edges_df.to_html(index=False, border=1)}

        <p style="color: #7f8c8d; margin-top: 30px;">
            <small>Generated: {datetime.now().strftime('%I:%M %p EST')}</small>
        </p>
    </body>
    </html>
    """

    subject = f"NBA Spreads/Totals: {len(edges)} Edges - {datetime.now().strftime('%b %d')}"

else:
    print("      [INFO] No edges found within 2-6 range")
    pd.DataFrame(columns=['TYPE', 'GAME', 'BET', 'FD_LINE', 'PROJECTION', 'EDGE', 'ODDS', 'DETAIL']).to_csv(output_file, index=False)

    email_body = "<html><body><h2>No edges found today</h2></body></html>"
    subject = f"NBA: No Edges - {datetime.now().strftime('%b %d')}"

# Send email
try:
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(email_body, 'html'))

    if os.path.exists(output_file):
        with open(output_file, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={output_file}')
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.send_message(msg)
    server.quit()
    print(f"      [OK] Email sent")
except Exception as e:
    print(f"      [INFO] Email not sent: {e}")

print(f"\n{'='*70}")
print(f"COMPLETE - {datetime.now().strftime('%I:%M %p EST')}")
print(f"Result: {len(edges)} edges found")
print(f"{'='*70}\n")
