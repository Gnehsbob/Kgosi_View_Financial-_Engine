# ==============================================================================
# config.py — Kgosi_View Theme
# ==============================================================================

THEME = {
    "BG":       "#0a0e14",
    "PANEL":    "#0f1923",
    "SURFACE":  "#131c28",
    "BORDER":   "#1c2936",
    "HOVER":    "#1e2d3d",
    "GREEN":    "#26a69a",
    "GREEN_DIM":"rgba(38,166,154,0.12)",
    "RED":      "#ef5350",
    "RED_DIM":  "rgba(239,83,80,0.12)",
    "TEXT":     "#d1d4dc",
    "DIM":      "#5d606b",
    "BLUE":     "#2962ff",
    "BLUE_DIM": "rgba(41,98,255,0.12)",
    "YELLOW":   "#ffb300",
    "PURPLE":   "#9c27b0",
    "CYAN":     "#00bcd4",
    "WHITE":    "#e8eaed",
}

# ──────────────────────────────────────────────────────────────────────────────
# MASTER CSS — Makes Streamlit look like a trading terminal
# ──────────────────────────────────────────────────────────────────────────────
CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

  .stApp {{
    background: {THEME['BG']};
    color: {THEME['TEXT']};
    font-family: 'Inter', -apple-system, sans-serif;
  }}
  header, .stApp > header {{ display:none !important; }}
  #MainMenu, footer, .stDeployButton {{ visibility:hidden !important; display:none !important; }}

  .block-container {{
    padding: 0.4rem 0.75rem 0.4rem 0.75rem !important;
    max-width: 100% !important;
  }}

  .stVerticalBlock > div {{ gap: 0.15rem !important; }}
  div[data-testid="stHorizontalBlock"] {{ gap: 0.35rem !important; align-items: center; }}

  .stSelectbox label, .stMultiSelect label, .stSlider label,
  .stNumberInput label {{ display: none !important; }}

  .stSelectbox > div > div {{
    background: {THEME['SURFACE']} !important;
    border: 1px solid {THEME['BORDER']} !important;
    border-radius: 6px !important;
    color: {THEME['TEXT']} !important;
    font-size: 0.8rem !important;
    min-height: 36px !important;
    font-weight: 600;
  }}
  .stSelectbox > div > div:hover {{
    border-color: {THEME['BLUE']} !important;
  }}

  .stMultiSelect > div > div {{
    background: {THEME['SURFACE']} !important;
    border: 1px solid {THEME['BORDER']} !important;
    border-radius: 6px !important;
    color: {THEME['TEXT']} !important;
    font-size: 0.78rem !important;
    min-height: 36px !important;
  }}
  .stMultiSelect span[data-baseweb="tag"] {{
    background: {THEME['BLUE_DIM']} !important;
    border: 1px solid {THEME['BLUE']} !important;
    color: {THEME['BLUE']} !important;
    border-radius: 4px !important;
    font-size: 0.72rem !important;
  }}

  .stNumberInput > div > div > input {{
    background: {THEME['SURFACE']} !important;
    border: 1px solid {THEME['BORDER']} !important;
    border-radius: 6px !important;
    color: {THEME['TEXT']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    text-align: center;
  }}
  .stNumberInput button {{
    background: {THEME['SURFACE']} !important;
    border: 1px solid {THEME['BORDER']} !important;
    color: {THEME['DIM']} !important;
  }}

  .stSlider > div > div > div > div {{
    background: {THEME['BLUE']} !important;
  }}
  .stSlider [data-baseweb="slider"] div[role="slider"] {{
    background: {THEME['BLUE']} !important;
    border: 2px solid {THEME['WHITE']} !important;
    width: 14px !important;
    height: 14px !important;
  }}
  .stSlider > div > div {{
    color: {THEME['DIM']} !important;
  }}

  .stButton > button {{
    background: {THEME['SURFACE']} !important;
    border: 1px solid {THEME['BORDER']} !important;
    border-radius: 6px !important;
    color: {THEME['TEXT']} !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    padding: 0.35rem 0.5rem !important;
    min-height: 36px !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
  }}
  .stButton > button:hover {{
    background: {THEME['HOVER']} !important;
    border-color: {THEME['BLUE']} !important;
  }}

  hr {{ border-color: {THEME['BORDER']} !important; margin: 0.3rem 0 !important; }}

  .stPlotlyChart {{
    border: 1px solid {THEME['BORDER']};
    border-radius: 8px;
    overflow: hidden;
  }}

  ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
  ::-webkit-scrollbar-track {{ background: {THEME['BG']}; }}
  ::-webkit-scrollbar-thumb {{ background: {THEME['BORDER']}; border-radius: 3px; }}

  [data-baseweb="popover"] {{
    background: {THEME['PANEL']} !important;
    border: 1px solid {THEME['BORDER']} !important;
  }}
  [data-baseweb="popover"] li {{
    color: {THEME['TEXT']} !important;
  }}
  [data-baseweb="popover"] li:hover {{
    background: {THEME['HOVER']} !important;
  }}

  .stDateInput label {{ display: none !important; }}
  .stDateInput > div > div > input {{
    background: {THEME['SURFACE']} !important;
    border: 1px solid {THEME['BORDER']} !important;
    border-radius: 6px !important;
    color: {THEME['TEXT']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    text-align: center;
    min-height: 36px !important;
  }}
  .stDateInput > div > div > input:focus {{
    border-color: {THEME['BLUE']} !important;
    box-shadow: 0 0 0 1px {THEME['BLUE']} !important;
  }}
  .stDateInput > div > div {{
    background: {THEME['SURFACE']} !important;
    border-radius: 6px !important;
  }}
  .stDateInput button {{
    color: {THEME['DIM']} !important;
  }}
  [data-baseweb="calendar"] {{
    background: {THEME['PANEL']} !important;
  }}
  [data-baseweb="calendar"] div {{
    color: {THEME['TEXT']} !important;
  }}
  [data-baseweb="calendar"] [aria-selected="true"] {{
    background: {THEME['BLUE']} !important;
  }}
</style>
"""

# ──────────────────────────────────────────────────────────────────────────────
# HTML COMPONENTS — all styles on single lines, no HTML comments
# ──────────────────────────────────────────────────────────────────────────────

def header_bar(symbol, timeframe, price, change_pct, is_playing):
    """Top bar: branding + live info, like FX Replay / TradeZella header."""
    status_color = THEME['GREEN'] if is_playing else THEME['DIM']
    status_text  = "REPLAYING" if is_playing else "PAUSED"
    price_str    = f"{price:,.5f}" if price < 10 else f"{price:,.2f}"
    chg_color    = THEME['GREEN'] if change_pct >= 0 else THEME['RED']
    chg_sign     = "+" if change_pct >= 0 else ""

    return (
        f'<div style="display:flex; align-items:center; justify-content:space-between; '
        f'background:{THEME["PANEL"]}; border:1px solid {THEME["BORDER"]}; '
        f'border-radius:8px; padding:8px 16px; margin-bottom:6px;">'

        # Left: Brand
        f'<div style="display:flex; align-items:center; gap:12px;">'
        f'<span style="font-size:1.05rem; font-weight:700; color:{THEME["WHITE"]}; letter-spacing:0.5px;">'
        f'KGOSI<span style="color:{THEME["BLUE"]}">_VIEW</span></span>'
        f'<span style="background:{THEME["SURFACE"]}; border:1px solid {THEME["BORDER"]}; '
        f'border-radius:4px; padding:2px 10px; font-size:0.78rem; color:{THEME["TEXT"]}; font-weight:600;">'
        f'{symbol}</span>'
        f'<span style="background:{THEME["SURFACE"]}; border:1px solid {THEME["BORDER"]}; '
        f'border-radius:4px; padding:2px 8px; font-size:0.72rem; color:{THEME["DIM"]}; font-weight:500;">'
        f'{timeframe}</span>'
        f'</div>'

        # Center: Price
        f'<div style="display:flex; align-items:baseline; gap:10px;">'
        f'<span style="font-family:JetBrains Mono,monospace; font-size:1.15rem; font-weight:700; color:{THEME["WHITE"]};">'
        f'{price_str}</span>'
        f'<span style="font-family:JetBrains Mono,monospace; font-size:0.78rem; font-weight:600; color:{chg_color};">'
        f'{chg_sign}{change_pct:.2f}%</span>'
        f'</div>'

        # Right: Status
        f'<div style="display:flex; align-items:center; gap:8px;">'
        f'<span style="width:7px; height:7px; border-radius:50%; background:{status_color}; '
        f'display:inline-block; box-shadow:0 0 6px {status_color};"></span>'
        f'<span style="font-size:0.7rem; font-weight:600; color:{status_color}; '
        f'letter-spacing:1px; text-transform:uppercase;">{status_text}</span>'
        f'</div>'

        f'</div>'
    )


def metric_card(label, value, color=None):
    """Compact metric tile for the bottom status bar."""
    c = color or THEME['TEXT']
    return (
        f'<div style="background:{THEME["SURFACE"]}; border:1px solid {THEME["BORDER"]}; '
        f'border-radius:6px; padding:6px 12px; text-align:center; min-width:110px;">'
        f'<div style="font-size:0.62rem; color:{THEME["DIM"]}; text-transform:uppercase; '
        f'letter-spacing:0.8px; margin-bottom:2px; font-weight:500;">{label}</div>'
        f'<div style="font-family:JetBrains Mono,monospace; font-size:0.88rem; '
        f'font-weight:700; color:{c};">{value}</div>'
        f'</div>'
    )


def status_bar(balance, realized_pnl, unrealized_pnl, position_type, position_size, cursor, total):
    """Bottom status bar like TradeZella / FX Replay."""
    pnl_color = THEME['GREEN'] if realized_pnl >= 0 else THEME['RED']
    upnl_color = THEME['GREEN'] if unrealized_pnl >= 0 else THEME['RED']
    pos_label = f"{position_type} {position_size:,}" if position_type else "FLAT"
    pos_color = THEME['GREEN'] if position_type == "LONG" else THEME['RED'] if position_type == "SHORT" else THEME['DIM']

    cards = (
        metric_card("Position", pos_label, pos_color)
        + metric_card("Account Balance", f"${balance:,.2f}")
        + metric_card("Realized PnL", f"${realized_pnl:,.2f}", pnl_color)
        + metric_card("Unrealized PnL", f"${unrealized_pnl:,.2f}", upnl_color)
    )

    return (
        f'<div style="display:flex; align-items:center; justify-content:space-between; '
        f'background:{THEME["PANEL"]}; border:1px solid {THEME["BORDER"]}; '
        f'border-radius:8px; padding:7px 14px; margin-top:4px; flex-wrap:wrap; gap:6px;">'
        f'<div style="display:flex; gap:8px; align-items:center;">{cards}</div>'
        f'<div style="font-family:JetBrains Mono,monospace; font-size:0.7rem; '
        f'color:{THEME["DIM"]}; letter-spacing:0.5px;">BAR {cursor} / {total}</div>'
        f'</div>'
    )


def playback_section_label(text):
    """Tiny label above a control group."""
    return (
        f'<div style="font-size:0.6rem; color:{THEME["DIM"]}; text-transform:uppercase; '
        f'letter-spacing:1px; margin-bottom:2px; text-align:center; font-weight:500;">{text}</div>'
    )


def section_divider(text):
    """Section divider label."""
    return (
        f'<div style="background:{THEME["PANEL"]}; border:1px solid {THEME["BORDER"]}; '
        f'border-radius:8px; padding:8px 14px; margin-bottom:4px; '
        f'display:flex; align-items:center; justify-content:center;">'
        f'<span style="font-size:0.65rem; color:{THEME["DIM"]}; letter-spacing:1.5px; '
        f'font-weight:600;">{text}</span></div>'
    )


# ──────────────────────────────────────────────────────────────────────────────
# CHART LAYOUT DEFAULTS
# ──────────────────────────────────────────────────────────────────────────────
CHART_LAYOUT = {
    'height': 560,
    'margin': dict(l=0, r=60, t=0, b=0),
    'paper_bgcolor': THEME['BG'],
    'plot_bgcolor': THEME['PANEL'],
    'xaxis_rangeslider_visible': False,
    'showlegend': False,
    'font': dict(family="Inter, sans-serif", size=10, color=THEME['DIM']),
    'hovermode': 'x unified',
    'hoverlabel': dict(
        bgcolor=THEME['SURFACE'],
        bordercolor=THEME['BORDER'],
        font=dict(family="JetBrains Mono", size=11, color=THEME['TEXT'])
    ),
    'xaxis': dict(
        gridcolor=THEME['BORDER'],
        gridwidth=1,
        griddash='dot',
        zeroline=False,
        showspikes=True,
        spikecolor=THEME['DIM'],
        spikethickness=0.5,
        spikemode='across',
        spikedash='dot',
        tickfont=dict(family="JetBrains Mono", size=9, color=THEME['DIM']),
    ),
    'yaxis': dict(
        gridcolor=THEME['BORDER'],
        gridwidth=1,
        griddash='dot',
        zeroline=False,
        side='right',
        showspikes=True,
        spikecolor=THEME['DIM'],
        spikethickness=0.5,
        spikemode='across',
        spikedash='dot',
        tickfont=dict(family="JetBrains Mono", size=10, color=THEME['DIM']),
    ),
    'dragmode': 'pan',
}