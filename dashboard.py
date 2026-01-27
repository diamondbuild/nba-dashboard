import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import pytz

# ============================================================================
# TIMEZONE CONFIG
# ============================================================================

eastern = pytz.timezone('US/Eastern')

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
# CUSTOM CSS - ELITE STYLING
# ============================================================================

st.markdown("""
<style>
    * { font-family: 'Segoe UI', -apple-system, sans-serif; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0f172a 0%, #1a202c 100%); }
    h1, h2, h3 { color: #ffffff; font-weight: 700; }
    h1 { font-size: 2.5rem; margin-bottom: 1rem; }
    
    /* Elite pick cards */
    .elite-pick { background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(20, 83, 45, 0.1) 100%); border: 2px solid #22c55e; border-radius: 12px; padding: 20px; margin: 15px 0; box-shadow: 0 8px 32px rgba(34, 197, 94, 0.2); }
    .strong-pick { background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(30, 58, 138, 0.1) 100%); border: 2px solid #3b82f6; border-radius: 12px; padding: 20px; margin: 15px 0; box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2); }
    .solid-pick { background: linear-gradient(135deg, rgba(234, 179, 8, 0.15) 0%, rgba(120, 81, 16, 0.1) 100%); border: 2px solid #eab308; border-radius: 12px; padding: 20px; margin: 15px 0; box-shadow: 0 8px 32px rgba(234, 179, 8, 0.2); }
    
    /* Metric cards */
    .metric-card { background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(100, 116, 139, 0.3); border-radius: 12px; padding: 20px; text-align: center; backdrop-filter: blur(10px); }
    .metric-label { color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { color: #ffffff; font-size: 2rem; font-weight: 700; margin: 10px 0; }
    
    /* Info boxes */
    .info-box { background: rgba(30, 58, 138, 0.2); border-left: 4px solid #3b82f6; padding: 15px; border-radius: 8px; margin: 15px 0; }
    .warning-box { background: rgba(168, 85, 247, 0.2); border-left: 4px solid #a855f7; padding: 15px; border-radius: 8px; margin: 15px 0; }
    
    /* Table styling */
    [data-testid="stDataFrame"] { background: rgba(30, 41, 59, 0.6) !important; }
    
    /* Buttons */
    .stButton > button { background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); color: white; border: none; border-radius: 8px; padding: 12px 24px; font-weight: 600; transition: all 0.3s ease; }
    .stButton > button:hover { background: linear-gradient(135deg, #2563eb 0%, #1e3a8a 100%); box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3); }
    
    /* Text colors */
    .text-success { color: #22c55e; }
    .text-warning { color: #eab308; }
    .text-danger { color: #ef4444; }
    .text-info { color: #3b82f6; }
    
    hr { border-color: rgba(100, 116, 139, 0.2); }
</style>
""", unsafe_allow_html=True)

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

def get_tier_badge(edge):
    """Get tier badge based on edge"""
    if edge >= 5:
        return "🟢 ELITE", "#22c55e"
    elif edge >= 4:
        return "🔵 STRONG", "#3b82f6"
    else:
        return "🟡 SOLID", "#eab308"

def calculate_metrics(df):
    """Calculate overall metrics"""
    if len(df) == 0:
        return {'total_bets': 0, 'wins': 0, 'losses': 0, 'voids': 0, 'win_rate': 0, 'avg_margin_win': 0, 'avg_margin_loss': 0}
    
    valid_df = df[df['RESULT'] != 'VOID']
    wins = len(valid_df[valid_df['RESULT'] == 'WIN'])
    losses = len(valid_df[valid_df['RESULT'] == 'LOSS'])
    voids = len(df[df['RESULT'] == 'VOID'])
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    
    win_margins = valid_df[valid_df['RESULT'] == 'WIN']['MARGIN']
    loss_margins = valid_df[valid_df['RESULT'] == 'LOSS']['MARGIN']
    avg_margin_win = win_margins.mean() if len(win_margins) > 0 else 0
    avg_margin_loss = loss_margins.mean() if len(loss_margins) > 0 else 0
    
    return {'total_bets': len(valid_df), 'wins': wins, 'losses': losses, 'voids': voids, 'win_rate': win_rate, 'avg_margin_win': avg_margin_win, 'avg_margin_loss': avg_margin_loss}

def display_pick_card(player, stat, line, projected, edge, odds, kelly_size, idx):
    """Display a professional pick card with proper tiles"""
    tier_text, color = get_tier_badge(edge)
    bet_amount = (kelly_size / 100) * 1000
    payout = bet_amount * (odds / 100) if odds > 0 else bet_amount * (100 / abs(odds))
    ev = payout * (edge / 100)
    
    # Header
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown(f"### {idx}. {player}")
    with col2:
        st.markdown(f"**{stat}** Over **{line}**")
    with col3:
        st.markdown(f"<div style='text-align: right; font-size: 1.1rem; font-weight: bold; color: {color};'>{tier_text}</div>", unsafe_allow_html=True)
    
    # Key metrics tiles
    tile1, tile2, tile3, tile4 = st.columns(4)
    
    with tile1:
        st.markdown(f"<div style='padding: 15px; background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; text-align: center;'><p style='margin: 0; color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;'>Projected</p><p style='margin: 8px 0; color: #ffffff; font-size: 1.3rem; font-weight: bold;'>{projected}</p></div>", unsafe_allow_html=True)
    
    with tile2:
        st.markdown(f"<div style='padding: 15px; background: rgba(30, 41, 59, 0.8); border: 1px solid {color}; border-radius: 8px; text-align: center;'><p style='margin: 0; color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;'>Edge</p><p style='margin: 8px 0; color: {color}; font-size: 1.3rem; font-weight: bold;'>+{edge}%</p></div>", unsafe_allow_html=True)
    
    with tile3:
        st.markdown(f"<div style='padding: 15px; background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; text-align: center;'><p style='margin: 0; color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;'>Odds</p><p style='margin: 8px 0; color: #ffffff; font-size: 1.3rem; font-weight: bold;'>{odds}</p></div>", unsafe_allow_html=True)
    
    with tile4:
        st.markdown(f"<div style='padding: 15px; background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; text-align: center;'><p style='margin: 0; color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;'>Kelly</p><p style='margin: 8px 0; color: #ffffff; font-size: 1.3rem; font-weight: bold;'>{kelly_size}%</p></div>", unsafe_allow_html=True)
    
    # Action tiles
    st.markdown("")
    action1, action2, action3 = st.columns(3)
    
    with action1:
        st.markdown(f"<div style='padding: 20px; background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(20, 83, 45, 0.1) 100%); border: 2px solid #22c55e; border-radius: 10px; text-align: center;'><p style='margin: 0; color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; font-weight: 500;'>💵 Bet Amount</p><p style='margin: 12px 0 0 0; color: #22c55e; font-size: 1.6rem; font-weight: bold;'>${bet_amount:.0f}</p></div>", unsafe_allow_html=True)
    
    with action2:
        st.markdown(f"<div style='padding: 20px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(30, 58, 138, 0.1) 100%); border: 2px solid #3b82f6; border-radius: 10px; text-align: center;'><p style='margin: 0; color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; font-weight: 500;'>🎯 If You Win</p><p style='margin: 12px 0 0 0; color: #3b82f6; font-size: 1.6rem; font-weight: bold;'>${payout:.0f}</p></div>", unsafe_allow_html=True)
    
    with action3:
        st.markdown(f"<div style='padding: 20px; background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(20, 83, 45, 0.1) 100%); border: 2px solid #22c55e; border-radius: 10px; text-align: center;'><p style='margin: 0; color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; font-weight: 500;'>📈 Expected Value</p><p style='margin: 12px 0 0 0; color: #22c55e; font-size: 1.6rem; font-weight: bold;'>+${ev:.0f}</p></div>", unsafe_allow_html=True)
    
    st.markdown("---")

def display_guidance():
    """Display betting guidance"""
    st.markdown("### 💡 Smart Betting Guidance")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <b>🎯 Kelly Criterion Sizing</b><br>
        The recommended bet size maximizes long-term wealth growth while managing risk. <b>Never exceed the suggested bet size.</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <b>📊 Edge Tiers</b><br>
        • 🟢 <b>ELITE (5%+)</b>: Strongest opportunities<br>
        • 🔵 <b>STRONG (4-5%)</b>: Good value<br>
        • 🟡 <b>SOLID (3.5-4%)</b>: Play smaller
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="warning-box">
        <b>⚠️ Risk Management</b><br>
        • Spread bets across games<br>
        • Track all results<br>
        • Stop if losing streak = 3<br>
        • Scale up with wins
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# MAIN APP
# ============================================================================

col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.markdown("🏀", unsafe_allow_html=True)
with col2:
    st.markdown("# NBA EDGE FINDER DASHBOARD")

st.markdown(f"**Updated:** {datetime.now(eastern).strftime('%B %d, %Y at %I:%M %p EST')}", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🎯 Today's Elite Picks", "📊 Historical Results", "📈 Performance"])

# === TAB 1: TODAY'S PICKS ===
with tab1:
    today_edges = load_todays_edges()
    
    if len(today_edges) == 0:
        st.info("⏳ No picks available yet. Check back later!")
    else:
        st.markdown("### 📈 Today's Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Picks</div><div class="metric-value">{len(today_edges)}</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Edge</div><div class="metric-value">+{today_edges['EDGE'].mean():.2f}%</div></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Best Edge</div><div class="metric-value">+{today_edges['EDGE'].max():.2f}%</div></div>""", unsafe_allow_html=True)
        with col4:
            elite_count = len(today_edges[today_edges['EDGE'] >= 5])
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Elite Picks</div><div class="metric-value" style="color: #22c55e;">{elite_count}</div></div>""", unsafe_allow_html=True)
        with col5:
            total_ev = (today_edges['EDGE'] * (today_edges['KELLY_SIZE'] / 100) * 1000 / 100).sum()
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Total EV</div><div class="metric-value" style="color: #22c55e;">+${total_ev:.0f}</div></div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔍 Filter Picks")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            stat_filter = st.multiselect("Stat Type", options=today_edges['STAT'].unique(), default=today_edges['STAT'].unique(), key="stat_filter")
        with col2:
            edge_min = st.slider("Minimum Edge (%)", min_value=0.0, max_value=10.0, value=3.5, step=0.5, key="edge_min")
        with col3:
            tier_filter = st.multiselect("Tier", options=["🟢 ELITE", "🔵 STRONG", "🟡 SOLID"], default=["🟢 ELITE", "🔵 STRONG", "🟡 SOLID"], key="tier_filter")
        
        filtered = today_edges[(today_edges['STAT'].isin(stat_filter)) & (today_edges['EDGE'] >= edge_min)]
        tier_edges = []
        for _, row in filtered.iterrows():
            tier_text, _ = get_tier_badge(row['EDGE'])
            if any(tier in tier_text for tier in [t.split()[1] for t in tier_filter]):
                tier_edges.append(row)
        
        filtered = pd.DataFrame(tier_edges) if tier_edges else pd.DataFrame()
        st.markdown("---")
        
        if len(filtered) > 0:
            st.markdown(f"### 🎯 {len(filtered)} Recommended Bets ($1000 Bankroll)")
            for idx, (_, row) in enumerate(filtered.iterrows(), 1):
                display_pick_card(row['PLAYER'], row['STAT'], row['LINE'], row['PROJECTED'], row['EDGE'], row['ODDS'], row['KELLY_SIZE'], idx)
            
            st.markdown("### 📊 Edge Distribution")
            col1, col2, col3 = st.columns(3)
            elite = len(filtered[filtered['EDGE'] >= 5])
            strong = len(filtered[(filtered['EDGE'] >= 4) & (filtered['EDGE'] < 5)])
            solid = len(filtered[filtered['EDGE'] < 4])
            
            with col1:
                st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #22c55e;"><div class="metric-label">Elite</div><div class="metric-value" style="color: #22c55e;">{elite}</div></div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #3b82f6;"><div class="metric-label">Strong</div><div class="metric-value" style="color: #3b82f6;">{strong}</div></div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #eab308;"><div class="metric-label">Solid</div><div class="metric-value" style="color: #eab308;">{solid}</div></div>""", unsafe_allow_html=True)
            
            st.markdown("---")
            csv = filtered.to_csv(index=False)
            st.download_button("📥 Download CSV", data=csv, file_name=f"picks_{datetime.now(eastern).strftime('%Y-%m-%d')}.csv", mime="text/csv")
        else:
            st.warning("No picks match your filters")
        
        st.markdown("---")
        display_guidance()

# === TAB 2: HISTORICAL RESULTS ===
with tab2:
    st.markdown("### 📊 Historical Results")
    results_df = load_results_data()
    
    if len(results_df) == 0:
        st.info("No historical data available yet")
    else:
        st.dataframe(results_df, use_container_width=True, height=500)
        csv = results_df.to_csv(index=False)
        st.download_button("📥 Download CSV", data=csv, file_name=f"results_{datetime.now(eastern).strftime('%Y-%m-%d')}.csv", mime="text/csv")

# === TAB 3: PERFORMANCE ANALYSIS ===
with tab3:
    results_df = load_results_data()
    
    if len(results_df) == 0:
        st.info("No data to analyze yet")
    else:
        metrics = calculate_metrics(results_df)
        st.markdown("### 📈 Overall Performance")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Bets</div><div class="metric-value">{metrics['total_bets']}</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Wins</div><div class="metric-value" style="color: #22c55e;">{metrics['wins']}</div></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Losses</div><div class="metric-value" style="color: #ef4444;">{metrics['losses']}</div></div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Win Rate</div><div class="metric-value" style="color: #3b82f6;">{metrics['win_rate']:.1f}%</div></div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<p style='text-align: center; color: #64748b; font-size: 0.85rem;'>NBA Edge Finder Dashboard | Last Updated {datetime.now(eastern).strftime('%B %d, %Y at %I:%M %p EST')}</p>", unsafe_allow_html=True)
