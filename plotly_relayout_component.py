import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import time
from datetime import datetime

# --- IMPORT OUR NEW CUSTOM COMPONENT ---
from plotly_relayout_component import plotly_relayout

# ================================================
# 1. CONFIGURATION & THEME
# ================================================
st.set_page_config(layout="wide", page_title="Kgosi_View Pro", initial_sidebar_state="collapsed")
DATA_PATH = os.environ.get('KGOSI_DATA_PATH', '/mnt/kgosi_view_data/projects/finance/data')

TV_BG, TV_PANEL, TV_BORDER = "#131722", "#1e222d", "#2a2e39"
TV_GREEN, TV_RED, TV_BLUE = "#26a69a", "#ef5350", "#2962ff"

st.markdown(f"""
<style>
    .stApp {{ background-color: {TV_BG}; color: #d1d4dc; }}
    #MainMenu, header, footer {{ visibility: hidden; }}
    .block-container {{ padding: 0.5rem !important; max-width: 100% !important; }}
    div.stButton > button {{ background-color: transparent; border: 1px solid {TV_BORDER}; color: #d1d4dc; height: 35px; width: 100%; }}
    div.stButton > button:hover {{ background-color: {TV_BLUE}; border-color: {TV_BLUE}; color: white; }}
</style>
""", unsafe_allow_html=True)

# ================================================
# 2. SESSION STATE
# ================================================
defaults = {
    'symbol': 'EURUSD', 'timeframe': '1H', 'cursor': 500, 'zoom': 150,
    'balance': 10000.0, 'position': 0, 'entry_price': 0.0,
    'sl_price': 0.0, 'tp_price': 0.0, 'trades': [], 'is_playing': False
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

@st.cache_data
def load_data(symbol):
    path = f"{DATA_PATH}/{symbol}_1M.csv"
    if not os.path.exists(path): return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=['Date']).sort_values('Date').reset_index(drop=True)
    return df

df = load_data(st.session_state.symbol)
if df.empty: st.stop()

max_idx = len(df) - 1
st.session_state.cursor = min(st.session_state.cursor, max_idx)
view_df = df.iloc[max(0, st.session_state.cursor - st.session_state.zoom) : st.session_state.cursor + 1]
curr = df.iloc[st.session_state.cursor]

# ================================================
# 3. CHART BUILDER (WITH DRAGGABLE SHAPES)
# ================================================
fig = make_subplots(rows=1, cols=1)

# Main Candles
fig.add_trace(go.Candlestick(
    x=view_df['Date'], open=view_df['Open'], high=view_df['High'], low=view_df['Low'], close=view_df['Close'],
    increasing_line_color=TV_GREEN, decreasing_line_color=TV_RED, name="Price"
))

# --- ADD EDITABLE SHAPES (SL / TP) ---
shapes = []
x0, x1 = view_df['Date'].iloc[0], view_df['Date'].iloc[-1]

# Shape 0: Stop Loss (Red)
if st.session_state.sl_price > 0:
    shapes.append(dict(type="line", xref="x", yref="y", x0=x0, x1=x1, y0=st.session_state.sl_price, y1=st.session_state.sl_price, line=dict(color=TV_RED, width=2, dash="dash"), editable=True))
# Shape 1: Take Profit (Green)
if st.session_state.tp_price > 0:
    shapes.append(dict(type="line", xref="x", yref="y", x0=x0, x1=x1, y0=st.session_state.tp_price, y1=st.session_state.tp_price, line=dict(color=TV_GREEN, width=2, dash="dash"), editable=True))
# Entry Line (Blue, Not editable)
if st.session_state.entry_price > 0:
    shapes.append(dict(type="line", xref="x", yref="y", x0=x0, x1=x1, y0=st.session_state.entry_price, y1=st.session_state.entry_price, line=dict(color=TV_BLUE, width=1, dash="dot")))

fig.update_layout(
    shapes=shapes, height=650, margin=dict(l=10, r=60, t=10, b=10),
    paper_bgcolor=TV_BG, plot_bgcolor=TV_PANEL, xaxis_rangeslider_visible=False,
    font=dict(color="#d1d4dc"), xaxis=dict(showgrid=True, gridcolor=TV_BORDER), yaxis=dict(side="right", showgrid=True, gridcolor=TV_BORDER)
)

# ================================================
# 4. RENDER UI GRID
# ================================================
c_chart, c_panel = st.columns([0.8, 0.2])

with c_chart:
    # --- MAGIC COMPONENT: Renders Chart & Listens to Drags ---
    rel = plotly_relayout(fig.to_dict(), key='relayout1', height=650)

    # --- PARSE THE DRAG EVENT ---
    if rel:
        for k, v in rel.items():
            if k.startswith('shapes') and k.endswith('y0'):
                idx = int(k.split('[')[1].split(']')[0])
                new_price = float(v)
                # If we drag Shape 0 (SL), update session state
                if idx == 0 and st.session_state.sl_price > 0:
                    st.session_state.sl_price = new_price
                    st.rerun() # Refresh to show new numbers
                # If we drag Shape 1 (TP)
                elif idx == 1 and st.session_state.tp_price > 0:
                    st.session_state.tp_price = new_price
                    st.rerun()

    # Playback controls
    b1, b2, b3 = st.columns([1,4,1])
    with b1: 
        if st.button("⏪ Back"): st.session_state.cursor -= 1; st.rerun()
    with b2: 
        st.slider("", 0, max_idx, st.session_state.cursor, key="slide", label_visibility="collapsed")
    with b3: 
        if st.button("Next ⏩"): st.session_state.cursor += 1; st.rerun()

with c_panel:
    st.markdown(f"### {st.session_state.symbol}")
    st.metric("Balance", f"${st.session_state.balance:,.2f}")
    
    # MT4 Style Setups
    if st.session_state.position == 0:
        c1, c2 = st.columns(2)
        if c1.button("Set SL (Auto)"): st.session_state.sl_price = float(curr['Close']) - 0.0020; st.rerun()
        if c2.button("Set TP (Auto)"): st.session_state.tp_price = float(curr['Close']) + 0.0040; st.rerun()

    # Manual Adjusters (Synced with drag)
    new_sl = st.number_input("Stop Loss", value=float(st.session_state.sl_price), format="%.5f")
    new_tp = st.number_input("Take Profit", value=float(st.session_state.tp_price), format="%.5f")
    if new_sl != st.session_state.sl_price: st.session_state.sl_price = new_sl; st.rerun()
    if new_tp != st.session_state.tp_price: st.session_state.tp_price = new_tp; st.rerun()

    # Buy / Sell
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🟢 BUY MARKET", use_container_width=True):
        st.session_state.position = 100000
        st.session_state.entry_price = float(curr['Close'])
        st.rerun()
    if st.button("🔴 CLOSE TRADE", use_container_width=True):
        pnl = (float(curr['Close']) - st.session_state.entry_price) * st.session_state.position
        st.session_state.balance += pnl
        st.session_state.position = 0; st.session_state.entry_price = 0; st.session_state.sl_price = 0; st.session_state.tp_price = 0
        st.rerun()
