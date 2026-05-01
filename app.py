"""
app.py — PitchSense: Multiverse War Room
MVP Final · Completed Voice + Full Dashboard
"""

import streamlit as st
import asyncio, sys, random
import pandas as pd

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import data_bridge, agent_brain, vibe, voice
import cricket_api as _capi
import ui_styles as ui
from config import MOCK_MODE
from win_probability import calculate_win_probability, calculate_win_probability_swing
from streamlit_autorefresh import st_autorefresh
from audio_recorder_streamlit import audio_recorder
from utils import build_match_context, generate_tactical_nudge

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="PitchSense · Multiverse War Room",
    layout="wide", page_icon="🌀",
    initial_sidebar_state="expanded",
)
st_autorefresh(interval=90_000, key="auto90s")

try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# ── Session state ────────────────────────────────────────────
_state_defaults = {
    "roasts": [],
    "voice_history": [],   # list of {"q": str, "a": str}
    "voice_mp3": None,
    "whatif_result": None,
    "chat_msgs": [
        {"user": "🤖 PulseBot",  "text": "War Room is OPEN. Who's dominating today? 🏏", "you": False},
        {"user": "👤 Fan_99",    "text": "RR batting first at Jaipur is dangerous 🔥", "you": False},
        {"user": "👤 Cricket22", "text": "DC needs early wickets or it's over 💀", "you": False},
    ],
    "game_score": 0, "game_streak": 0,
    "last_guess": None, "last_result": None,
    "predict_shown": False, "meme_shown": False,
    "coach_shown": True,
    "active_tab": "scoreboard",
}
for k, v in _state_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Data layer ────────────────────────────────────────────────
def sync_data():
    async def _f():
        matches = await data_bridge.get_live_matches()
        if not matches:
            return None, [], {}
        m = matches[0]
        for match in matches:
            name = match.get("match_name", "")
            short = match.get("short_name", "")
            if "Indian Premier League" in name or "IPL" in name or "RR vs DC" in short:
                m = match
                break
        mid   = m.get("match_id", "")
        sc    = await data_bridge.get_scorecard(mid) if mid else m
        last5 = await data_bridge.get_last_5_overs(mid) if mid else []
        ai    = await agent_brain.get_full_analysis()
        return sc, last5, ai
    return loop.run_until_complete(_f())

sc, last5, ai_data = sync_data()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌀 PitchSense")
    st.caption("Multiverse War Room · Powered by Gemini")
    st.divider()
    if MOCK_MODE:
        st.warning("📦 **Demo Mode** — MI vs RCB mock")
    elif _capi.quota_exceeded:
        st.error("🚫 CricAPI quota hit — enable MOCK_MODE")
    else:
        st.success("✅ Live — CricAPI connected")
    if sc:
        st.markdown(f"**{sc.get('short_name','—')}**")
        st.caption(sc.get("venue", "")[:45])
        st.caption(sc.get("status", "")[:60])
    st.divider()
    st.markdown("#### 🗺️ Dev Phases")
    st.markdown("✅ Phase 1 — Data + Cache\n\n✅ Phase 2 — AI Brain + Vibe\n\n✅ Phase 3 — UI Rebuild + Voice\n\n🔵 Phase 4 — Final MVP ← **HERE**")
    st.divider()
    st.caption("Disk+hot cache · ≤1 API call/90s")
    if st.button("🗑️ Force Resync", use_container_width=True):
        data_bridge.clear_cache()
        st.rerun()

if not sc:
    st.error("⚠️ No match data. Check connection or enable MOCK_MODE in .env")
    st.stop()

# ── Vibe engine ────────────────────────────────────────────────
room_vibe = vibe.compute_vibe(sc, ai_data.get("vibe", "calm"))
st.markdown(vibe.get_vibe_css(room_vibe), unsafe_allow_html=True)
st.markdown(ui.GOOGLE_FONTS + ui.GLOBAL_CSS, unsafe_allow_html=True)

# SFX toast on vibe change
if room_vibe["sfx"] != "none":
    st.toast(f"{room_vibe['emoji']} {room_vibe['banner']}", icon=room_vibe["emoji"])

# ── Pre-compute match data ─────────────────────────────────────
i1     = sc.get("innings1") or {}
i2     = sc.get("innings2") or {}
active = i2 if (i2 and i2.get("runs") is not None) else i1
team   = active.get("team_short", "BAT")
runs   = active.get("runs", 0)
wkts   = active.get("wickets", 0)
ovs    = active.get("overs", "0")
crr    = float(active.get("run_rate", 0) or 0)
is_chase = active is i2 and i2.get("target")
rrr    = i2.get("required_run_rate", "—") if is_chase else "—"
target = i2.get("target", 180) if is_chase else 180

try:
    wp      = calculate_win_probability(target, runs, wkts, ovs)
    bat_pct = int(wp["batting_team_pct"])
except Exception:
    bat_pct = 50

bat_name = active.get("team_short", "BAT")
bwl_name = (i1.get("team_short", "BWL") if active is i2 else "BWL")
context  = build_match_context(sc)

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
h1, h2 = st.columns([7, 2])
with h1:
    st.markdown("## 🌀 PitchSense — Multiverse War Room")
    st.caption(f"SATELLITE FEED · {sc.get('short_name','Match')} · {sc.get('venue','')[:42]}")
with h2:
    if st.button("🔄 Resync Stream", use_container_width=True):
        data_bridge.clear_cache()
        st.rerun()

st.markdown(
    f"<div class='pitch-banner'>{room_vibe['emoji']} {room_vibe['banner']}</div>",
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════
# FULL-WIDTH VOICE BAR — THE PULSE CO-HOST
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div style="background:linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));
            border:1px solid rgba(255,255,255,0.1);border-radius:20px;
            padding:20px 28px;margin-bottom:20px;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;
              font-weight:700;color:#e2e8f0;margin-bottom:4px;">
    🎙️ Pulse — Your AI Voice Co-Host
  </div>
  <div style="font-size:0.82rem;color:#64748b;">
    Tap the mic · Ask anything about the match · Pulse replies in real-time audio
  </div>
</div>
""", unsafe_allow_html=True)

v_mic, v_resp, v_hint = st.columns([1, 2.5, 1.5])

with v_mic:
    audio_bytes = audio_recorder(
        text="",
        recording_color="#FF1744",
        neutral_color=room_vibe["primary_color"],
        icon_name="microphone",
        icon_size="3x",
    )

with v_resp:
    if audio_bytes:
        with st.spinner("🎙️ Pulse is processing your question..."):
            ai_txt, mp3 = loop.run_until_complete(
                voice.transcribe_and_respond(audio_bytes, context)
            )
            st.session_state.voice_history.insert(0, {"q": "🎤 You spoke", "a": ai_txt})
            st.session_state.voice_history = st.session_state.voice_history[:3]
            st.session_state.voice_mp3 = mp3

    if st.session_state.voice_mp3:
        st.audio(st.session_state.voice_mp3, format="audio/mp3", autoplay=True)

    for entry in st.session_state.voice_history:
        st.markdown(f"""
<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
            border-left:3px solid {room_vibe['primary_color']};
            border-radius:12px;padding:10px 14px;margin-bottom:8px;font-size:0.9rem;">
  <div style="color:#64748b;font-size:0.75rem;margin-bottom:4px;">{entry['q']}</div>
  <div style="color:#e2e8f0;"><b style="color:{room_vibe['primary_color']};">Pulse:</b> {entry['a']}</div>
</div>""", unsafe_allow_html=True)

    if not st.session_state.voice_history:
        st.markdown(
            f"<div style='color:#475569;font-size:0.88rem;padding:10px;'>"
            f"Pulse is ready. Tap mic and ask: <i>\"Can MI chase this?\"</i> or <i>\"Who should bowl next?\"</i></div>",
            unsafe_allow_html=True
        )

with v_hint:
    # Text fallback input
    st.markdown("<div style='padding-top:6px;'>", unsafe_allow_html=True)
    txt_q = st.text_input("Or type your question:", placeholder="Who's in form?", label_visibility="collapsed")
    if st.button("Ask Pulse →", use_container_width=True):
        if txt_q:
            with st.spinner("Pulse thinking..."):
                ai_txt, mp3 = loop.run_until_complete(
                    voice.text_to_response(txt_q, context)
                )
                st.session_state.voice_history.insert(0, {"q": f"💬 {txt_q}", "a": ai_txt})
                st.session_state.voice_history = st.session_state.voice_history[:3]
                st.session_state.voice_mp3 = mp3
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# ROW 1 — SCOREBOARD + PRESSURE GAUGE
# ══════════════════════════════════════════════════════════════
r1a, r1b = st.columns([1.2, 1])

with r1a:
    with st.container(border=True):
        st.markdown("### 📡 Live Scoreboard")
        has_data = i1.get("runs") is not None or i2.get("runs") is not None
        if not has_data:
            st.info(f"⏳ **Waiting for first ball…**\n\n{sc.get('status','Toss done')}")
            if sc.get("toss"):
                st.caption(f"🪙 {sc['toss']}")
        else:
            if i1.get("runs") is not None:
                done1 = i1.get("wickets",0)==10 or str(i1.get("overs","0")).startswith("20")
                st.markdown(ui.score_card_html(i1, "1st Innings ✅" if done1 else "1st Innings 🏏", active is i1, room_vibe["primary_color"]), unsafe_allow_html=True)
            if i2.get("runs") is not None:
                st.markdown(ui.score_card_html(i2, "2nd Innings — Chasing 🏏", active is i2, room_vibe["primary_color"]), unsafe_allow_html=True)

            # Key metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Score", f"{runs}/{wkts}")
            m2.metric("Overs", ovs)
            m3.metric("Req RR" if is_chase else "Curr RR", str(rrr) if is_chase else f"{crr:.2f}")
            m4.metric("Target" if is_chase else "Projected", target)

            # Ball-by-ball stream
            all_balls = []
            for ov in last5:
                all_balls.extend(ov.get("balls", []))
            if all_balls:
                st.markdown("**Last deliveries:**")
                st.markdown(ui.ball_row_html(all_balls), unsafe_allow_html=True)

            # Fall of wickets
            fow = active.get("fall_of_wickets", [])
            if fow:
                with st.expander("📉 Fall of Wickets"):
                    st.caption("  ·  ".join(fow[:6]))

with r1b:
    with st.container(border=True):
        st.markdown("### 🎯 Momentum Gauge")
        st.markdown(
            ui.gauge_html(bat_pct, bat_name, bwl_name, room_vibe["primary_color"], room_vibe["glow_color"]),
            unsafe_allow_html=True,
        )
        try:
            sw = calculate_win_probability_swing(target, runs, wkts, ovs, last5)
            swing = sw.get("swing", 0)
            s1, s2 = st.columns(2)
            arrow = "▲" if swing > 0 else ("▼" if swing < 0 else "—")
            s1.metric(f"{bat_name} Win%", f"{bat_pct}%", f"{arrow} {abs(swing):.1f}% last 2 ov")
            s2.metric("Runs Needed" if is_chase else "Projected", str(i2.get("runs_needed","—")) if is_chase else str(target))
        except Exception:
            pass

    with st.container(border=True):
        st.markdown("### 📈 Over Worm")
        if last5:
            labels = [f"Ov {o.get('over','?')}" for o in last5]
            rvals  = [int(o.get("runs", 0)) for o in last5]
            df = pd.DataFrame({"Runs": rvals}, index=labels)
            st.bar_chart(df["Runs"], height=120, use_container_width=True)
        else:
            st.caption("Ball-by-ball data streams once play begins.")

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# ROW 2 — AI BRAIN (3 PANELS)
# ══════════════════════════════════════════════════════════════
ai_a, ai_b, ai_c = st.columns(3)

with ai_a:
    with st.container(border=True):
        st.markdown("### 🧠 Tactical Coach")
        nudge = generate_tactical_nudge(i2 if i2.get("runs") is not None else {}, i1)
        st.info(f"**Rule-based read:** {nudge}")
        if st.session_state.coach_shown:
            coach_txt = ai_data.get("coach", "Analyzing...")
            st.success(f"**Gemini Coach:** {coach_txt}")
        if st.button("Toggle AI Coach", use_container_width=True):
            st.session_state.coach_shown = not st.session_state.coach_shown
            st.rerun()

with ai_b:
    with st.container(border=True):
        st.markdown("### 🔮 AI Prediction")
        st.caption("Next 12 balls — what Gemini sees coming")
        if st.button("Reveal Forecast ⚡", use_container_width=True):
            st.session_state.predict_shown = not st.session_state.predict_shown
        if st.session_state.predict_shown:
            st.success(ai_data.get("predict", "Calculating..."))
        else:
            st.markdown("<div style='color:#475569;font-size:0.88rem;padding:8px;'>Click to reveal AI prediction for the next 12 balls.</div>", unsafe_allow_html=True)

with ai_c:
    with st.container(border=True):
        st.markdown("### 😂 Hinglish Banter")
        st.caption("Indore-style roast · powered by Gemini")
        if st.button("🔥 Generate Banter", use_container_width=True):
            st.session_state.meme_shown = True
            roast = ai_data.get("roast", "—")
            if roast not in st.session_state.roasts:
                st.session_state.roasts.insert(0, roast)
                st.session_state.roasts = st.session_state.roasts[:3]
        if st.session_state.meme_shown:
            st.warning(ai_data.get("meme", "Loading..."))
        for r in st.session_state.roasts:
            st.caption(f"💀 {r}")

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# ROW 3 — MATCHUP + WHAT-IF SANDBOX
# ══════════════════════════════════════════════════════════════
r3a, r3b = st.columns([1, 1.1])

with r3a:
    with st.container(border=True):
        st.markdown("### 🤺 Live Matchup")
        batters = [b for b in active.get("batsmen", []) if "batting*" in b.get("status", "")]
        if batters:
            bcols = st.columns(len(batters))
            for idx, b in enumerate(batters):
                sr = round(b.get("sr") or (b.get("runs",0)/max(b.get("balls",1),1)*100), 1)
                bcols[idx].metric(
                    f"🏏 {b['name'].split()[-1]}",
                    f"{b.get('runs',0)}* ({b.get('balls',0)}b)",
                    f"SR {sr}",
                    delta_color="off"
                )
        else:
            st.caption("Batting lineup loads once play begins.")

        bowlers_src = i2.get("bowlers",[]) if active is i2 else i1.get("bowlers",[])
        bowlers = sorted(bowlers_src, key=lambda x: (x.get("wickets",0), -float(x.get("economy",99))), reverse=True)
        if bowlers:
            bw = bowlers[0]
            st.metric(
                f"🎳 {bw['name'].split()[-1]} — Lead Bowler",
                f"{bw.get('wickets',0)}/{bw.get('runs',0)}",
                f"Eco {bw.get('economy',0)} · {bw.get('overs',0)} ov",
                delta_color="inverse"
            )
            if len(bowlers) > 1:
                bw2 = bowlers[1]
                st.caption(f"Also: {bw2['name']} {bw2.get('wickets',0)}/{bw2.get('runs',0)} eco {bw2.get('economy',0)}")

with r3b:
    with st.container(border=True):
        st.markdown("### 🦋 Multiverse Sandbox")
        st.caption("Fracture the timeline. Gemini simulates the alternate reality.")
        sim = st.text_input(
            "Scenario:", placeholder='What if Dhoni walks in right now?',
            label_visibility="collapsed", key="sim_input"
        )
        if st.button("⚡ Fracture the Timeline", use_container_width=True):
            if sim:
                with st.spinner("Simulating alternate reality…"):
                    async def _sim():
                        return await agent_brain.process_message(f"/simulate {sim}", "STRATEGY")
                    st.session_state.whatif_result = loop.run_until_complete(_sim())

        if st.session_state.whatif_result:
            st.success(st.session_state.whatif_result)
        else:
            st.markdown("<div style='color:#475569;font-size:0.85rem;padding:8px;'>Enter any \"What if\" scenario and watch Gemini rewrite the match.</div>", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# ROW 4 — MINI-GAME + LIVE FAN CHAT + COMING SOON
# ══════════════════════════════════════════════════════════════
r4a, r4b, r4c = st.columns([1, 1.2, 0.85])

with r4a:
    with st.container(border=True):
        st.markdown("### 🎲 Next-Ball Predictor")
        st.caption(f"**{st.session_state.game_score} pts** · Streak: **{st.session_state.game_streak}** 🔥")
        choices = ["Dot Ball 🟫", "Single 1️⃣", "Boundary 🟢", "SIX! 🟡", "WICKET! 🔴"]
        guess = st.selectbox("Predict next ball:", choices, label_visibility="collapsed")
        if st.button("🔒 Lock It In", use_container_width=True):
            outcome = random.choices(choices, weights=[30, 35, 20, 8, 7])[0]
            if outcome == guess:
                st.session_state.game_score  += 10 + st.session_state.game_streak * 2
                st.session_state.game_streak += 1
                st.session_state.last_result = f"✅ Correct! +{10+st.session_state.game_streak*2} pts · Streak {st.session_state.game_streak}🔥"
            else:
                st.session_state.last_result = f"❌ It was **{outcome}** · Streak reset"
                st.session_state.game_streak = 0
        if st.session_state.last_result:
            st.info(st.session_state.last_result)

with r4b:
    with st.container(border=True):
        st.markdown("### 💬 Fan Chat Room")
        st.caption("Chat with fans · Multi-user coming in v2 🚀")
        for msg in st.session_state.chat_msgs[-5:]:
            cls = "chat-bubble you" if msg.get("you") else "chat-bubble"
            st.markdown(
                f"<div class='{cls}'><b>{msg['user']}:</b> {msg['text']}</div>",
                unsafe_allow_html=True,
            )
        chat_in = st.chat_input("Join the hype...")
        if chat_in:
            st.session_state.chat_msgs.append({"user": "👤 You", "text": chat_in, "you": True})
            st.rerun()

with r4c:
    with st.container(border=True):
        st.markdown("### 🚀 Coming in v2")
        st.markdown(f"""
<div style='font-size:0.83rem;color:#94a3b8;line-height:2;'>
🌐 <b style='color:#e2e8f0;'>Global Fan Rooms</b><br>
&nbsp;&nbsp;&nbsp;Real-time multi-user chat<br>
📊 <b style='color:#e2e8f0;'>Player HeatMaps</b><br>
&nbsp;&nbsp;&nbsp;Shot zone overlays<br>
🏆 <b style='color:#e2e8f0;'>Fantasy AI Advisor</b><br>
&nbsp;&nbsp;&nbsp;Live DFS pick optimizer<br>
🔔 <b style='color:#e2e8f0;'>Push Alerts</b><br>
&nbsp;&nbsp;&nbsp;Wicket / boundary notify<br>
📡 <b style='color:#e2e8f0;'>Multi-Match Mode</b><br>
&nbsp;&nbsp;&nbsp;Watch 4 games at once<br>
🎮 <b style='color:#e2e8f0;'>Team Battle Mode</b><br>
&nbsp;&nbsp;&nbsp;Compete vs other fans
</div>""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#334155;font-size:0.75rem;padding:8px;'>"
    "🌀 PitchSense · Multiverse War Room · Built with Gemini 2.0 Flash + CricAPI · "
    "Half-Day Hackathon Sprint MVP · Phase 4 Complete"
    "</div>",
    unsafe_allow_html=True,
)
