"""
ui_styles.py  —  PitchSense global CSS + reusable HTML components
"""

GOOGLE_FONTS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
"""

GLOBAL_CSS = """
<style>
/* ── Fonts ─────────────────────────────────── */
* { box-sizing: border-box; }
.stApp, body {
    background-color: #0a0c12 !important;
    background-image: var(--vibe-bg) !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Ambient vibe glow ring ─────────────────── */
.stApp::after {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none; z-index: 9999;
    background: radial-gradient(ellipse at 50% -10%, var(--vibe-primary) 0%, transparent 55%);
    opacity: 0.07;
    animation: ambientPulse var(--pulse-speed) ease-in-out infinite alternate;
}
@keyframes ambientPulse { from { opacity: 0.05; } to { opacity: 0.14; } }

/* ── Streamlit containers → glass cards ─────── */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 18px !important;
    backdrop-filter: blur(16px) !important;
    transition: border-color 0.35s ease, box-shadow 0.35s ease, transform 0.25s ease !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    border-color: var(--vibe-primary) !important;
    box-shadow: 0 20px 50px rgba(0,0,0,0.55), 0 0 30px color-mix(in srgb, var(--vibe-primary) 25%, transparent) !important;
    transform: translateY(-3px) !important;
}

/* ── Typography ────────────────────────────── */
h1, h2, h3 {
    color: var(--vibe-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    text-shadow: 0 0 20px color-mix(in srgb, var(--vibe-primary) 40%, transparent);
}

/* ── Metrics ───────────────────────────────── */
[data-testid="stMetricValue"] {
    color: var(--vibe-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2rem !important;
    text-shadow: 0 0 10px color-mix(in srgb, var(--vibe-primary) 60%, transparent);
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.8rem !important; }
[data-testid="stMetricDelta"] { font-size: 0.75rem !important; }

/* ── Buttons ───────────────────────────────── */
.stButton > button {
    background: rgba(255,255,255,0.04) !important;
    color: var(--vibe-primary) !important;
    border: 1px solid var(--vibe-primary) !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background: var(--vibe-primary) !important;
    color: #000 !important;
    box-shadow: 0 0 20px color-mix(in srgb, var(--vibe-primary) 50%, transparent) !important;
    transform: translateY(-1px) !important;
}

/* ── Inputs ────────────────────────────────── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── Progress / Sliders ────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--vibe-glow), var(--vibe-primary)) !important;
}

/* ── Sidebar ────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(10,12,18,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── Vibe Banner ────────────────────────────── */
.pitch-banner {
    width: 100%; padding: 16px 24px; text-align: center;
    background: linear-gradient(135deg, var(--vibe-primary), var(--vibe-glow));
    color: #000; font-family: 'Space Grotesk', sans-serif;
    font-weight: 800; font-size: 1.4rem; letter-spacing: 1px;
    border-radius: 14px; margin-bottom: 20px;
    box-shadow: 0 0 40px color-mix(in srgb, var(--vibe-primary) 40%, transparent);
    animation: bannerIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes bannerIn { from { opacity: 0; transform: translateY(-18px) scale(0.97); } to { opacity: 1; transform: translateY(0) scale(1); } }

/* ── Stat Pill ──────────────────────────────── */
.stat-pill {
    display: inline-block; padding: 4px 12px;
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 999px; font-size: 0.78rem; color: #94a3b8;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Chat bubble ────────────────────────────── */
.chat-bubble {
    padding: 8px 14px; border-radius: 12px; margin-bottom: 6px;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
    font-size: 0.88rem;
}
.chat-bubble.you { border-color: var(--vibe-primary); background: color-mix(in srgb, var(--vibe-primary) 10%, transparent); }

/* ── Score row ──────────────────────────────── */
.score-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 14px; border-radius: 12px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace;
}
.score-team { font-size: 1rem; color: #94a3b8; }
.score-val  { font-size: 1.5rem; font-weight: 700; color: var(--vibe-primary); }
.score-meta { font-size: 0.75rem; color: #64748b; }

/* ── Ball badge ─────────────────────────────── */
.ball { display: inline-flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; border-radius: 50%;
    font-weight: 700; font-size: 0.8rem; margin: 3px;
    font-family: 'JetBrains Mono', monospace; }
.ball-W  { background: #ff1744; color: #fff; }
.ball-6  { background: #FFD700; color: #000; }
.ball-4  { background: #00e676; color: #000; }
.ball-0  { background: rgba(255,255,255,0.08); color: #64748b; }
.ball-N  { background: rgba(255,255,255,0.12); color: #e2e8f0; }

/* ── Hide autorefresh iframe ────────────────── */
iframe[title="streamlit_autorefresh.streamlit_autorefresh"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
</style>
"""


def gauge_html(batting_pct: int, bat: str, bwl: str, primary: str, glow: str) -> str:
    angle = -90 + (180 * batting_pct / 100)
    dashoffset = 251 - (251 * batting_pct / 100)
    return f"""
    <div style="display:flex;flex-direction:column;align-items:center;padding:10px 0;">
      <svg viewBox="0 0 220 120" width="100%" style="max-width:360px;">
        <!-- track -->
        <path d="M 20 105 A 90 90 0 0 1 200 105" fill="none"
              stroke="rgba(255,255,255,0.06)" stroke-width="18" stroke-linecap="round"/>
        <!-- danger zone (right = bowling wins) -->
        <path d="M 20 105 A 90 90 0 0 1 200 105" fill="none"
              stroke="rgba(255,71,87,0.15)" stroke-width="18" stroke-linecap="round"
              stroke-dasharray="283" stroke-dashoffset="141"/>
        <!-- value arc -->
        <path d="M 20 105 A 90 90 0 0 1 200 105" fill="none"
              stroke="{primary}" stroke-width="18" stroke-linecap="round"
              stroke-dasharray="283" stroke-dashoffset="{283 - (283 * batting_pct / 100)}"
              style="transition:stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1);
                     filter:drop-shadow(0 0 8px {glow});"/>
        <!-- needle -->
        <line x1="110" y1="105" x2="110" y2="30" stroke="#fff" stroke-width="3.5" stroke-linecap="round"
              style="transform-origin:110px 105px;
                     transform:rotate({angle}deg);
                     transition:transform 1.4s cubic-bezier(.4,0,.2,1);
                     filter:drop-shadow(0 0 4px #fff8);"/>
        <circle cx="110" cy="105" r="9" fill="{primary}"
                style="filter:drop-shadow(0 0 6px {glow});"/>
        <!-- percentage text -->
        <text x="110" y="80" text-anchor="middle" fill="{primary}"
              font-family="JetBrains Mono" font-size="18" font-weight="700">{batting_pct}%</text>
      </svg>
      <div style="display:flex;justify-content:space-between;width:90%;max-width:340px;
                  font-family:'Space Grotesk',sans-serif;font-weight:600;margin-top:6px;">
        <span style="color:#64748b;font-size:1rem;">{bwl}</span>
        <span style="color:{primary};font-size:1rem;">{bat}</span>
      </div>
    </div>"""


def ball_row_html(balls: list) -> str:
    COLORS = {"W": "ball-W", "6": "ball-6", "4": "ball-4", "0": "ball-0"}
    parts = []
    for b in balls[-12:]:
        cls = COLORS.get(str(b), "ball-N")
        parts.append(f'<span class="ball {cls}">{b}</span>')
    return f'<div style="display:flex;flex-wrap:wrap;gap:2px;margin-top:8px;">{"".join(parts)}</div>'


def score_card_html(inn: dict, label: str, active: bool, vibe_color: str) -> str:
    r   = inn.get("runs", "—")
    w   = inn.get("wickets", "—")
    ov  = inn.get("overs", "—")
    rr  = inn.get("run_rate", "—")
    nm  = inn.get("team_short", "?")
    border = f"border-color:{vibe_color};" if active else ""
    badge  = f'<span style="background:{vibe_color};color:#000;border-radius:6px;padding:2px 8px;font-size:0.7rem;font-weight:700;">LIVE</span>' if active else ""
    return f"""
    <div class="score-row" style="{border}">
      <div>
        <div class="score-team">{nm} {badge}</div>
        <div class="score-meta">{label}</div>
      </div>
      <div style="text-align:right;">
        <div class="score-val">{r}/{w}</div>
        <div class="score-meta">{ov} ov · RR {rr}</div>
      </div>
    </div>"""
