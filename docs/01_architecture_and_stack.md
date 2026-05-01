# PitchSense — Architecture & Tech Stack
> Half-Day Sprint · MVP v1.0 · Author: Antigravity AI

---

## 1. The Core Philosophy

PitchSense is not a dashboard. It is a **living room companion** — a co-host that listens, reacts, and speaks. Every architectural decision must serve one principle: **zero friction between the fan's emotion and the app's response.**

---

## 2. Final Tech Stack

### 2.1 Frontend / App Shell

| Tool | Version | Why |
|---|---|---|
| **Streamlit** | `≥ 1.35` | Stays. Fast iteration, Python-native. We will break its default aesthetic completely with injected CSS/JS. The `components.html` bridge is our escape hatch for raw HTML/CSS/JS islands. |
| **Custom CSS + JS (injected)** | Vanilla | Tailwind is a build-step overhead. We inject a complete design system via `st.markdown(..., unsafe_allow_html=True)` and `streamlit.components.v1.html()`. This gives us keyframe animations, CSS variables, and dynamic JS DOM manipulation — things Streamlit itself cannot do. |

### 2.2 Voice I/O Pipeline

| Tool | Version | Why |
|---|---|---|
| **`audio_recorder_streamlit`** | `≥ 0.0.8` | The only battle-tested, in-browser mic recorder that works inside Streamlit's iframe sandbox. Returns raw WAV bytes. **Free & open-source.** |
| **Gemini 2.0 Flash (Multimodal Audio)** | `google-genai ≥ 1.5` | Gemini's native audio understanding replaces Whisper entirely. We pass raw audio bytes directly in the multipart request. Eliminates a whole transcription step. **Free tier: 15 RPM, 1M tokens/day.** |
| **gTTS (Google Text-to-Speech)** | `≥ 2.5` | Takes the AI's text reply and produces an MP3 audio buffer. **100% free.** We pipe the buffer into Streamlit's `st.audio()` and auto-play it via a JS `audio.play()` injection. This closes the voice loop: Fan speaks → AI understands → AI speaks back. |

### 2.3 Live Data

| Tool | Version | Why |
|---|---|---|
| **CricAPI (cricapi.com/v1)** | REST | **Already integrated and battle-tested** in `cricket_api.py`. Free tier gives 100 calls/day (plenty for a demo with 90s caching). We are keeping `cricket_api.py` and `data_bridge.py` as-is. |
| **`mock_data.py`** | Local | Already exists. Critical for offline demos when API quota is exhausted. Phase 1 hardens this. |

### 2.4 AI Brain

| Tool | Version | Why |
|---|---|---|
| **Gemini 2.0 Flash** | `gemini-2.0-flash` | Already in `config.py`. The mega-prompt caching architecture in `agent_brain.py` is **brilliant and survives refactoring**. We extend it with new output keys: `vibe`, `roast`, `whatif`. |
| **JSON-mode responses** | `response_mime_type="application/json"` | Already implemented. Guarantees parse-safety. All new AI features use this. |

### 2.5 Reactive UI Mechanics

| Tool | Version | Why |
|---|---|---|
| **`streamlit-autorefresh`** | `≥ 0.0.1` | Triggers silent re-runs every 60s without user action. The game is *alive* even when the fan is just watching. **Free & lightweight.** |
| **CSS Custom Properties + JS** | Vanilla | The "Vibe System" works by setting `--vibe-color`, `--vibe-bg`, `--pulse-speed` CSS variables dynamically via `st.components.v1.html()`. Zero extra libraries. |
| **Lottie Animations** | `streamlit-lottie` | For the pressure gauge needle animation and celebration effects. Free Lottie JSON files from LottieFiles. |

### 2.6 Sound Effects

| Tool | Version | Why |
|---|---|---|
| **Injected `<audio>` HTML** | Native Browser API | We embed tiny base64-encoded SFX (crowd cheer, boundary horn) directly in the injected HTML. No server, no CDN. Just `new Audio(base64).play()` triggered from Python via `st.components.v1.html()`. |

---

## 3. Dropped Ideas (with reasons)

| Idea | Decision | Reason |
|---|---|---|
| Telegram Bot (`bot.py`) | **Removed from active path** | Scope conflict. Telegram is a separate runtime loop that complicates the Streamlit event model. Archived, not extended. |
| Chat Room (multi-user) | **Deferred to v2** | Requires a real-time backend (Firebase/Supabase). Half-day budget doesn't allow for auth + DB provisioning. |
| ML Win Probability | **Existing engine kept** | `win_probability.py` is a solid DLS-inspired rule-based model. No heavy ML overhead. |

---

## 4. Feature Priority Matrix

Scored on: **Impact** (wow-factor) × **Build speed** (inversely proportional to complexity).

| # | Feature | Impact | Build Time | MVP? |
|---|---|---|---|---|
| 1 | **Hey Pulse Voice Co-Host** (mic → Gemini audio → gTTS) | ⭐⭐⭐⭐⭐ | ~2h | ✅ YES |
| 2 | **Reactive Vibe UI** (CSS reacts to wickets/boundaries) | ⭐⭐⭐⭐⭐ | ~1.5h | ✅ YES |
| 3 | **Multiverse "What-If" Predictor** (already partially built!) | ⭐⭐⭐⭐ | ~30min | ✅ YES |
| 4 | **Roast / Hype Engine** (Hinglish banter button) | ⭐⭐⭐⭐ | ~20min | ✅ YES |
| 5 | **Dynamic Pressure Gauge** (animated dial, not a progress bar) | ⭐⭐⭐⭐ | ~45min | ✅ YES |
| 6 | **Dynamic Audio SFX** (crowd cheer on boundary) | ⭐⭐⭐ | ~30min | ✅ YES |
| 7 | **Auto Live-Refresh** (60s silent reload) | ⭐⭐⭐ | ~10min | ✅ YES |
| 8 | **Over-by-Over Worm Chart** (already exists, keep) | ⭐⭐⭐ | carry-over | ✅ YES |
| 9 | **Chat Room** (multi-user) | ⭐⭐⭐ | ~8h | ❌ v2 |

---

## 5. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER BROWSER (Streamlit)                     │
│                                                                 │
│   [MIC Button] ──► raw audio bytes (WAV)                       │
│                              │                                  │
│   [Auto-refresh 60s]         │                                  │
│         │                    ▼                                  │
│         │       ┌─────────────────────────┐                    │
│         │       │    VOICE PIPELINE       │                    │
│         │       │  audio_recorder_st      │                    │
│         │       │  → Gemini Audio API     │ ◄── STT + NLU      │
│         │       │  → gTTS MP3 buffer      │ ──► TTS Response   │
│         │       └─────────────────────────┘                    │
│         │                    │                                  │
│         ▼                    ▼                                  │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │               DATA BRIDGE LAYER                         │  │
│    │   data_bridge.py → cricket_api.py → CricAPI REST        │  │
│    │   [90s @st.cache_data TTL] + mock_data.py fallback      │  │
│    └────────────────────────┬────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │              AI BRAIN (agent_brain.py)                  │  │
│    │   Mega-Prompt → JSON {predict, coach, meme,             │  │
│    │                        vibe, roast, whatif}             │  │
│    │   90s cache per match_id → 0ms UI reads                 │  │
│    └────────────────────────┬────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │           VIBE ENGINE (vibe.py — NEW)                   │  │
│    │   Reads: run_rate, wicket_count, last_event             │  │
│    │   Emits: vibe_state = {color, bg, pulse, sfx, label}    │  │
│    └────────────────────────┬────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │              app.py  (PitchSense UI)                    │  │
│    │   Injects CSS variables from vibe_state                 │  │
│    │   Renders: Scoreboard · Pressure Gauge · Voice Panel    │  │
│    │            Roast Engine · What-If Sandbox · SFX Player  │  │
│    └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. New File Structure

```
d:\PitchSense\
│
├── app.py                  # REFACTORED — PitchSense UI entry point
├── agent_brain.py          # EXTENDED — new JSON keys: vibe, roast
├── cricket_api.py          # KEPT AS-IS — rock solid
├── data_bridge.py          # KEPT AS-IS
├── win_probability.py      # KEPT AS-IS
├── config.py               # MINOR UPDATE — new constants
├── mock_data.py            # KEPT AS-IS — hardened
│
├── vibe.py                 # NEW — Vibe state engine (pure logic)
├── voice.py                # NEW — Voice pipeline (record→Gemini→gTTS→play)
│
├── assets/
│   ├── sfx/
│   │   ├── boundary.b64    # Base64-encoded crowd cheer MP3
│   │   └── wicket.b64      # Base64-encoded dramatic sting MP3
│   └── lottie/
│       └── pressure.json   # Pressure gauge Lottie animation
│
├── docs/                   # THIS FOLDER
│   ├── 01_architecture_and_stack.md
│   ├── 02_execution_phases.md
│   └── 03_project_context.md
│
├── .env                    # KEEP — secrets
├── requirements.txt        # UPDATED
└── README.md               # UPDATE LAST
```

---

## 7. Updated `requirements.txt` (final)

```txt
# Core
streamlit>=1.35.0
python-dotenv>=1.0.0

# AI & Voice
google-genai>=1.5.0
gTTS>=2.5.0

# Data & Async
httpx>=0.27.0

# UI Enhancements
streamlit-autorefresh>=0.0.1
audio-recorder-streamlit>=0.0.8
streamlit-lottie>=0.0.5
requests>=2.31.0

# Utilities
pandas>=2.0.0
```

> **Dropped:** `python-telegram-bot` — the Telegram bot is archived, not part of this sprint.
