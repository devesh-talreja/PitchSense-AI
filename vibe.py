"""
vibe.py
───────
PitchSense Vibe State Engine.
Pure Python — no Streamlit dependency. Takes match data and an AI-detected vibe label,
returns a VibeState dict that drives the CSS / SFX / banner.
"""

from typing import TypedDict


class VibeState(TypedDict):
    label: str          # "calm" | "boundary" | "wicket" | "chase" | "win" | "loss"
    primary_color: str  # hex
    glow_color: str     # hex
    bg_gradient: str    # CSS gradient string
    pulse_speed: str    # CSS animation-duration e.g. "0.8s"
    sfx: str            # "boundary" | "wicket" | "none"
    emoji: str          # mood emoji
    banner: str         # short banner text


# ── Vibe presets ─────────────────────────────────────────────────
_VIBES: dict[str, VibeState] = {
    "calm": {
        "label": "calm",
        "primary_color": "#66fcf1",
        "glow_color": "#45a29e",
        "bg_gradient": "radial-gradient(ellipse at 50% 0%, rgba(102,252,241,0.06) 0%, transparent 60%)",
        "pulse_speed": "3s",
        "sfx": "none",
        "emoji": "🏏",
        "banner": "Match in progress — Stay sharp!",
    },
    "boundary": {
        "label": "boundary",
        "primary_color": "#FFD700",
        "glow_color": "#FF9500",
        "bg_gradient": "radial-gradient(ellipse at 50% 0%, rgba(255,215,0,0.10) 0%, transparent 55%)",
        "pulse_speed": "0.6s",
        "sfx": "boundary",
        "emoji": "🔥",
        "banner": "BOUNDARY! The crowd erupts!",
    },
    "wicket": {
        "label": "wicket",
        "primary_color": "#FF1744",
        "glow_color": "#D50000",
        "bg_gradient": "radial-gradient(ellipse at 50% 0%, rgba(255,23,68,0.10) 0%, transparent 55%)",
        "pulse_speed": "0.8s",
        "sfx": "wicket",
        "emoji": "💀",
        "banner": "WICKET! The game changes!",
    },
    "chase": {
        "label": "chase",
        "primary_color": "#FF6D00",
        "glow_color": "#FF3D00",
        "bg_gradient": "radial-gradient(ellipse at 50% 0%, rgba(255,109,0,0.10) 0%, transparent 55%)",
        "pulse_speed": "1.2s",
        "sfx": "none",
        "emoji": "⚡",
        "banner": "Run chase intensifies — Every ball counts!",
    },
    "win": {
        "label": "win",
        "primary_color": "#00E676",
        "glow_color": "#00BFA5",
        "bg_gradient": "radial-gradient(ellipse at 50% 0%, rgba(0,230,118,0.12) 0%, transparent 55%)",
        "pulse_speed": "0.4s",
        "sfx": "boundary",
        "emoji": "🏆",
        "banner": "MATCH WON! What a game!",
    },
    "loss": {
        "label": "loss",
        "primary_color": "#78909C",
        "glow_color": "#37474F",
        "bg_gradient": "radial-gradient(ellipse at 50% 0%, rgba(120,144,156,0.06) 0%, transparent 55%)",
        "pulse_speed": "4s",
        "sfx": "none",
        "emoji": "😔",
        "banner": "Match over. Better luck next time.",
    },
}


def compute_vibe(sc: dict, ai_vibe: str = "") -> VibeState:
    """
    Compute the current vibe state from match data + optional AI hint.
    Priority: explicit match events > AI hint > heuristic fallback.
    """
    i1 = sc.get("innings1") or {}
    i2 = sc.get("innings2") or {}
    match_ended = sc.get("match_ended", False)

    # 1. Match ended?
    if match_ended:
        status = (sc.get("status") or "").lower()
        if "won" in status:
            return _VIBES["win"]
        return _VIBES["loss"]

    # 2. AI gave us a vibe label?
    if ai_vibe in _VIBES:
        return _VIBES[ai_vibe]

    # 3. Heuristic: detect chase tension
    if i2 and i2.get("runs") is not None:
        rrr = float(i2.get("required_run_rate") or 0)
        overs = str(i2.get("overs", "0"))
        ov_float = float(overs.split(".")[0]) + float(overs.split(".")[1]) / 6 if "." in overs else float(overs)
        if rrr > 10 and ov_float > 15:
            return _VIBES["chase"]
        if rrr > 12:
            return _VIBES["chase"]

    # 4. Check last 5 overs for recent events
    last5 = sc.get("last_5_overs") or []
    if last5:
        latest = last5[-1]
        balls = latest.get("balls", [])
        if balls:
            last_ball = str(balls[-1])
            if last_ball == "W":
                return _VIBES["wicket"]
            if last_ball in ("4", "6"):
                return _VIBES["boundary"]

    return _VIBES["calm"]


def get_vibe_css(vibe: VibeState) -> str:
    """Generate dynamic CSS custom property overrides for the current vibe."""
    return f"""
    <style>
        :root {{
            --vibe-primary: {vibe['primary_color']};
            --vibe-glow: {vibe['glow_color']};
            --vibe-bg: {vibe['bg_gradient']};
            --pulse-speed: {vibe['pulse_speed']};
        }}
    </style>
    """
