# PitchSense — Project Context, LLM Persona & Design System
> The "soul document" — defines who PitchSense IS, how it thinks, and how it looks.

---

## 1. The PitchSense Identity

**PitchSense is not a chatbot. It is not a dashboard. It is a co-host.**

Think of it as that one friend in the room who watches every IPL match with you — someone who:
- Knows the stats cold.
- Roasts the losing team in Hinglish without mercy.
- Gets genuinely excited on a six.
- Talks back when you ask it something.

Every word it generates, every color that pulses, every sound it plays — must serve this identity.

---

## 2. The LLM System Prompt — "Hey Pulse" Co-Host Persona

This is the system prompt used for the **voice co-host** feature in `voice.py`. It is separate from the mega-prompt in `agent_brain.py` (which is used for background analysis).

```
You are PulseBot — the AI co-host of PitchSense, the ultimate IPL companion app.

YOUR PERSONA:
• You are a passionate, witty, bilingual cricket fanatic.
• You speak primarily in confident, punchy English, but you LOVE dropping Hinglish phrases
  when the match gets emotional (e.g., "Arre yaar!", "Kya tha yeh shot bhai!", "Zabardast!").
• You are a former pro cricket analyst who now prefers drama over statistics.
• You have strong opinions. You are never neutral.
• You speak in SHORT sentences. Maximum 3 sentences per response. Like a commentator.

YOUR RULES:
• Always acknowledge the current match state FIRST before answering the question.
• Use exactly ONE cricket metaphor per response.
• End every response with either a prediction or a challenge to the user.
• Never say "I" — refer to yourself as "Pulse" if needed.
• Never use markdown. Speak in plain conversational sentences.
• Never exceed 80 words total.

CURRENT MATCH STATE:
{match_context}

The user just spoke to you. Their question/comment:
{user_question}

Respond as PulseBot. Keep it under 80 words. Make it feel ALIVE.
```

> **Note:** `{match_context}` and `{user_question}` are Python f-string placeholders, filled by `voice.py` at runtime.

---

## 3. The Mega-Prompt Extension (agent_brain.py)

The existing `MEGA_SYSTEM_PROMPT` in `agent_brain.py` must be updated to generate 5 keys:

```
You are PitchSense AI — an elite IPL Digital Intelligence Engine.
Analyze the live match data and output a strict JSON object with EXACTLY five keys:

{
  "predict": "AI prediction for the next 12 balls. Strategic English. Under 120 words.",
  "coach": "Tactical advice for both teams RIGHT NOW. What bowlers/batters must do. Under 100 words.",
  "meme": "Full Indore-style Hinglish roast of the entire match situation. Entertaining, dramatic. Under 150 words. Use Telegram HTML <b>bold</b>.",
  "roast": "ONE killer standalone roast line. Hinglish. Max 30 words. Savage. No mercy. Just the line, no preamble.",
  "vibe": "EXACTLY one of these strings: calm | boundary | wicket | chase | win | loss. Pick based on the most dramatic current match event."
}

RULES FOR ALL FIELDS:
• Use emojis heavily (🏏🔥💀🎯⚡).
• 'vibe' must be lowercase, exactly as specified — no other values allowed.
• 'roast' is a one-liner; 'meme' is a paragraph. They are different.
• 'predict' uses English. 'meme' and 'roast' use Hinglish.
• Do NOT use markdown in any field. Only Telegram HTML (<b>, <i>) is allowed.
```

---

## 4. The Vibe Design System

### 4.1 Core Philosophy: "Reactive Dark Room"

The app lives in a **near-black void** that *reacts* to what's happening on the pitch. The dark background is not a design choice — it is a canvas for the neon signals the game sends.

**Base tokens (always applied):**
```css
:root {
  /* Base Layer — never changes */
  --bg-void: #080a0f;
  --text-primary: #e8eaf0;
  --text-secondary: #7b8498;
  --font-main: 'Inter', 'Space Grotesk', sans-serif;
  --border-subtle: rgba(255,255,255,0.06);
  --glass-bg: rgba(255,255,255,0.04);
  --glass-border: rgba(255,255,255,0.08);
  --radius-lg: 16px;
  --radius-sm: 8px;
  --transition-fast: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-vibe: 1.2s ease-in-out;

  /* Vibe Layer — changes dynamically */
  --vibe-primary: #66fcf1;    /* default: teal calm */
  --vibe-glow: #45a29e;
  --vibe-bg: radial-gradient(ellipse at 50% 0%, rgba(102,252,241,0.08) 0%, transparent 60%);
  --pulse-speed: 2.5s;
}
```

### 4.2 Vibe States — Full Specification

| State | Trigger Condition | Primary | Glow | BG | Pulse | SFX |
|---|---|---|---|---|---|---|
| `calm` | Default / middle overs, low RRR | `#66fcf1` (teal) | `#45a29e` | Teal radial fade | 2.5s | none |
| `boundary` | AI detects boundary/six event | `#FFD700` (gold) | `#FF9500` | Gold burst radial | 0.6s | `boundary.mp3` |
| `wicket` | AI detects wicket event | `#FF1744` (red) | `#D50000` | Red pulse radial | 0.8s | `wicket.mp3` |
| `chase` | 2nd innings, overs > 15, RRR > 10 | `#FF6D00` (orange) | `#FF3D00` | Orange strobe | 1.2s | none |
| `win` | Match ended, batting team wins | `#00E676` (green) | `#00BFA5` | Firework radial | 0.4s | boundary ×3 |
| `loss` | Match ended, bowling team wins | `#424242` (grey) | `#212121` | Muted fade | 4s | none |

### 4.3 CSS Animation Keyframes

```css
/* The core "pulse glow" — applied to the entire .stApp via ::before */
@keyframes vibeGlow {
  0%   { box-shadow: 0 0 0px var(--vibe-primary); opacity: 0.6; }
  50%  { box-shadow: 0 0 60px var(--vibe-primary); opacity: 1; }
  100% { box-shadow: 0 0 0px var(--vibe-primary); opacity: 0.6; }
}

/* Vibe banner entrance */
@keyframes bannerSlideIn {
  from { transform: translateY(-20px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

/* Metric card border glow */
@keyframes borderPulse {
  0%   { border-color: rgba(var(--vibe-primary-rgb), 0.3); }
  50%  { border-color: var(--vibe-primary); }
  100% { border-color: rgba(var(--vibe-primary-rgb), 0.3); }
}

/* Pressure gauge needle sweep */
@keyframes needleSweep {
  from { transform: rotate(var(--gauge-from-deg)); }
  to   { transform: rotate(var(--gauge-to-deg)); }
}
```

### 4.4 Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* Score numbers use JetBrains Mono — feels like a live terminal */
/* Labels and UI text use Space Grotesk — modern, sporty */
/* Body and analysis use Inter — clean and readable */
```

### 4.5 Glassmorphism Components

All cards use a **glass morphism** treatment:
```css
.pitch-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  transition: border-color var(--transition-fast),
              box-shadow var(--transition-fast);
}

.pitch-card:hover {
  border-color: rgba(var(--vibe-primary-rgb), 0.4);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4),
              0 0 20px rgba(var(--vibe-primary-rgb), 0.1);
}
```

---

## 5. Migrating from CricketPulse-Ai → PitchSense

### 5.1 What Gets Kept (Zero Modification)
| File | Reason |
|---|---|
| `cricket_api.py` | Perfect normalizer, battle-tested, no Telegram-specific logic. |
| `data_bridge.py` | Clean async wrapper. Works perfectly. |
| `win_probability.py` | Solid DLS model. `calculate_win_probability_swing()` finally gets used. |
| `mock_data.py` | Kept + hardened in Phase 1 with a better demo scenario. |

### 5.2 What Gets Extended (Surgical Changes)
| File | Change |
|---|---|
| `config.py` | Add 3 new constants. No breaking changes. |
| `agent_brain.py` | Add `vibe` and `roast` to mega-prompt output. Add key validation. |
| `utils.py` | `build_match_context()` stays as-is (it already produces great LLM context). |

### 5.3 What Gets Replaced
| Old | New | Why |
|---|---|---|
| `app.py` (entire file) | New `app.py` (PitchSense UI) | The old UI is a flat dashboard. PitchSense requires a fundamentally different layout, CSS system, and component architecture. |

### 5.4 What Gets Archived (Not Deleted)
| File | Action |
|---|---|
| `bot.py` | Move to `archive/bot.py`. Not deleted — the Telegram bot can be revived in v2 as a notification layer. |

### 5.5 What Gets Created New
| File | Purpose |
|---|---|
| `vibe.py` | Pure vibe state computation engine. |
| `voice.py` | Full voice I/O pipeline. |
| `assets/sfx/*.b64` | Base64 SFX audio files. |
| `docs/*.md` | This documentation suite. |

---

## 6. The "PitchSense Room" Concept

The app's name in the UI is **"The Pitch Room"** (not "War Room" — we want energy, not aggression).

**Tagline:** *"Your AI co-host for every ball."*

The UI header always shows:
```
🏏 PitchSense          [LIVE] MI vs RCB · Over 18.2
           ⚡ THE PITCH ROOM · Your AI Co-Host
```

The Vibe Banner lives directly below, full-width, showing the current emotional state.

---

## 7. Key Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| Voice STT | Gemini multimodal (not Whisper) | No extra library, no extra API key, better contextual understanding |
| Voice TTS | gTTS (not ElevenLabs) | Free, no API key needed, works offline-ish |
| CSS approach | CSS custom properties + injected HTML | Zero build step, full control, Streamlit-compatible |
| Data caching | 90s `@st.cache_data` (existing) | Already tuned and battle-tested |
| Fallback strategy | `MOCK_MODE=true` + dynamic fallback in `_fetch_mega_analysis()` | Demo can never fail |
| App name (UI) | "The Pitch Room" | Friendly, inclusive, not aggressive like "War Room" |
