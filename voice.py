"""
voice.py
────────
PitchSense Voice I/O Pipeline.
Fan speaks → Gemini understands (multimodal audio) → gTTS speaks back.
"""

import asyncio
import logging
from io import BytesIO

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, VOICE_LANGUAGE, VOICE_TLD

log = logging.getLogger(__name__)
client = genai.Client(api_key=GEMINI_API_KEY)

VOICE_SYSTEM_PROMPT = """You are PulseBot — the AI co-host of PitchSense, the ultimate IPL companion app.

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
• Never use markdown or HTML tags. Speak in plain conversational sentences.
• Never exceed 80 words total.
• Be entertaining and fun, not boring or robotic."""


async def transcribe_and_respond(
    audio_bytes: bytes,
    match_context: str,
    language: str = VOICE_LANGUAGE,
) -> tuple[str, bytes | None]:
    """
    Takes raw audio bytes from the mic, sends to Gemini multimodal,
    converts response to gTTS MP3.

    Returns: (ai_text_reply, mp3_audio_bytes_or_None)
    """
    # Build multimodal content: audio + text context
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
    context_part = types.Part(text=(
        f"Here is the current live cricket match state:\n{match_context}\n\n"
        "The user just spoke to you via their microphone. "
        "Listen to their audio and respond as PulseBot."
    ))

    try:
        resp = await client.aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=[types.Content(role="user", parts=[audio_part, context_part])],
            config=types.GenerateContentConfig(
                system_instruction=VOICE_SYSTEM_PROMPT,
                temperature=0.8,
            ),
        )
        ai_text = resp.text or "Pulse couldn't catch that — ask again, yaar!"
    except Exception as exc:
        err = str(exc)
        log.error("Voice transcription failed: %s", err)
        if "429" in err or "RESOURCE_EXHAUSTED" in err:
            ai_text = "Whoa, hold on! My Gemini quota just maxed out for the day! But looking at the match, it's getting intense out there. Switch to the text chat for now, yaar!"
        else:
            ai_text = "PulseBot hit a bouncer — the audio didn't come through clearly. Try speaking again!"

    # Convert text to speech via gTTS
    mp3_bytes = None
    try:
        from gtts import gTTS
        tts = gTTS(text=ai_text, lang=language, tld=VOICE_TLD)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        mp3_bytes = audio_buffer.read()
    except Exception as exc:
        log.error("gTTS failed: %s", exc)

    return ai_text, mp3_bytes


async def text_to_response(
    user_text: str,
    match_context: str,
) -> tuple[str, bytes | None]:
    """
    Text-based chat fallback (no mic). User types a question → AI responds + TTS.
    """
    prompt = (
        f"Here is the current live cricket match state:\n{match_context}\n\n"
        f"The user asks: {user_text}\n\n"
        "Respond as PulseBot."
    )

    try:
        resp = await client.aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=[types.Content(role="user", parts=[types.Part.from_text(prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=VOICE_SYSTEM_PROMPT,
                temperature=0.8,
            ),
        )
        ai_text = resp.text or "Pulse is speechless — that's a first!"
    except Exception as exc:
        err = str(exc)
        log.error("Text chat failed: %s", err)
        if "429" in err or "RESOURCE_EXHAUSTED" in err:
            ai_text = "Gemini quota hit — Pulse is taking a water break! We've run out of free-tier AI requests for the day."
        else:
            ai_text = "Pulse hit a technical snag. Check your internet connection!"

    # TTS
    mp3_bytes = None
    try:
        from gtts import gTTS
        tts = gTTS(text=ai_text, lang=VOICE_LANGUAGE, tld=VOICE_TLD)
        buf = BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        mp3_bytes = buf.read()
    except Exception as exc:
        log.error("gTTS failed: %s", exc)

    return ai_text, mp3_bytes
