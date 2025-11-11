# app/pages/8_Analytics.py
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ensure project root is on path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.auth import check_login, get_user_info, get_user_stats
from utils.theme import apply_theme, get_theme_css

# Page config
st.set_page_config(page_title="Analytics - Samvaad", page_icon="📊", layout="wide")

apply_theme()
st.markdown(get_theme_css(), unsafe_allow_html=True)

# require login
if not check_login():
    st.warning("⚠️ Please login to access analytics.")
    st.switch_page("pages/1_🔐_Login.py")

user_info = get_user_info() or {}
stats = {}
try:
    stats = get_user_stats(user_info.get('user_id'))
except Exception as e:
    st.error(f"Could not load analytics: {e}")
    stats = None

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Analytics")
    st.markdown("Your progress at a glance")
    st.markdown("---")
    
    date_range = st.selectbox("Time Period:", 
                             ["Last 7 Days", "Last 30 Days", "All Time"])
    
    st.markdown("---")
    
    if st.button("🏠 Back to Dashboard", width='stretch'):
        st.switch_page("pages/3_🏠_Dashboard.py")

# Header
st.markdown("""
    <div class="hero-section">
        <h1 class="main-title">📊 Your Analytics</h1>
        <p class="tagline">Track your progress and achievements</p>
    </div>
""", unsafe_allow_html=True)

# Prepare safe defaults
actions = stats.get('actions', []) if stats else []
practice = stats.get('practice', []) if stats else []
history = stats.get('history', []) if stats else []

# Overview Metrics
st.markdown("### 📈 Overview")
col1, col2, col3, col4 = st.columns(4)

# compute metrics safely
try:
    total_actions = sum([a[1] for a in actions]) if actions else 0
except Exception:
    total_actions = 0

try:
    avg_confidence = (sum([a[2] for a in actions if a[2] is not None]) / len(actions)) if actions else 0
except Exception:
    avg_confidence = 0

practice_sessions = len(practice) if practice else 0

try:
    avg_practice_score = (sum([p[1] for p in practice]) / len(practice)) if practice else 0
except Exception:
    avg_practice_score = 0

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_actions}</div>
            <div class="metric-label">Total Translations</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_confidence:.0%}</div>
            <div class="metric-label">Avg Confidence</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{practice_sessions}</div>
            <div class="metric-label">Practice Sessions</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_practice_score:.1%}</div>
            <div class="metric-label">Practice Score</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Translation Types")
    
    if actions:
        # Convert to DataFrame (robust)
        try:
            action_data = pd.DataFrame(actions, columns=['Action Type', 'Count', 'Avg Confidence'])
            fig = px.pie(action_data, 
                         values='Count', 
                         names='Action Type',
                         title='Distribution of Translation Types',
                         color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Poppins', size=12)
            )
            st.plotly_chart(fig, use_container_width=False, width='stretch')
        except Exception as e:
            st.error(f"Could not render action chart: {e}")
    else:
        st.info("No data yet. Start using the translator!")

with col2:
    st.markdown("### 🎯 Confidence Distribution")
    
    if history:
        try:
            confidences = [h[2] for h in history if len(h) > 2 and h[2] is not None]
            if confidences:
                fig = go.Figure(data=[go.Histogram(
                    x=confidences,
                    nbinsx=20,
                    marker_color='#9CC3D5',
                    name='Confidence'
                )])
                fig.update_layout(
                    title='Recognition Confidence Distribution',
                    xaxis_title='Confidence Score',
                    yaxis_title='Frequency',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Poppins', size=12)
                )
                st.plotly_chart(fig, use_container_width=False, width='stretch')
            else:
                st.info("No confidence data available yet")
        except Exception as e:
            st.error(f"Could not render confidence histogram: {e}")
    else:
        st.info("No data yet. Start translating!")

# Practice Progress
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🎯 Practice Progress")

if practice:
    try:
        practice_df = pd.DataFrame(practice[:20], columns=['Sign', 'Score', 'Timestamp'])
        practice_df['Timestamp'] = pd.to_datetime(practice_df['Timestamp'])
        practice_df = practice_df.sort_values('Timestamp')
        
        fig = px.line(practice_df, 
                      x='Timestamp', 
                      y='Score',
                      title='Practice Score Over Time',
                      markers=True,
                      color_discrete_sequence=['#9CC3D5'])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Poppins', size=12),
            yaxis_range=[0, 1.05]
        )
        st.plotly_chart(fig, use_container_width=False, width='stretch')
    except Exception as e:
        st.error(f"Could not render practice progress: {e}")
else:
    st.info("Start practicing to see your progress!")

# Recent Activity
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🕒 Recent Activity")

if history:
    try:
        for i, h in enumerate(history[:10]):
            # Robust unpacking: convert to list, pad to length 4 and slice
            h_list = list(h)
            h_list += [None] * (4 - len(h_list))
            action_type, output, confidence, timestamp = h_list[:4]

            confidence_str = f" - {confidence:.0%}" if confidence else ""
            output_preview = str(output) if output is not None else ""
            st.markdown(f"""
            <div class="info-card" style="background:#f9fafb; border-radius:10px; padding:8px;">
                <strong>{action_type or 'Unknown'}</strong>{confidence_str}<br>
                <small>Result: {output_preview[:50]}</small><br>
                <small style="color: #888;">🕐 {timestamp or ''}</small>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not render recent history: {e}")
else:
    st.info("No activity yet. Start using Samvaad!")

# Achievements
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("### 🏆 Achievements")

col1, col2, col3, col4 = st.columns(4)

achievements = [
    ("🎯", "First Translation", total_actions >= 1),
    ("🔥", "10 Translations", total_actions >= 10),
    ("⭐", "High Accuracy", avg_confidence >= 0.8),
    ("💪", "Practice Champion", practice_sessions >= 5),
]

for i, (icon, name, achieved) in enumerate(achievements):
    with [col1, col2, col3, col4][i]:
        opacity = "1.0" if achieved else "0.3"
        st.markdown(f"""
        <div class="feature-card" style="opacity: {opacity};">
            <div class="feature-icon">{icon}</div>
            <h4>{name}</h4>
            <p>{'✅ Unlocked!' if achieved else '🔒 Locked'}</p>
        </div>
        """, unsafe_allow_html=True)
