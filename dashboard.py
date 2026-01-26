import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import pytz

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="NBA Edge Finder Dashboard",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .win {
        color: #00cc00;
        font-weight: bold;
    }
    .loss {
        color: #ff3333;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTO TEAM LOOKUP
# ============================================================================

@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_nba_player_teams():
    """Fetch current NBA rosters from ESPN API"""
    team_map = {}

    try:
        # Fetch all NBA teams
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if 'sports' in data and len(data['sports']) > 0:
                teams = data['sports'][0]['leagues'][0]['teams']

                for team_data in teams:
                    team = team_data['team']
                    team_abbr = team.get('abbreviation', '')

                    # Get roster for this team
                    team_id = team.get('id', '')
                    roster_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/roster"

                    try:
                        roster_response = requests.get(roster_url, timeout=5)
                        if roster_response.status_code == 200:
                            roster_data = roster_response.json()

                            # Parse athletes
                            if 'athletes' in roster_data:
                                for athlete in roster_data['athletes']:
                                    player_name = athlete.get('displayName', '')
                                    if player_name:
                                        team_map[player_name] = team_abbr
                    except:
                        continue
    except:
        pass

    return team_map

def get_team(player_name, team_map):
    """Get team abbreviation for a player"""
    # Direct match
    if player_name in team_map:
        return team_map[player_name]

    # Fuzzy match - check if player name is contained in any key
    for roster_name, team in team_map.items():
        if player_name.lower() in roster_name.lower() or roster_name.lower() in player_name.lower():
            return team

    return 'N/A'

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_data(ttl=300)
def load_results_data():
    """Load historical results from GitHub"""
    url = 'https://raw.githubusercontent.com/diamondbuild/nba-dashboard/main/results_history.csv'
    try:
        df = pd.read_csv(url)
        df['DATE'] = pd.to_datetime(df['DATE'])
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_todays_edges():
    """Load today's edge picks from GitHub"""
    eastern = pytz.timezone('US/Eastern')
    today = datetime.now(eastern).strftime('%Y-%m-%d')
    url = f'https://raw.githubusercontent.com/diamondbuild/nba-dashboard/main/edges_{today}.csv'
    try:
        df = pd.read_csv(url)
        return df
    except:
        return pd.DataFrame()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_metrics(df):
    """Calculate overall metrics"""
    if len(df) == 0:
        return {
            'total_bets': 0,
            'wins': 0,
            'losses': 0,
            'voids': 0,
            'win_rate': 0,
            'avg_margin_win': 0,
            'avg_margin_loss': 0
        }

    valid_df = df[df['RESULT'] != 'VOID']
    wins = len(valid_df[valid_df['RESULT'] == 'WIN'])
    losses = len(valid_df[valid_df['RESULT'] == 'LOSS'])
    voids = len(df[df['RESULT'] == 'VOID'])

    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

    win_margins = valid_df[valid_df['RESULT'] == 'WIN']['MARGIN']
    loss_margins = valid_df[valid_df['RESULT'] == 'LOSS']['MARGIN']

    avg_margin_win = win_margins.mean() if len(win_margins) > 0 else 0
    avg_margin_loss = loss_margins.mean() if len(loss_margins) > 0 else 0

    return {
        'total_bets': len(valid_df),
        'wins': wins,
        'losses': losses,
        'voids': voids,
        'win_rate': win_rate,
        'avg_margin_win': avg_margin_win,
        'avg_margin_loss': avg_margin_loss
    }

def calculate_edge_breakdown(df):
    """Calculate win rate by edge range"""
    if len(df) == 0:
        return pd.DataFrame()

    valid_df = df[df['RESULT'] != 'VOID'].copy()

    # Define edge buckets
    valid_df['EDGE_BUCKET'] = pd.cut(valid_df['EDGE'], 
                                     bins=[0, 2.5, 3.5, 4.5, 100],
                                     labels=['2.0-2.5', '2.5-3.5', '3.5-4.5', '4.5+'])

    # Calculate stats by bucket
    breakdown = []
    for bucket in ['2.0-2.5', '2.5-3.5', '3.5-4.5', '4.5+']:
        bucket_df = valid_df[valid_df['EDGE_BUCKET'] == bucket]
        if len(bucket_df) > 0:
            wins = (bucket_df['RESULT'] == 'WIN').sum()
            losses = (bucket_df['RESULT'] == 'LOSS').sum()
            total = wins + losses
            win_rate = (wins / total * 100) if total > 0 else 0
            breakdown.append({
                'Edge': bucket,
                'Record': f"{wins}-{losses}",
                'Win%': f"{win_rate:.1f}%"
            })

    return pd.DataFrame(breakdown)

# ============================================================================
# MAIN APP
# ============================================================================

# Header
st.markdown('<div class="main-header">🏀 NBA EDGE FINDER DASHBOARD</div>', unsafe_allow_html=True)

# Fetch team data (cached for 24 hours)
with st.spinner('Loading NBA rosters...'):
    team_map = fetch_nba_player_teams()

# Load data
results_df = load_results_data()
todays_edges = load_todays_edges()

# Add team column to today's edges
if len(todays_edges) > 0:
    todays_edges['TEAM'] = todays_edges['PLAYER'].apply(lambda x: get_team(x, team_map))

# ============================================================================
# SIDEBAR - FILTERS
# ============================================================================

st.sidebar.header("📊 Filters")

# Stat type filter for TODAY'S picks
if len(todays_edges) > 0:
    stat_types_today = ['All'] + sorted(todays_edges['STAT'].unique().tolist())
    selected_stat_today = st.sidebar.selectbox("Stat Type", stat_types_today)

    # Edge size filter for TODAY'S picks
    edge_min_today = st.sidebar.slider("Minimum Edge", 0.0, 10.0, 0.0, 0.5)
else:
    selected_stat_today = 'All'
    edge_min_today = 0.0

# Date range filter for historical results
if len(results_df) > 0:
    min_date = results_df['DATE'].min().date()
    max_date = results_df['DATE'].max().date()

    date_range = st.sidebar.date_input(
        "Date Range (Results)",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Apply filters to historical results
    filtered_df = results_df.copy()

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['DATE'].dt.date >= start_date) & 
                                   (filtered_df['DATE'].dt.date <= end_date)]

    if selected_stat_today != 'All':
        filtered_df = filtered_df[filtered_df['STAT'] == selected_stat_today]

    filtered_df = filtered_df[filtered_df['EDGE'] >= edge_min_today]
else:
    filtered_df = results_df
    st.sidebar.info("No historical data yet. Run track_results.py to populate.")

# ============================================================================
# SIDEBAR - EDGE PERFORMANCE TABLE
# ============================================================================

st.sidebar.divider()
st.sidebar.subheader("📈 Record by Edge")

if len(results_df) > 0:
    edge_breakdown = calculate_edge_breakdown(results_df)
    if len(edge_breakdown) > 0:
        st.sidebar.dataframe(
            edge_breakdown,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.sidebar.info("Not enough data yet.")
else:
    st.sidebar.info("No historical data yet.")

# ============================================================================
# TODAY'S PICKS (FILTERED)
# ============================================================================

# Header with date
eastern = pytz.timezone('US/Eastern')
today_str = datetime.now(eastern).strftime('%B %d, %Y')
st.header(f"🎯 Today's Edge Picks - {today_str}")

if len(todays_edges) > 0:
    # APPLY FILTERS to today's picks
    filtered_today = todays_edges.copy()

    if selected_stat_today != 'All':
        filtered_today = filtered_today[filtered_today['STAT'] == selected_stat_today]

    filtered_today = filtered_today[filtered_today['EDGE'] >= edge_min_today]

    # Display metrics for FILTERED picks
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Picks", len(filtered_today))
    with col2:
        if len(filtered_today) > 0:
            avg_edge = filtered_today['EDGE'].mean()
            st.metric("Avg Edge", f"+{avg_edge:.1f}")
        else:
            st.metric("Avg Edge", "N/A")
    with col3:
        if len(filtered_today) > 0:
            max_edge = filtered_today['EDGE'].max()
            st.metric("Max Edge", f"+{max_edge:.1f}")
        else:
            st.metric("Max Edge", "N/A")

    # Display FILTERED picks table
    st.subheader("📋 Today's Recommendations")

    if len(filtered_today) > 0:
        display_df = filtered_today[['PLAYER', 'TEAM', 'STAT', 'FD_LINE', 'PROJECTION', 'EDGE', 'BET', 'ODDS']].copy()
        # Sort by EDGE first (highest to lowest)
        display_df = display_df.sort_values('EDGE', ascending=False)
        # Then format EDGE column
        display_df['EDGE'] = display_df['EDGE'].apply(lambda x: f"+{x:.1f}")

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No picks match your filter criteria. Try adjusting the filters.")
else:
    st.info("No picks for today yet. Run find_edges_v2_TELEGRAM.py to generate.")

st.divider()

# ============================================================================
# OVERALL STATS
# ============================================================================

st.header("📈 Overall Performance")

if len(filtered_df) > 0:
    metrics = calculate_metrics(filtered_df)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Bets", metrics['total_bets'])

    with col2:
        st.metric("Wins", metrics['wins'], delta=None)

    with col3:
        st.metric("Losses", metrics['losses'], delta=None)

    with col4:
        win_rate_color = "normal" if metrics['win_rate'] < 53 else "inverse"
        st.metric("Win Rate", f"{metrics['win_rate']:.1f}%", 
                 delta=f"{metrics['win_rate']-53:.1f}% vs breakeven")

    with col5:
        record = f"{metrics['wins']}-{metrics['losses']}"
        if metrics['voids'] > 0:
            record += f" ({metrics['voids']} void)"
        st.metric("Record", record)

    st.divider()

    # Recent results table
    st.subheader("📋 Recent Results")

    recent_df = filtered_df.sort_values('DATE', ascending=False).head(20)

    display_recent = recent_df[['DATE', 'PLAYER', 'STAT', 'BET_TYPE', 'LINE', 
                                 'PROJECTION', 'ACTUAL', 'RESULT', 'MARGIN']].copy()
    display_recent['DATE'] = display_recent['DATE'].dt.strftime('%Y-%m-%d')

    # FORMAT all numeric columns to 1 decimal place as STRINGS
    display_recent['LINE'] = display_recent['LINE'].apply(lambda x: f"{x:.1f}")
    display_recent['PROJECTION'] = display_recent['PROJECTION'].apply(lambda x: f"{x:.1f}")
    display_recent['ACTUAL'] = display_recent['ACTUAL'].apply(lambda x: f"{x:.1f}")
    display_recent['MARGIN'] = display_recent['MARGIN'].apply(lambda x: f"{x:.1f}")

    # Color code results with DARK, HIGH CONTRAST colors
    def highlight_result(row):
        if row['RESULT'] == 'WIN':
            return ['background-color: #28a745; color: white; font-weight: bold'] * len(row)
        elif row['RESULT'] == 'LOSS':
            return ['background-color: #dc3545; color: white; font-weight: bold'] * len(row)
        else:
            return ['background-color: #ffc107; color: black; font-weight: bold'] * len(row)

    st.dataframe(
        display_recent.style.apply(highlight_result, axis=1),
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No results to display yet. Run your scripts to populate data!")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption(f"Last updated: {datetime.now(eastern).strftime('%B %d, %Y at %I:%M %p EST')}")
st.caption("Data refreshes every 5 minutes")
