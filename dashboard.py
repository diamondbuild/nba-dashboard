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
    body { font-family: 'Segoe UI', sans-serif; }
    .metric-card { 
        background: linear-gradient(135deg, #1e3a8a 0%, #1f2937 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .stat-value { font-size: 32px; font-weight: bold; }
    .stat-label { font-size: 14px; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTO TEAM LOOKUP
# ============================================================================

@st.cache_data(ttl=86400)
def fetch_nba_player_teams():
    """Fetch current NBA rosters from ESPN API"""
    team_map = {}
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'sports' in data and len(data['sports']) > 0:
                teams = data['sports'][0]['leagues'][0]['teams']
                for team_data in teams:
                    team = team_data['team']
                    team_abbr = team.get('abbreviation', '')
                    team_id = team.get('id', '')
                    roster_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/roster"
                    try:
                        roster_response = requests.get(roster_url, timeout=5)
                        if roster_response.status_code == 200:
                            roster_data = roster_response.json()
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
    if player_name in team_map:
        return team_map[player_name]
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
    valid_df['EDGE_BUCKET'] = pd.cut(valid_df['EDGE'], bins=[0, 2.5, 3.5, 4.5, 100], labels=['2.0-2.5', '2.5-3.5', '3.5-4.5', '4.5+'])
    
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

def calculate_stat_type_breakdown(df):
    """Calculate win rate by stat type"""
    if len(df) == 0:
        return pd.DataFrame()
    
    valid_df = df[df['RESULT'] != 'VOID'].copy()
    stat_types = valid_df['STAT'].unique()
    
    breakdown = []
    for stat_type in sorted(stat_types):
        type_df = valid_df[valid_df['STAT'] == stat_type]
        if len(type_df) > 0:
            wins = (type_df['RESULT'] == 'WIN').sum()
            losses = (type_df['RESULT'] == 'LOSS').sum()
            total = wins + losses
            win_rate = (wins / total * 100) if total > 0 else 0
            breakdown.append({
                'Stat': stat_type,
                'Record': f"{wins}-{losses}",
                'Win%': f"{win_rate:.1f}%"
            })
    
    return pd.DataFrame(breakdown)

# ============================================================================
# MAIN APP
# ============================================================================

st.markdown('# 🏀 NBA EDGE FINDER DASHBOARD')

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Today's Picks", "📈 Historical Results", "📉 Performance Analysis"])

# === TAB 1: TODAY'S PICKS ===
with tab1:
    st.markdown('## 🎯 Today\'s Edge Picks - ' + datetime.now().strftime('%B %d, %Y'))
    
    # Load today's edges
    today_edges = load_todays_edges()
    
    if len(today_edges) == 0:
        st.info("⏳ No edge picks available yet. Check back later!")
    else:
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Picks", len(today_edges))
        
        with col2:
            st.metric("Avg Edge", f"+{today_edges['EDGE'].mean():.2f}%")
        
        with col3:
            st.metric("Best Edge", f"+{today_edges['EDGE'].max():.2f}%")
        
        with col4:
            st.metric("Lowest Edge", f"+{today_edges['EDGE'].min():.2f}%")
        
        # Filters
        st.markdown("### 🔍 Filters")
        col1, col2 = st.columns(2)
        
        with col1:
            stat_filter = st.multiselect(
                "Stat Type",
                options=today_edges['STAT'].unique(),
                default=today_edges['STAT'].unique()
            )
        
        with col2:
            edge_min_today = st.slider(
                "Minimum Edge (%)",
                min_value=0.0,
                max_value=10.0,
                value=3.5,
                step=0.5
            )
        
        # Filter data
        filtered_today = today_edges[today_edges['STAT'].isin(stat_filter)]
        
        # Check if EDGE column exists and filter
        if 'EDGE' in filtered_today.columns:
            filtered_today = filtered_today[filtered_today['EDGE'] >= edge_min_today]
        
        # Display picks
        st.markdown(f"### 📋 {len(filtered_today)} Filtered Picks")
        
        if len(filtered_today) > 0:
            # Create display dataframe
            display_df = filtered_today[['PLAYER', 'STAT', 'LINE', 'PROJECTED', 'EDGE', 'ODDS', 'KELLY_SIZE']].copy()
            
            # Format columns
            if 'EDGE' in display_df.columns:
                display_df['EDGE'] = display_df['EDGE'].apply(lambda x: f"+{x:.2f}%" if pd.notna(x) else "N/A")
            if 'KELLY_SIZE' in display_df.columns:
                display_df['KELLY_SIZE'] = display_df['KELLY_SIZE'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            # Download button
            csv = filtered_today.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"edges_{datetime.now().strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No picks match your filters")

# === TAB 2: HISTORICAL RESULTS ===
with tab2:
    st.markdown('## 📊 Historical Results')
    
    results_df = load_results_data()
    
    if len(results_df) == 0:
        st.info("No historical data available yet. Start tracking results!")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            stat_filter = st.multiselect(
                "Stat Type",
                options=results_df['STAT'].unique(),
                default=results_df['STAT'].unique(),
                key="hist_stat"
            )
        
        with col2:
            date_range = st.date_input(
                "Date Range",
                value=(results_df['DATE'].min(), results_df['DATE'].max()),
                key="hist_date"
            )
        
        with col3:
            result_filter = st.multiselect(
                "Result",
                options=['WIN', 'LOSS', 'VOID'],
                default=['WIN', 'LOSS', 'VOID'],
                key="hist_result"
            )
        
        # Filter data
        filtered_results = results_df[
            (results_df['STAT'].isin(stat_filter)) &
            (results_df['DATE'].dt.date >= date_range[0]) &
            (results_df['DATE'].dt.date <= date_range[1]) &
            (results_df['RESULT'].isin(result_filter))
        ]
        
        # Display results
        st.dataframe(filtered_results, use_container_width=True, height=400)
        
        # Download button
        csv = filtered_results.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"results_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )

# === TAB 3: PERFORMANCE ANALYSIS ===
with tab3:
    st.markdown('## 📈 Performance Analytics')
    
    results_df = load_results_data()
    
    if len(results_df) == 0:
        st.info("No data to analyze yet")
    else:
        # Overall metrics
        st.markdown('### 📊 Overall Performance')
        metrics = calculate_metrics(results_df)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Bets", metrics['total_bets'])
        col2.metric("Wins", metrics['wins'])
        col3.metric("Losses", metrics['losses'])
        col4.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
        
        # Edge breakdown
        st.markdown('### 📊 Win Rate by Edge Range')
        edge_breakdown = calculate_edge_breakdown(results_df)
        if len(edge_breakdown) > 0:
            st.dataframe(edge_breakdown, use_container_width=True)
        
        # Stat type breakdown
        st.markdown('### 📊 Win Rate by Stat Type')
        stat_breakdown = calculate_stat_type_breakdown(results_df)
        if len(stat_breakdown) > 0:
            st.dataframe(stat_breakdown, use_container_width=True)

st.markdown('---')
st.markdown('<p style="text-align: center; color: gray;">NBA Edge Finder Dashboard | Updated ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S EST') + '</p>', unsafe_allow_html=True)
