import requests
from datetime import datetime, timedelta

def get_yesterdays_games():
    """Fetch yesterday's NBA game results from ESPN"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={yesterday}"
    response = requests.get(url, timeout=10)
    return response.json() if response.status_code == 200 else None

def get_player_stats_from_game(game_id):
    """Fetch player stats for a specific game"""
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={game_id}"
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        data = response.json()
        player_stats = {}

        if 'boxscore' in data and 'players' in data['boxscore']:
            for team in data['boxscore']['players']:
                for player in team.get('statistics', [{}])[0].get('athletes', []):
                    name = player.get('athlete', {}).get('displayName', '')
                    stats = player.get('stats', [])

                    # DEBUG: Print raw stats for Kawhi Leonard
                    if 'Kawhi' in name or 'Leonard' in name:
                        print(f"\n🔍 DEBUG: Found {name}")
                        print(f"   Raw stats array: {stats}")
                        print(f"   Array length: {len(stats)}")

                    if len(stats) >= 13:
                        pts = float(stats[12]) if stats[12] != '--' else 0
                        reb = float(stats[6]) if stats[6] != '--' else 0
                        ast = float(stats[7]) if stats[7] != '--' else 0

                        player_stats[name] = {
                            'PTS': pts,
                            'REB': reb,
                            'AST': ast,
                            'PRA': pts + reb + ast
                        }

                        # DEBUG: Print calculated stats for Kawhi
                        if 'Kawhi' in name or 'Leonard' in name:
                            print(f"   Calculated:")
                            print(f"   - PTS: {pts} (index 12)")
                            print(f"   - REB: {reb} (index 6)")
                            print(f"   - AST: {ast} (index 7)")
                            print(f"   - PRA: {pts + reb + ast}")

        return player_stats
    return {}

# Run debug
print("🔍 DEBUGGING ESPN API - Looking for Kawhi Leonard stats\n")
print("="*70)

games_data = get_yesterdays_games()
if games_data and 'events' in games_data:
    for game in games_data['events']:
        game_id = game['id']
        away = game['competitions'][0]['competitors'][1]['team']['displayName']
        home = game['competitions'][0]['competitors'][0]['team']['displayName']

        print(f"\nGame: {away} @ {home}")

        stats = get_player_stats_from_game(game_id)

        # Show all Clippers players (Kawhi's team)
        if 'Clippers' in away or 'Clippers' in home:
            print(f"\n📊 ALL CLIPPERS PLAYERS:")
            for player_name, player_stats in stats.items():
                if 'Clippers' in away or 'Clippers' in home:
                    print(f"  {player_name}: PTS={player_stats.get('PTS', 0)}, REB={player_stats.get('REB', 0)}, AST={player_stats.get('AST', 0)}, PRA={player_stats.get('PRA', 0)}")

print("\n" + "="*70)
