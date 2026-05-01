<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini_2.0-8E75B2?style=for-the-badge&logo=google-gemini&logoColor=white" />
</div>

<h1 align="center">🌀 PitchSense: Multiverse War Room</h1>

<p align="center">
  <strong>An AI-powered, Voice-Reactive Live Cricket Companion Dashboard.</strong><br>
  Built during a half-day Hackathon sprint.
</p>

---

## ⚡ Overview

**PitchSense** isn't just another cricket scoreboard—it's a reactive, immersive **War Room** for cricket fans. 

Powered by **Google's Gemini 2.0 Flash** and live data from **CricAPI**, PitchSense acts as your intelligent co-host. It doesn't just show you the score; it senses the momentum, recalculates win probabilities, generates tactical advice, simulates "What-If" alternate realities, and actually **talks to you** using multimodal AI voice.

## 🔥 Key Features

### 🎙️ Pulse: The AI Voice Co-Host
Tap the microphone and ask, *"Can MI chase this?"* or *"Who's bowling the next over?"* 
Pulse listens via `audio-recorder-streamlit`, streams the audio to Gemini for multimodal contextual analysis, and talks back to you via `gTTS` audio synthesis.

### 🎨 The Vibe Engine
The UI is physically connected to the match. The CSS background, glow effects, and primary colors actively morph based on the "vibe" of the game. If a wicket falls, the dashboard flashes red. If a boundary is hit, the UI celebrates.

### 🦋 Multiverse Sandbox (Timeline Simulator)
Ever wonder *"What if Dhoni walks in right now?"* Type your scenario into the Sandbox. The Gemini Agent analyzes the live ball-by-ball data and simulates the fallout of your alternate timeline. 

### 🧠 Mega-Prompt Caching Architecture
To bypass the strict rate limits of free-tier APIs, PitchSense uses a highly optimized **Disk + Memory Layered Cache** and a **Mega-Prompt architecture**. It generates the Tactical Coach, Match Predictor, and Hinglish Roast Banter all in a single API call, storing it locally to guarantee 0ms latency for the user.

### 🎯 Pressure Gauge & UI
- **Apple-style Glassmorphism**: Stunning, blur-backdrop CSS containers.
- **Dynamic SVG Pressure Gauge**: Live win-probability tracker that swings over by over.
- **Over Worm & Live Fan Chat**: Engage with the match ball-by-ball.

---

## 🏗️ Architecture Stack

- **Frontend**: Streamlit + Custom CSS + React UI Components (`audio-recorder-streamlit`)
- **AI Engine**: Google GenAI SDK (`gemini-2.0-flash`)
- **Data Pipeline**: CricAPI + Asyncio + `httpx`
- **Voice Synthesis**: Google Text-to-Speech (`gTTS`)
- **State Management**: Two-layer persistent cache (`.pitchsense_cache.json` + memory)

---

## 🚀 Quick Start Guide

### 1. Clone the Repo
```bash
git clone https://github.com/yourusername/PitchSense.git
cd PitchSense
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory:
```env
# Your API Keys
GEMINI_API_KEY=your_gemini_api_key_here
CRICKET_API_KEY=your_cricapi_key_here

# Set to 'true' if CricAPI runs out of free quota
MOCK_MODE=false
```

### 4. Boot the War Room
```bash
streamlit run app.py
```

---

## 🛠️ The "Offline" Fallback (Hackathon Safe)

APIs fail. Free tiers exhaust. Hackathon Wi-Fi drops. PitchSense is built to survive it all:
1. **Gemini Quota Exhaustion**: If Gemini hits a `429 RESOURCE_EXHAUSTED` error, the app gracefully degrades. The Voice module will intelligently mock an AI response and still read it aloud, keeping your demo alive.
2. **CricAPI Exhaustion**: If your 100/day call limit is hit, just flip `MOCK_MODE=true` in `.env`. PitchSense will instantly swap to a highly-detailed, mocked "MI vs RCB" match, complete with ball-by-ball arrays so the graphs and UI remain completely functional.

---

<p align="center">
  <i>Built with ❤️ and ☕ for the Hackathon</i>
</p>
