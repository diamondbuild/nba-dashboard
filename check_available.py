import requests
import json

API_KEY = 'b380c6cf923b7a0ec7ef2e2b87622d1a'

print("Checking what's actually available...\n")

response = requests.get(
    'https://api.the-odds-api.com/v4/sports/basketball_nba/events',
    params={
        'apiKey': API_KEY,
        'regions': 'us,us2',  # Check both US regions
        'markets': 'player_points',
        'oddsFormat': 'american'
    },
    timeout=30
)

if response.status_code == 200:
    events = response.json()
    print(f"Found {len(events)} games\n")
    
    all_bookmakers = set()
    
    for event in events:
        print(f"\nGame: {event['away_team']} @ {event['home_team']}")
        print(f"Commence: {event['commence_time']}")
        
        if 'bookmakers' in event and len(event['bookmakers']) > 0:
            print(f"Bookmakers with props: {len(event['bookmakers'])}")
            for bookmaker in event['bookmakers']:
                print(f"  - {bookmaker['key']} ({bookmaker['title']})")
                all_bookmakers.add(bookmaker['key'])
        else:
            print("  No bookmakers with props yet")
    
    print("\n" + "="*70)
    print("ALL AVAILABLE BOOKMAKERS:")
    print("="*70)
    for bm in sorted(all_bookmakers):
        print(f"  {bm}")
    
    if len(all_bookmakers) == 0:
        print("\nNO PLAYER PROPS AVAILABLE YET FROM ANY BOOKMAKER")
        print("Player props typically post 2-4 hours before tip-off.")
        print("Try again closer to game time.")
    elif 'fanduel' not in all_bookmakers:
        print("\nFanDuel props not in API feed yet.")
        print("Available bookmakers:", ', '.join(sorted(all_bookmakers)))
        print("\nYou can either:")
        print("1. Wait and try again in 1-2 hours")
        print("2. Use a different bookmaker from the list above")
        print("3. Use the manual CSV approach")
else:
    print(f"Error: {response.status_code}")
    print(response.text)

print(f"\nAPI requests remaining: {response.headers.get('x-requests-remaining', 'unknown')}")
