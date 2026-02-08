import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import time

from config import THEME, CSS, CHART_LAYOUT, header_bar, status_bar, playback_section_label, section_divider

# ==============================================================================
# PAGE CONFIG
# ==============================================================================
st.set_page_config(
    layout="wide",
    page_title="Kgosi_View Pro",
    page_icon="$",
    initial_sidebar_state="collapsed",
)

DATA_PATH = os.environ.get('KGOSI_DATA_PATH', '/mnt/kgosi_view_data/projects/finance/data')

# Inject Master CSS
st.markdown(CSS, unsafe_allow_html=True)


# ==============================================================================
# SESSION STATE
# ==============================================================================
defaults = {
    'symbol': 'EURUSD',
    'timeframe': '1H',
    'cursor': 500,
    'zoom': 150,
    # Trading
    'sl_price': 0.0,
    'tp_price': 0.0,
    'entry_price': 0.0,
    'trades': [],
    'position': 0,
    'position_type': None,
    'balance': 10000.0,
    'realized_pnl': 0.0,
    # Overlays
    'overlay_symbols': [],
    'overlay_cache': {},
    'overlay_cache_key': None,
    # Playback
    'is_playing': False,
    'playback_speed': 200,
    'last_advance_time': None,
    'substep': 0,
    'substeps_per_candle': 6,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ==============================================================================
# DATA ENGINE
# ==============================================================================
@st.cache_data
def get_data(symbol, timeframe):
    p1 = os.path.join(DATA_PATH, f"{symbol}_1M.csv")
    p2 = os.path.join(DATA_PATH, f"{symbol}.csv")
    path = p1 if os.path.exists(p1) else p2

    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, parse_dates=['Date'])
        if timeframe != '1M':
            tf_map = {'5M': '5min', '15M': '15min', '1H': '1h', '4H': '4h', '1D': '1D'}
            if timeframe in tf_map:
                df = df.set_index('Date').resample(tf_map[timeframe]).agg({
                    'Open': 'first', 'High': 'max', 'Low': 'min',
                    'Close': 'last', 'Volume': 'sum'
                }).dropna().reset_index()
        return df
    except Exception:
        return pd.DataFrame()


def align_overlay_data(main_dates, overlay_df):
    if overlay_df.empty:
        return pd.DataFrame()
    aligned = pd.DataFrame({'Date': main_dates}).sort_values('Date')
    overlay_sorted = overlay_df.sort_values('Date')
    res = pd.merge_asof(aligned, overlay_sorted, on='Date', direction='forward')
    if res['Close'].isna().any():
        res.ffill(inplace=True)
        res.bfill(inplace=True)
    return res


# ── Load available files ──
try:
    files = sorted(set(
        f.replace('_1M.csv', '').replace('.csv', '')
        for f in os.listdir(DATA_PATH) if f.endswith('.csv')
    ))
    files = files if files else ['EURUSD']
    overlay_files = [f for f in files if f != st.session_state.symbol]
except Exception:
    files, overlay_files = ['EURUSD'], []

df = get_data(st.session_state.symbol, st.session_state.timeframe)
if df.empty:
    st.error("No data found. Check DATA_PATH.")
    st.stop()


# ── Overlay Cache ──
def ensure_overlay_cache():
    current_key = (
        tuple(st.session_state.overlay_symbols),
        st.session_state.timeframe,
        st.session_state.symbol,
    )
    if st.session_state.get('overlay_cache_key') != current_key:
        st.session_state.overlay_cache = {}
        for sym in st.session_state.overlay_symbols:
            odf = get_data(sym, st.session_state.timeframe)
            if not odf.empty:
                aligned = align_overlay_data(df['Date'], odf)
                st.session_state.overlay_cache[sym] = aligned
        st.session_state.overlay_cache_key = current_key


ensure_overlay_cache()

# ── View Slicing ──
max_idx = len(df) - 1
st.session_state.cursor = min(st.session_state.cursor, max_idx)
view_start = max(0, st.session_state.cursor - st.session_state.zoom)
view_df = df.iloc[view_start: st.session_state.cursor + 1].reset_index(drop=True)
curr = df.iloc[st.session_state.cursor]

# Calculate change %
if st.session_state.cursor > 0:
    prev_close = df.iloc[st.session_state.cursor - 1]['Close']
    change_pct = ((curr['Close'] - prev_close) / prev_close) * 100
else:
    change_pct = 0.0

# Calculate unrealized PnL
unrealized_pnl = 0.0
if st.session_state.position != 0 and st.session_state.entry_price > 0:
    if st.session_state.position_type == "LONG":
        unrealized_pnl = (curr['Close'] - st.session_state.entry_price) * st.session_state.position
    elif st.session_state.position_type == "SHORT":
        unrealized_pnl = (st.session_state.entry_price - curr['Close']) * st.session_state.position


# ==============================================================================
# TOOLBAR — Symbol | TF | Overlays
# ==============================================================================
tb1, tb2, tb3, tb_spacer = st.columns([1.2, 0.8, 2.5, 5.5])

with tb1:
    new_sym = st.selectbox(
        "Symbol", files,
        index=files.index(st.session_state.symbol) if st.session_state.symbol in files else 0,
        label_visibility="collapsed",
    )
    if new_sym != st.session_state.symbol:
        st.session_state.symbol = new_sym
        st.session_state.cursor = min(st.session_state.cursor, 500)
        st.rerun()

with tb2:
    tfs = ['1M', '5M', '15M', '1H', '4H', '1D']
    cur_tf_idx = tfs.index(st.session_state.timeframe) if st.session_state.timeframe in tfs else 3
    new_tf = st.selectbox("TF", tfs, index=cur_tf_idx, label_visibility="collapsed")
    if new_tf != st.session_state.timeframe:
        st.session_state.timeframe = new_tf
        st.rerun()

with tb3:
    selected_overlays = st.multiselect(
        "Overlays", options=overlay_files,
        default=st.session_state.overlay_symbols,
        max_selections=4, label_visibility="collapsed",
        placeholder="Add overlays...",
    )
    if selected_overlays != st.session_state.overlay_symbols:
        st.session_state.overlay_symbols = selected_overlays
        st.session_state.overlay_cache_key = None
        st.rerun()


# ==============================================================================
# PLAYBACK CONTROLS BAR
# ==============================================================================

# Layout: nav | play/speed | trade | reset
pc1, pc2, pc3, pc4, pc5 = st.columns([1.8, 1.2, 1.5, 2.5, 0.6])

with pc1:
    st.markdown(playback_section_label("NAVIGATE"), unsafe_allow_html=True)
    n1, n2, n3, n4 = st.columns([1, 1, 1, 1])
    with n1:
        if st.button("⏮", use_container_width=True, help="Jump to start"):
            st.session_state.cursor = 0
            st.rerun()
    with n2:
        if st.button("◀", use_container_width=True, help="Step back"):
            st.session_state.cursor = max(0, st.session_state.cursor - 1)
            st.rerun()
    with n3:
        if st.button("▶", use_container_width=True, help="Step forward"):
            st.session_state.cursor = min(max_idx, st.session_state.cursor + 1)
            st.rerun()
    with n4:
        if st.button("⏭", use_container_width=True, help="Jump to end"):
            st.session_state.cursor = max_idx
            st.rerun()

with pc2:
    st.markdown(playback_section_label("PLAYBACK"), unsafe_allow_html=True)
    # Play / Pause with visual distinction
    if st.session_state.is_playing:
        pause_css = f'<style>div[data-testid="stHorizontalBlock"]:has(> div:nth-child(2)) .pause-target button {{ background: {THEME["RED_DIM"]} !important; border-color: {THEME["RED"]} !important; color: {THEME["RED"]} !important; }}</style>'
        st.markdown(pause_css, unsafe_allow_html=True)
        btn_label = "⏸  Pause"
    else:
        btn_label = "▶  Play"

    if st.button(btn_label, use_container_width=True):
        st.session_state.is_playing = not st.session_state.is_playing
        st.session_state.last_advance_time = None
        if st.session_state.is_playing:
            st.session_state._old_substeps = st.session_state.substeps_per_candle
            st.session_state.substeps_per_candle = 1
        else:
            st.session_state.substeps_per_candle = st.session_state.get('_old_substeps', 6)
        st.rerun()

with pc3:
    st.markdown(playback_section_label("SPEED (MS)"), unsafe_allow_html=True)
    st.session_state.playback_speed = st.slider(
        "Speed", 50, 1000, st.session_state.playback_speed, step=50,
        label_visibility="collapsed",
    )

with pc4:
    st.markdown(playback_section_label("GO TO DATE"), unsafe_allow_html=True)
    # Build min/max dates from the dataset
    min_date = df['Date'].iloc[0].date()
    max_date = df['Date'].iloc[-1].date()
    current_date = df.iloc[st.session_state.cursor]['Date'].date()
    picked_date = st.date_input(
        "Go to date",
        value=current_date,
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed",
    )
    if picked_date != current_date:
        # Find the closest bar index to the selected date
        target = pd.Timestamp(picked_date)
        idx = (df['Date'] - target).abs().idxmin()
        st.session_state.cursor = int(idx)
        st.rerun()

with pc5:
    st.markdown(playback_section_label("RESET"), unsafe_allow_html=True)
    if st.button("↺", use_container_width=True, help="Reset to bar 500"):
        st.session_state.update({
            'cursor': 500, 'is_playing': False,
            'sl_price': 0.0, 'tp_price': 0.0,
            'entry_price': 0.0, 'position': 0,
            'position_type': None,
        })
        st.rerun()



# ==============================================================================
# CANDLESTICK CHART
# ==============================================================================
fig = go.Figure()

# Candlesticks
fig.add_trace(go.Candlestick(
    x=view_df['Date'],
    open=view_df['Open'],
    high=view_df['High'],
    low=view_df['Low'],
    close=view_df['Close'],
    increasing=dict(line=dict(color=THEME['GREEN'], width=1), fillcolor=THEME['GREEN']),
    decreasing=dict(line=dict(color=THEME['RED'], width=1), fillcolor=THEME['RED']),
    name=st.session_state.symbol,
    whiskerwidth=0.4,
))

# Overlays from cache
overlay_idx = 0
overlay_colors = [THEME['BLUE'], THEME['YELLOW'], THEME['PURPLE'], THEME['CYAN']]
for sym in st.session_state.overlay_symbols:
    if sym in st.session_state.overlay_cache:
        full_overlay = st.session_state.overlay_cache[sym]
        ov_view = full_overlay.iloc[view_start: st.session_state.cursor + 1]
        color = overlay_colors[overlay_idx % len(overlay_colors)]
        yaxis_key = f'y{overlay_idx + 2}'

        fig.add_trace(go.Scatter(
            x=ov_view['Date'], y=ov_view['Close'],
            mode='lines', name=sym, yaxis=yaxis_key,
            line=dict(color=color, width=1.5),
        ))
        overlay_idx += 1

# SL / TP / Entry lines
if st.session_state.sl_price > 0:
    fig.add_hline(
        y=st.session_state.sl_price, line_dash="dash",
        line_color=THEME['RED'], line_width=1,
        annotation_text="SL", annotation_font_color=THEME['RED'],
        annotation_font_size=10,
    )
if st.session_state.tp_price > 0:
    fig.add_hline(
        y=st.session_state.tp_price, line_dash="dash",
        line_color=THEME['GREEN'], line_width=1,
        annotation_text="TP", annotation_font_color=THEME['GREEN'],
        annotation_font_size=10,
    )
if st.session_state.entry_price > 0:
    fig.add_hline(
        y=st.session_state.entry_price, line_dash="dot",
        line_color=THEME['BLUE'], line_width=1,
        annotation_text="ENTRY", annotation_font_color=THEME['BLUE'],
        annotation_font_size=10,
    )

# Current price marker — horizontal dashed line + annotation on right
fig.add_shape(
    type="line",
    x0=view_df['Date'].iloc[0], x1=view_df['Date'].iloc[-1],
    y0=curr['Close'], y1=curr['Close'],
    line=dict(color=THEME['BLUE'], width=0.8, dash="dot"),
)
fig.add_annotation(
    x=view_df['Date'].iloc[-1], y=curr['Close'],
    text=f" {curr['Close']:,.5f}" if curr['Close'] < 10 else f" {curr['Close']:,.2f}",
    showarrow=False, xanchor="left",
    font=dict(family="JetBrains Mono", size=10, color=THEME['WHITE']),
    bgcolor=THEME['BLUE'], borderpad=3,
)

# Build layout
layout = dict(CHART_LAYOUT)

if overlay_idx > 0:
    # Each overlay axis gets ~7% of chart width on the right
    chart_right = max(0.65, 0.93 - (overlay_idx * 0.07))
    layout['xaxis']['domain'] = [0, chart_right]
    layout['margin'] = dict(l=0, r=10, t=0, b=0)

    for i in range(overlay_idx):
        color = overlay_colors[i % len(overlay_colors)]
        # Place each axis in its own slot after the chart area
        axis_pos = chart_right + 0.02 + (i * 0.07)
        layout[f'yaxis{i + 2}'] = dict(
            title=dict(text=st.session_state.overlay_symbols[i], font=dict(color=color, size=10)),
            tickfont=dict(color=color, family="JetBrains Mono", size=9),
            overlaying='y', side='right', anchor='free', position=min(axis_pos, 0.99),
            showgrid=False,
        )
else:
    layout['margin'] = dict(l=0, r=60, t=0, b=0)

fig.update_layout(**layout)

st.plotly_chart(
    fig, use_container_width=True,
    config={
        'displaylogo': False,
        'scrollZoom': True,
        'modeBarButtonsToAdd': ['drawline', 'drawrect', 'eraseshape'],
        'modeBarButtonsToRemove': ['autoScale2d'],
    },
)

# ==============================================================================
# TRADE PANEL
# ==============================================================================

tr1, tr2, tr3, tr4, tr5 = st.columns([1, 1, 1, 1, 1])

with tr1:
    st.markdown(playback_section_label("STOP LOSS"), unsafe_allow_html=True)
    st.session_state.sl_price = st.number_input(
        "SL", value=float(st.session_state.sl_price),
        format="%.5f", label_visibility="collapsed", step=0.00010,
    )

with tr2:
    st.markdown(playback_section_label("TAKE PROFIT"), unsafe_allow_html=True)
    st.session_state.tp_price = st.number_input(
        "TP", value=float(st.session_state.tp_price),
        format="%.5f", label_visibility="collapsed", step=0.00010,
    )

with tr3:
    st.markdown(playback_section_label("BUY / LONG"), unsafe_allow_html=True)
    buy_css = f'<style>[data-testid="stHorizontalBlock"] > div:nth-child(3) .stButton > button {{ background: {THEME["GREEN_DIM"]} !important; border: 1px solid {THEME["GREEN"]} !important; color: {THEME["GREEN"]} !important; font-weight: 700 !important; }} [data-testid="stHorizontalBlock"] > div:nth-child(3) .stButton > button:hover {{ background: {THEME["GREEN"]} !important; color: {THEME["BG"]} !important; }}</style>'
    st.markdown(buy_css, unsafe_allow_html=True)
    if st.button("BUY", use_container_width=True):
        if st.session_state.position == 0:
            st.session_state.position = 100000
            st.session_state.position_type = "LONG"
            st.session_state.entry_price = curr['Close']
            st.rerun()

with tr4:
    st.markdown(playback_section_label("SELL / SHORT"), unsafe_allow_html=True)
    sell_css = f'<style>[data-testid="stHorizontalBlock"] > div:nth-child(4) .stButton > button {{ background: {THEME["RED_DIM"]} !important; border: 1px solid {THEME["RED"]} !important; color: {THEME["RED"]} !important; font-weight: 700 !important; }} [data-testid="stHorizontalBlock"] > div:nth-child(4) .stButton > button:hover {{ background: {THEME["RED"]} !important; color: {THEME["BG"]} !important; }}</style>'
    st.markdown(sell_css, unsafe_allow_html=True)
    if st.button("SELL", use_container_width=True):
        if st.session_state.position == 0:
            st.session_state.position = 100000
            st.session_state.position_type = "SHORT"
            st.session_state.entry_price = curr['Close']
            st.rerun()

with tr5:
    st.markdown(playback_section_label("CLOSE POSITION"), unsafe_allow_html=True)
    if st.button("CLOSE", use_container_width=True, disabled=(st.session_state.position == 0)):
        if st.session_state.position != 0:
            # Calculate PnL
            if st.session_state.position_type == "LONG":
                pnl = (curr['Close'] - st.session_state.entry_price) * st.session_state.position
            else:
                pnl = (st.session_state.entry_price - curr['Close']) * st.session_state.position
            st.session_state.realized_pnl += pnl
            st.session_state.balance += pnl
            st.session_state.position = 0
            st.session_state.position_type = None
            st.session_state.entry_price = 0.0
            st.rerun()


# ==============================================================================
# BOTTOM STATUS BAR
# ==============================================================================
st.markdown(
    status_bar(
        balance=st.session_state.balance,
        realized_pnl=st.session_state.realized_pnl,
        unrealized_pnl=unrealized_pnl,
        position_type=st.session_state.position_type,
        position_size=st.session_state.position,
        cursor=st.session_state.cursor,
        total=max_idx,
    ),
    unsafe_allow_html=True,
)


# ==============================================================================
# AUTO-REPLAY ENGINE (unchanged logic)
# ==============================================================================
if st.session_state.is_playing:
    sleep_time = st.session_state.playback_speed / 1000.0
    time.sleep(max(0.01, sleep_time))

    if st.session_state.cursor < max_idx:
        st.session_state.cursor += 1
        st.rerun()
    else:
        st.session_state.is_playing = False
        st.rerun()
