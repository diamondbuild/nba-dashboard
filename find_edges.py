import requests
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# The Odds API Key
API_KEY = 'b380c6cf923b7a0ec7ef2e2b87622d1a'

# Email Settings
SENDER_EMAIL = 'joey19154@gmail.com'           # Your Gmail address
SENDER_PASSWORD = 'vkdamnqnrpmwdxwy'        # Your 16-character App Password from Google
RECIPIENT_EMAIL = 'joey19154@gmail.com'        # Where to send results (can be same or different email)

# ============================================================================
# SCRIPT START
# ============================================================================

print(f"\n{'='*70}")
print(f"NBA PLAYER PROPS EDGE FINDER")
print(f"Started: {datetime.now().strftime('%B %d, %Y at %I:%M %p EST')}")
print(f"{'='*70}\n")

# === STEP 1: FETCH NBA GAME IDs ===
print("[1/5] Fetching today's NBA games...")

try:
    response = requests.get(
        'https://api.the-odds-api.com/v4/sports/basketball_nba/events',
        params={'apiKey': API_KEY},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"      ✗ API Error: {response.status_code}")
        print(f"      Response: {response.text}")
        exit()
    
    events = response.json()
    print(f"      ✓ Found {len(events)} NBA games scheduled")
    
    # Check API usage
    requests_remaining = response.headers.get('x-requests-remaining', 'unknown')
    print(f"      ✓ API requests remaining: {requests_remaining}")
    
except Exception as e:
    print(f"      ✗ Error fetching data: {e}")
    exit()

if len(events) == 0:
    print("      ✗ No NBA games scheduled today")
    exit()

# === STEP 2: FETCH PLAYER PROPS FOR EACH GAME ===
print(f"\n[2/5] Fetching player props from FanDuel for {len(events)} games...")

player_props = []
props_found_count = 0

for i, event in enumerate(events, 1):
    event_id = event['id']
    home_team = event['home_team']
    away_team = event['away_team']
    
    print(f"      → Game {i}/{len(events)}: {away_team} @ {home_team}")
    
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
            print(f"         ✗ Error fetching props: {props_response.status_code}")
            continue
        
        event_data = props_response.json()
        
        # Parse bookmakers and markets
        if 'bookmakers' not in event_data or len(event_data['bookmakers']) == 0:
            print(f"         → No props available yet")
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
                        continue  # Skip the "Over" label, we want player names
                    
                    player_props.append({
                        'PLAYER': outcome['description'],
                        'STAT': stat_type,
                        'FD_LINE': outcome['point'],
                        'OVER_ODDS': outcome.get('price', -110)
                    })
                    game_props += 1
        
        if game_props > 0:
            print(f"         ✓ Found {game_props} props")
            props_found_count += game_props
        else:
            print(f"         → No props available yet")
    
    except Exception as e:
        print(f"         ✗ Error: {e}")
        continue

print(f"\n      ✓ Total props collected: {props_found_count}")

if len(player_props) == 0:
    print("      ✗ No FanDuel props available yet")
    print("      → Props typically post 2-4 hours before tip-off")
    print("      → Try running again closer to game time")
    exit()

# Remove duplicates
fd_df = pd.DataFrame(player_props).drop_duplicates(subset=['PLAYER', 'STAT', 'FD_LINE'])
print(f"      ✓ Parsed {len(fd_df)} unique player props")
print(f"      ✓ Covering {fd_df['PLAYER'].nunique()} players")

# === STEP 3: LOAD YOUR PROJECTIONS ===
print("\n[3/5] Loading your projections...")

try:
    proj_df = pd.read_csv('player_projections.csv')
    print(f"      ✓ Loaded projections for {len(proj_df)} players")
except FileNotFoundError:
    print("      ✗ Error: player_projections.csv not found")
    print("      → Make sure you ran project_props.py first")
    exit()

# === STEP 4: FIND EDGES ===
print("\n[4/5] Comparing projections to FanDuel lines...")

edges = []

for stat in ['PTS', 'REB', 'AST', '3PM', 'PRA', 'STL', 'BLK']:
    stat_lines = fd_df[fd_df['STAT'] == stat].copy()
    if len(stat_lines) == 0:
        continue
    
    proj_col = f'PROJ_{stat}'
    if proj_col not in proj_df.columns:
        continue
    
    merged = stat_lines.merge(proj_df[['PLAYER', proj_col]], on='PLAYER', how='inner')
    
    print(f"      → Checking {len(merged)} {stat} props")
    
    for _, row in merged.iterrows():
        projection = row[proj_col]
        fd_line = row['FD_LINE']
        edge = projection - fd_line
        
        # Set threshold based on stat type
        if stat == 'PRA':
            threshold = 3.0
        elif stat == 'PTS':
            threshold = 2.0
        else:
            threshold = 1.5
        
        if abs(edge) >= threshold:
            edges.append({
                'PLAYER': row['PLAYER'],
                'STAT': stat,
                'FD_LINE': fd_line,
                'PROJECTION': round(projection, 1),
                'EDGE': round(edge, 1),
                'BET': 'OVER' if edge > 0 else 'UNDER',
                'ODDS': row['OVER_ODDS']
            })

print(f"      ✓ Analysis complete")

# === STEP 5: SAVE & EMAIL RESULTS ===
print("\n[5/5] Preparing results...")

today = datetime.now().strftime('%Y-%m-%d')
output_file = f'edges_{today}.csv'

if edges:
    edges_df = pd.DataFrame(edges).sort_values('EDGE', key=abs, ascending=False)
    edges_df.to_csv(output_file, index=False)
    
    print(f"      ✓ Found {len(edges_df)} betting edges")
    print(f"      ✓ Saved to {output_file}")
    
    # Prepare email body
    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #2c3e50;">🏀 NBA Player Prop Edges - {datetime.now().strftime('%B %d, %Y')}</h2>
        
        <div style="background-color: #27ae60; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin: 0;">✓ Found {len(edges_df)} Betting Edges</h3>
        </div>
        
        <h3>Summary:</h3>
        <ul>
            <li><strong>OVER bets:</strong> {len(edges_df[edges_df['BET'] == 'OVER'])}</li>
            <li><strong>UNDER bets:</strong> {len(edges_df[edges_df['BET'] == 'UNDER'])}</li>
            <li><strong>Average edge:</strong> {edges_df['EDGE'].abs().mean():.1f} points</li>
            <li><strong>Largest edge:</strong> {edges_df['EDGE'].abs().max():.1f} points ({edges_df.iloc[0]['PLAYER']} {edges_df.iloc[0]['STAT']})</li>
        </ul>
        
        <h3>Top 10 Biggest Edges:</h3>
        {edges_df.head(10).to_html(index=False, border=1, justify='left')}
        
        <p style="color: #7f8c8d; margin-top: 30px;">
            <em>Full results attached as CSV spreadsheet.</em><br>
            <small>Generated at {datetime.now().strftime('%I:%M %p EST on %B %d, %Y')}</small>
        </p>
    </body>
    </html>
    """
    
    email_subject = f"🏀 NBA Props: {len(edges)} Edges Found - {datetime.now().strftime('%b %d')}"
    
else:
    print("      → No edges found (projections within threshold)")
    
    # Create empty CSV
    pd.DataFrame(columns=['PLAYER', 'STAT', 'FD_LINE', 'PROJECTION', 'EDGE', 'BET', 'ODDS']).to_csv(output_file, index=False)
    
    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #2c3e50;">🏀 NBA Player Prop Edges - {datetime.now().strftime('%B %d, %Y')}</h2>
        
        <div style="background-color: #f39c12; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin: 0;">No Edges Found Today</h3>
        </div>
        
        <p>Your projections are within the edge threshold for all FanDuel lines.</p>
        
        <ul>
            <li><strong>Props checked:</strong> {len(fd_df)}</li>
            <li><strong>Players analyzed:</strong> {fd_df['PLAYER'].nunique()}</li>
            <li><strong>Games covered:</strong> {len(events)}</li>
        </ul>
        
        <p style="color: #7f8c8d;">This is normal - edges are rare. Check back tomorrow!</p>
        
        <p style="color: #7f8c8d; margin-top: 30px;">
            <small>Generated at {datetime.now().strftime('%I:%M %p EST on %B %d, %Y')}</small>
        </p>
    </body>
    </html>
    """
    
    email_subject = f"🏀 NBA Props: No Edges - {datetime.now().strftime('%b %d')}"

# === SEND EMAIL ===
print("\n      Sending email...")

msg = MIMEMultipart()
msg['From'] = SENDER_EMAIL
msg['To'] = RECIPIENT_EMAIL
msg['Subject'] = email_subject

msg.attach(MIMEText(email_body, 'html'))

# Attach CSV file
if os.path.exists(output_file):
    with open(output_file, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={output_file}')
    msg.attach(part)

# Send via Gmail SMTP
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.send_message(msg)
    server.quit()
    print(f"      ✓ Email sent successfully to {RECIPIENT_EMAIL}")
except Exception as e:
    print(f"      ✗ Failed to send email: {e}")
    print(f"      → Check your email settings and App Password")

# === FINAL SUMMARY ===
print(f"\n{'='*70}")
print(f"COMPLETE")
print(f"Finished: {datetime.now().strftime('%I:%M %p EST')}")
if edges:
    print(f"Result: {len(edges)} edges found and emailed")
else:
    print(f"Result: No edges found today")
print(f"{'='*70}\n")
