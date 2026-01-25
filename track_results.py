import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

# TELEGRAM CONFIG
TELEGRAM_BOT_TOKEN = '7575252205:AAGPJO7mZMtFUZ-layIz-O9_eB2-TdyGXpE'
TELEGRAM_CHAT_ID = '-1003840733254'

# FILE PATHS
RESULTS_DB = 'results_history.csv'
TODAY_EDGES_FILE = f'edges_{datetime.now().strftime("%Y-%m-%d")}.csv'

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
        print(f"      [ERROR] Telegram failed: {e}")
        return None

# ============================================================================
# NBA STATS FETCHING
# ============================================================================

def get_yesterdays_games():
    """Fetch yesterday's NBA game results from ESPN"""
    try:
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={yesterday}"

        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"      [ERROR] Could not fetch games: {e}")
        return None

def get_player_stats_from_game(game_id):
    """Fetch player stats for a specific game"""
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={game_id}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            player_stats = {}

            # Parse box score
            if 'boxscore' in data and 'players' in data['boxscore']:
                for team in data['boxscore']['players']:
                    for player in team.get('statistics', [{}])[0].get('athletes', []):
                        name = player.get('athlete', {}).get('displayName', '')
                        stats = player.get('stats', [])

                        # Stats order: MIN, FG, 3PT, FT, OREB, DREB, REB, AST, STL, BLK, TO, PF, PTS
                        if len(stats) >= 13:
                            player_stats[name] = {
                                'PTS': float(stats[12]) if stats[12] != '--' else 0,
                                'REB': float(stats[6]) if stats[6] != '--' else 0,
                                'AST': float(stats[7]) if stats[7] != '--' else 0,
                                'STL': float(stats[8]) if stats[8] != '--' else 0,
                                'BLK': float(stats[9]) if stats[9] != '--' else 0,
                                '3PM': float(stats[2].split('-')[0]) if stats[2] != '--' and '-' in stats[2] else 0
                            }

                            # Calculate PRA
                            player_stats[name]['PRA'] = (
                                player_stats[name]['PTS'] + 
                                player_stats[name]['REB'] + 
                                player_stats[name]['AST']
                            )

            return player_stats
        return {}
    except Exception as e:
        print(f"      [ERROR] Could not fetch player stats: {e}")
        return {}

def get_all_player_stats_yesterday():
    """Get all player stats from yesterday's games"""
    print("\n[1/4] Fetching yesterday's game results...")

    games_data = get_yesterdays_games()
    if not games_data or 'events' not in games_data:
        print("      [ERROR] No games found")
        return {}

    games = games_data['events']
    print(f"      [OK] Found {len(games)} games from yesterday")

    print("\n[2/4] Fetching player stats from each game...")

    all_stats = {}
    for i, game in enumerate(games, 1):
        game_id = game['id']
        away_team = game['competitions'][0]['competitors'][1]['team']['displayName']
        home_team = game['competitions'][0]['competitors'][0]['team']['displayName']

        print(f"      -> Game {i}/{len(games)}: {away_team} @ {home_team}")

        game_stats = get_player_stats_from_game(game_id)
        all_stats.update(game_stats)

        time.sleep(0.5)  # Be nice to ESPN servers

    print(f"\n      [OK] Collected stats for {len(all_stats)} players")
    return all_stats

# ============================================================================
# RESULTS TRACKING
# ============================================================================

def load_yesterdays_bets():
    """Load yesterday's edge picks"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    edges_file = f'edges_{yesterday}.csv'

    if not os.path.exists(edges_file):
        print(f"      [ERROR] Could not find {edges_file}")
        return None

    try:
        df = pd.read_csv(edges_file)
        print(f"      [OK] Loaded {len(df)} bets from {edges_file}")
        return df
    except Exception as e:
        print(f"      [ERROR] Could not read file: {e}")
        return None

def check_bet_results(bets_df, player_stats):
    """Compare bets against actual results"""
    print("\n[3/4] Checking bet results...")

    results = []

    for _, bet in bets_df.iterrows():
        player_name = bet['PLAYER']
        stat_type = bet['STAT']
        line = bet['FD_LINE']
        projection = bet['PROJECTION']
        edge = bet['EDGE']
        bet_type = bet['BET']  # Should be 'OVER'
        odds = bet['ODDS']

        # Try to find player in stats (handle name variations)
        actual_stat = None
        matched_name = None

        for stats_name, stats in player_stats.items():
            if player_name.lower() in stats_name.lower() or stats_name.lower() in player_name.lower():
                if stat_type in stats:
                    actual_stat = stats[stat_type]
                    matched_name = stats_name
                    break

        if actual_stat is None:
            result = 'VOID'
            margin = 0
            print(f"      -> {player_name} {stat_type}: NO DATA (game postponed or DNP)")
        else:
            if bet_type == 'OVER':
                if actual_stat > line:
                    result = 'WIN'
                    margin = actual_stat - line
                else:
                    result = 'LOSS'
                    margin = actual_stat - line  # Negative
            else:  # UNDER
                if actual_stat < line:
                    result = 'WIN'
                    margin = line - actual_stat
                else:
                    result = 'LOSS'
                    margin = line - actual_stat  # Negative

            status_icon = '✅' if result == 'WIN' else '❌'
            print(f"      -> {player_name} {stat_type} {bet_type} {line}: {actual_stat} {status_icon} ({margin:+.1f})")

        results.append({
            'DATE': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'PLAYER': player_name,
            'STAT': stat_type,
            'BET_TYPE': bet_type,
            'LINE': line,
            'PROJECTION': projection,
            'EDGE': edge,
            'ODDS': odds,
            'ACTUAL': actual_stat if actual_stat is not None else 'N/A',
            'RESULT': result,
            'MARGIN': round(margin, 1) if actual_stat is not None else 0
        })

    return pd.DataFrame(results)

def update_results_database(results_df):
    """Append results to historical database"""
    print("\n[4/4] Updating results database...")

    if os.path.exists(RESULTS_DB):
        history_df = pd.read_csv(RESULTS_DB)
        updated_df = pd.concat([history_df, results_df], ignore_index=True)
    else:
        updated_df = results_df
        print("      [INFO] Creating new results database")

    updated_df.to_csv(RESULTS_DB, index=False)
    print(f"      [OK] Saved to {RESULTS_DB} ({len(updated_df)} total records)")

    return updated_df

def generate_summary(results_df, history_df):
    """Generate summary statistics"""

    # Yesterday's results (excluding voids)
    valid_results = results_df[results_df['RESULT'] != 'VOID']
    wins = len(valid_results[valid_results['RESULT'] == 'WIN'])
    losses = len(valid_results[valid_results['RESULT'] == 'LOSS'])
    voids = len(results_df[results_df['RESULT'] == 'VOID'])

    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

    # All-time stats
    all_valid = history_df[history_df['RESULT'] != 'VOID']
    total_wins = len(all_valid[all_valid['RESULT'] == 'WIN'])
    total_losses = len(all_valid[all_valid['RESULT'] == 'LOSS'])
    total_bets = total_wins + total_losses

    overall_win_rate = (total_wins / total_bets * 100) if total_bets > 0 else 0

    # Best/worst performers
    if len(valid_results) > 0:
        best_bet = valid_results.loc[valid_results['MARGIN'].idxmax()] if wins > 0 else None
        worst_bet = valid_results.loc[valid_results['MARGIN'].idxmin()] if losses > 0 else None
    else:
        best_bet = None
        worst_bet = None

    # Stats by category - FIXED
    stats_breakdown = {}
    if len(all_valid) > 0:
        for stat in all_valid['STAT'].unique():
            stat_data = all_valid[all_valid['STAT'] == stat]
            stat_wins = len(stat_data[stat_data['RESULT'] == 'WIN'])
            stat_total = len(stat_data)
            stat_rate = (stat_wins / stat_total * 100) if stat_total > 0 else 0
            stats_breakdown[stat] = stat_rate

    return {
        'yesterday': {
            'wins': wins,
            'losses': losses,
            'voids': voids,
            'win_rate': win_rate,
            'best_bet': best_bet,
            'worst_bet': worst_bet
        },
        'all_time': {
            'wins': total_wins,
            'losses': total_losses,
            'total_bets': total_bets,
            'win_rate': overall_win_rate,
            'stats_breakdown': stats_breakdown
        }
    }

def send_results_summary(summary):
    """Send results summary to Telegram"""

    y = summary['yesterday']
    a = summary['all_time']

    message = f"📊 <b>YESTERDAY'S RESULTS</b>\n\n"
    message += f"<b>Record:</b> {y['wins']}-{y['losses']}"
    if y['voids'] > 0:
        message += f" ({y['voids']} void)"
    message += f"\n<b>Win Rate:</b> {y['win_rate']:.1f}%\n"

    if y['best_bet'] is not None:
        b = y['best_bet']
        message += f"\n🏆 <b>Best Hit:</b>\n"
        message += f"  {b['PLAYER']} {b['STAT']} {b['BET_TYPE']} {b['LINE']}\n"
        message += f"  Actual: {b['ACTUAL']} ({b['MARGIN']:+.1f})\n"

    if y['worst_bet'] is not None:
        w = y['worst_bet']
        message += f"\n💀 <b>Worst Miss:</b>\n"
        message += f"  {w['PLAYER']} {w['STAT']} {w['BET_TYPE']} {w['LINE']}\n"
        message += f"  Actual: {w['ACTUAL']} ({w['MARGIN']:+.1f})\n"

    message += f"\n━━━━━━━━━━━━━━━━━━━\n"
    message += f"📈 <b>ALL-TIME STATS</b>\n\n"
    message += f"<b>Total Bets:</b> {a['total_bets']}\n"
    message += f"<b>Record:</b> {a['wins']}-{a['losses']}\n"
    message += f"<b>Win Rate:</b> {a['win_rate']:.1f}%\n"

    if len(a['stats_breakdown']) > 0:
        message += f"\n<b>By Stat Type:</b>\n"
        for stat, rate in a['stats_breakdown'].items():
            message += f"  • {stat}: {rate:.1f}%\n"

    message += f"\n<i>Updated: {datetime.now().strftime('%I:%M %p EST')}</i>"

    send_telegram_message(message)

# ============================================================================
# MAIN SCRIPT
# ============================================================================

print(f"\n{'='*70}")
print(f"NBA BET RESULTS TRACKER")
print(f"Tracking: {(datetime.now() - timedelta(days=1)).strftime('%B %d, %Y')}")
print(f"{'='*70}\n")

# Load yesterday's bets
print("[STEP 1] Loading yesterday's bet picks...")
bets_df = load_yesterdays_bets()

if bets_df is None or len(bets_df) == 0:
    print("\n[EXIT] No bets to track")
    exit()

# Fetch actual stats
player_stats = get_all_player_stats_yesterday()

if len(player_stats) == 0:
    print("\n[ERROR] Could not fetch player stats")
    exit()

# Check results
results_df = check_bet_results(bets_df, player_stats)

# Update database
history_df = update_results_database(results_df)

# Generate summary
summary = generate_summary(results_df, history_df)

# Send to Telegram
print("\n[5/5] Sending results to Telegram...")
send_results_summary(summary)
print("      [OK] Results sent")

# Display summary
print(f"\n{'='*70}")
print(f"SUMMARY")
print(f"{'='*70}")
print(f"Yesterday: {summary['yesterday']['wins']}-{summary['yesterday']['losses']} ({summary['yesterday']['win_rate']:.1f}%)")
print(f"All-Time: {summary['all_time']['wins']}-{summary['all_time']['losses']} ({summary['all_time']['win_rate']:.1f}%)")
print(f"{'='*70}\n")
