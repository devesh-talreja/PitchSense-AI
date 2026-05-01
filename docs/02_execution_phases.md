# PitchSense — Sprint Execution Phases
> Half-Day Sprint · 4 Phases · ~6 Hours Total

---

## Sprint Timeline Overview

```
[Phase 1] Foundation & Data Layer     ~60 min   [09:00 → 10:00]
[Phase 2] AI Brain & Vibe Engine      ~90 min   [10:00 → 11:30]
[Phase 3] Voice Co-Host + UI Polish   ~120 min  [11:30 → 13:30]
[Phase 4] SFX, QA & Demo Hardening   ~60 min   [13:30 → 14:30]
```

> ⚡ All times are relative to sprint start. Adjust to your actual clock.

---

## Phase 1 — Foundation & Data Layer
**Duration: ~60 min**
**Goal: The app runs, data flows, fallbacks work. Nothing breaks the demo.**

### Tasks

#### 1.1 Dependency Install
- [ ] Update `requirements.txt` with new packages (from `01_architecture_and_stack.md`).
- [ ] Run `pip install -r requirements.txt` and resolve any conflicts.

> 🔴 **HUMAN REQUIRED:** Approve and run the pip install command. Watch for errors on `audio-recorder-streamlit` (it has C-level dependencies on Windows — may need `pip install pyaudio` separately or a pre-built wheel).

#### 1.2 Config Update
- [ ] Add to `config.py`:
  - `AUTOREFRESH_INTERVAL = 60_000` (ms)
  - `VOICE_LANGUAGE = "en-in"` (Indian English for gTTS)
  - `SFX_ENABLED = True`

#### 1.3 Harden Mock Data
- [ ] Review `mock_data.py` — ensure it returns data in the **exact same shape** as `cricket_api.normalize_match()`.
- [ ] Add a `MOCK_MATCH_STATE` constant representing a tense chase scenario (e.g., 7 wickets down, 20 runs needed off 12 balls). This will be the default demo state.
- [ ] Update `data_bridge.py` to use `mock_data.py` when `MOCK_MODE=true` in `.env`.

> 🔴 **HUMAN REQUIRED:** Set `MOCK_MODE=true` in your `.env` during development. Switch to `false` only when you want real API data.

#### 1.4 Create New File Skeletons
- [ ] Create `vibe.py` with function signatures only (no logic yet).
- [ ] Create `voice.py` with function signatures only.
- [ ] Create `assets/sfx/` directory (files generated in Phase 3).

#### 1.5 Smoke Test
- [ ] Run `streamlit run app.py` — the OLD app should still render perfectly with `MOCK_MODE=true`.

**Exit Criteria:** `streamlit run app.py` loads, shows live (or mock) data, zero import errors.

---

## Phase 2 — AI Brain Extension & Vibe Engine
**Duration: ~90 min**
**Goal: The AI is smarter, the Vibe system is computed, the app has a soul.**

### Tasks

#### 2.1 Extend Mega-Prompt in `agent_brain.py`
- [ ] Add two new keys to `MEGA_SYSTEM_PROMPT` JSON schema:
  - `"vibe"`: One of `["calm", "boundary", "wicket", "chase", "win", "loss"]` — a machine-readable state for the CSS engine.
  - `"roast"`: A standalone, punchier Hinglish roast (30 words max). Separate from `"meme"` for targeted button use.
- [ ] Update `_fetch_mega_analysis()` to validate all 5 keys exist.
- [ ] Update the fallback dict to include `vibe` and `roast`.

#### 2.2 Build `vibe.py` — The State Engine
This module is **pure Python**, no Streamlit. It takes match data and AI vibe label → outputs a `VibeState` TypedDict.

```python
# vibe.py output contract
VibeState = TypedDict('VibeState', {
    'label': str,           # "boundary" | "wicket" | "chase" | "calm" | "win"
    'primary_color': str,   # hex e.g. "#ff3366"
    'glow_color': str,      # hex
    'bg_gradient': str,     # CSS gradient string
    'pulse_speed': str,     # CSS animation duration e.g. "0.8s"
    'sfx': str,             # "boundary" | "wicket" | "none"
    'emoji': str,           # "🔥" | "💀" | "⚡" | "😤"
    'banner': str,          # Short text e.g. "SIX! MAXWELL IS ON FIRE!"
})
```

- [ ] Implement `compute_vibe(sc: dict, ai_vibe: str) -> VibeState`:
  - **wicket**: `primary=#ff3366`, pulsing red, sfx=wicket, fast pulse.
  - **boundary**: `primary=#FFD700`, golden glow, sfx=boundary, fast pulse.
  - **chase** (last 5 overs, high RRR): `primary=#FF6B00`, orange urgent, medium pulse.
  - **calm**: `primary=#66fcf1`, teal glow (existing color), slow pulse.
  - **win/loss**: special full-screen overlays (handled in Phase 3).

#### 2.3 Implement `win_probability.py` Swing Display
- [ ] Wire `calculate_win_probability_swing()` into `app.py` (it already exists in `win_probability.py` but is unused!).
- [ ] This powers the **Pressure Gauge** in Phase 3.

#### 2.4 Integration Test
- [ ] Call `agent_brain._get_cached_analysis("vibe")` from a test script and verify the response.
- [ ] Call `compute_vibe()` with sample data and print the `VibeState`.

> 🔴 **HUMAN REQUIRED:** If Gemini returns a `vibe` key value that's not in the allowed list, the CSS engine will silently default to "calm". That's by design. Verify this doesn't happen with your real match data.

**Exit Criteria:** `compute_vibe()` returns correct states for wicket/boundary/chase scenarios.

---

## Phase 3 — Voice Co-Host + Full UI Rebuild
**Duration: ~120 min**
**Goal: PitchSense looks and feels like a professional product. The voice loop works.**

### Tasks

#### 3.1 Build `voice.py` — The Audio Pipeline

```python
# voice.py — public API
async def transcribe_and_respond(
    audio_bytes: bytes,
    match_context: str,
    language: str = "en-in"
) -> tuple[str, bytes]:
    """
    Returns: (ai_text_reply, mp3_audio_bytes)
    """
```

- [ ] Send `audio_bytes` to Gemini as a multipart audio Part (using `types.Part.from_bytes(data, mime_type="audio/wav")`).
- [ ] System prompt: use the PitchSense Co-Host persona from `03_project_context.md`.
- [ ] Pass `match_context` (from `utils.build_match_context()`) as a text Part alongside the audio.
- [ ] Parse text reply → pass to `gTTS(text, lang="en-in")` → write to `BytesIO` buffer.
- [ ] Return `(text, mp3_bytes)`.

> 🔴 **HUMAN REQUIRED:** Test microphone permissions in your browser. Chrome on Windows requires HTTPS or localhost. Streamlit's `localhost:8501` qualifies — but confirm the browser shows the microphone permission prompt when you first click the mic button.

#### 3.2 Full App Rebuild — `app.py`

The new app is a **single-page layout** with 5 zones:

```
┌─────────────────────────────────────────────────────┐
│  [HEADER] PitchSense + live team names + vibe banner│
├────────────────────────┬────────────────────────────┤
│  [LEFT PANEL]          │  [RIGHT PANEL]             │
│  • Scoreboard          │  • 🎤 Hey Pulse (Voice)    │
│  • Over worm chart     │  • 🔮 What-If Sandbox      │
│  • Fall of Wickets     │  • 😂 Roast Engine         │
├────────────────────────┴────────────────────────────┤
│  [BOTTOM FULL-WIDTH]                                │
│  • Pressure Gauge (animated dial)                   │
│  • AI Coach's Insight (scrolling text)              │
└─────────────────────────────────────────────────────┘
```

- [ ] **CSS Vibe Injection:** At the top of `app.py`, inject CSS custom properties from `VibeState`:
  ```python
  st.markdown(f"""<style>
    :root {{
      --vibe-primary: {vibe['primary_color']};
      --vibe-glow: {vibe['glow_color']};
      --vibe-bg: {vibe['bg_gradient']};
      --pulse-speed: {vibe['pulse_speed']};
    }}
  </style>""", unsafe_allow_html=True)
  ```
- [ ] **Vibe Banner:** Full-width animated banner under the header showing `vibe['banner']` + `vibe['emoji']`.
- [ ] **Hey Pulse Voice Panel:**
  - `audio_recorder_streamlit` component renders a mic button.
  - On audio capture: call `voice.transcribe_and_respond()`.
  - Show AI text reply in a styled chat bubble.
  - Play MP3 via `st.audio(mp3_bytes, format='audio/mp3', autoplay=True)`.
- [ ] **Pressure Gauge:** Replace the old `st.progress()` bar with a proper animated SVG arc gauge using injected HTML/SVG. The needle animates via CSS `transform: rotate()`.
- [ ] **What-If Sandbox:** Keep the existing text input, improve the output rendering.
- [ ] **Roast Engine:** Dedicated button that reads from `agent_brain._get_cached_analysis("roast")`.
- [ ] **Auto-refresh:** `streamlit_autorefresh(interval=60000, key="autorefresh")` at the top.

#### 3.3 Sound Effects
- [ ] Find/generate two tiny royalty-free MP3 SFX:
  - `boundary.mp3` — crowd cheer (2-3 seconds).
  - `wicket.mp3` — dramatic "out!" sting (2-3 seconds).
- [ ] Base64-encode both and store in `assets/sfx/boundary.b64` and `assets/sfx/wicket.b64`.
- [ ] In `app.py`, when `vibe['sfx'] != 'none'`, inject:
  ```html
  <script>
    const sfx = new Audio("data:audio/mp3;base64,{b64_data}");
    sfx.volume = 0.4;
    sfx.play();
  </script>
  ```

> 🔴 **HUMAN REQUIRED:**
> 1. Review the Pressure Gauge SVG visually — the needle rotation math needs real-data validation.
> 2. Review the Vibe Banner CSS animations — confirm they feel good at each state, not overwhelming.
> 3. Confirm the audio autoplay works in your browser (Chrome may block autoplay without user interaction — the SFX is fine since Vibe changes after a UI refresh which IS user-triggered).

**Exit Criteria:** The full UI renders beautifully. Voice button appears. Roast button generates text. The gauge animates. SFX play on boundary/wicket states.

---

## Phase 4 — QA, Demo Hardening & Handoff
**Duration: ~60 min**
**Goal: Nothing can break during a demo. The app is presentation-ready.**

### Tasks

#### 4.1 Error Boundary Audit
- [ ] Every API call wrapped in `try/except` with a graceful fallback message.
- [ ] `voice.py` — if Gemini audio fails, fall back to text-only response (no crash).
- [ ] SFX injection — wrapped in `try/except` to never crash the app.
- [ ] AI JSON parse — already uses `response_mime_type="application/json"`, but add key-existence checks for all 5 keys.

#### 4.2 MOCK_MODE Demo Scenario
- [ ] Create a **"perfect demo state"** in `mock_data.py`:
  - Match: MI vs RCB, over 18.2, MI batting, need 23 off 10 balls, 6 wickets down.
  - This state naturally triggers: `vibe=chase`, high RRR, dramatic pressure gauge.
- [ ] Confirm the Vibe Engine correctly outputs `chase` for this state.

#### 4.3 Performance Check
- [ ] Verify 90s cache TTL works — the second page load should be instant.
- [ ] Confirm `streamlit-autorefresh` doesn't cause flickering (set `debounce=True` if available).

#### 4.4 Requirements Lock
- [ ] Run `pip freeze > requirements_locked.txt` to capture exact versions.
- [ ] Test clean install: `pip install -r requirements.txt` in a fresh venv.

> 🔴 **HUMAN REQUIRED:**
> 1. **Get API Keys (if not already done):**
>    - CricAPI: [cricapi.com](https://cricapi.com) → Sign up → free 100 calls/day key.
>    - Gemini: [aistudio.google.com](https://aistudio.google.com) → Get API Key (free tier).
> 2. **Final `.env` check:** Confirm `.env` has `GEMINI_API_KEY`, `CRICKET_API_KEY`, `MOCK_MODE=false`.
> 3. **Browser test (full flow):**
>    - Load `localhost:8501`.
>    - Click mic, ask "Who is winning?" → Hear AI voice reply.
>    - Click Roast → See Hinglish roast text.
>    - Click What-If → Type "What if Dhoni bats now?" → See AI prediction.
>    - Confirm Vibe Banner changes color between page refreshes.
> 4. **Screenshot** the app for the README.

#### 4.5 README Update
- [ ] Update `README.md` with: new features list, updated install instructions, screenshot.

**Exit Criteria:** App runs end-to-end with real API data. All 3 main features (voice, roast, what-if) demonstrably work. No unhandled exceptions in 10 minutes of use.

---

## Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| `audio-recorder-streamlit` won't install on Windows | Medium | Pre-install `pyaudio` wheel from [gohlke wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/) |
| Gemini audio API returns error on WAV format | Low | Convert WAV → FLAC using `pydub` before sending |
| Browser blocks mic permission | Low | Use Chrome, accept the prompt; test on `localhost` |
| CricAPI 100-call limit hit during demo | Medium | Use `MOCK_MODE=true` — the demo state is always dramatic |
| `gTTS` network timeout | Low | Wrap in try/except; show text-only response as fallback |
| Autorefresh causes infinite API loop | Low | `@st.cache_data(ttl=90)` prevents redundant calls |
