# app.py
import streamlit as st 
import requests
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import uuid
import base64
from streamlit_mic_recorder import mic_recorder
import tempfile
import torchaudio
from transformers import WhisperProcessor, WhisperForConditionalGeneration


# ------------------- CONFIG -------------------
st.set_page_config(page_title="EmoAid: Chatbot for Sensitive Souls", layout="centered")

# ------------------- HELPERS -------------------

def get_groq_response(user_input, personality, api_key):
    prompt = f"You are a {personality} for someone who's emotionally sensitive. Respond gently to: {user_input}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {response.text}"

def translate_text(text, target_lang):
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        return f"Translation error: {e}"

def detect_mood(text):
    keywords = {
        "loneliness": ["alone", "lonely", "isolated"],
        "breakup": ["breakup", "heartbroken", "relationship"],
        "anxiety": ["anxious", "nervous", "worried"],
        "sadness": ["sad", "depressed", "cry"],
        "anger": ["angry", "frustrated"]
    }
    text = text.lower()
    for mood, words in keywords.items():
        if any(word in text for word in words):
            return mood
    return "neutral"

def speak_text(text, lang="en"):
    filename = f"speech_{uuid.uuid4().hex}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    with open(filename, "rb") as audio_file:
        audio_bytes = audio_file.read()
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f'<audio autoplay controls><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    os.remove(filename)

# ------------------- SIDEBAR -------------------
st.sidebar.title("🧠 EmoAid Settings")
# Hide Groq API key - load from secrets or env variable
api_key = st.secrets.get("GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ Groq API key not found. Please set it in secrets.toml or as an environment variable.")

language = st.sidebar.selectbox("🌍 Language", ["English", "Urdu", "Punjabi","Korean","Bangoli","Hindi","Pahto","Balochi","French","Arabic","Chinese","Spanish","German"])
language_codes = {
    "English": "en",
    "Urdu": "ur",
    "Punjabi": "pa",
    "Korean": "ko",
    "Bangoli": "bn",
    "Hindi": "hi",
    "Pahto": "ps",
    "Balochi": "bal",
    "French": "fr",
    "Arabic": "ar",
    "Chinese": "zh-CN",
    "Spanish": "es",
    "German": "de"
}

personality = st.sidebar.selectbox("🎭 Personality Mode", ["Therapist", "Motivator", "Funny Friend",
    "Wise Elder", "Gentle Listener", "Romantic Poet",
    "Spiritual Guide", "Empathetic Sister", "Tough Love Coach",
    "Stoic Philosopher", "Inner Child"])
speak = st.sidebar.checkbox("🔊 Enable Voice Response")

# ------------------- MAIN APP -------------------
st.title("🩷 EmoAid: Chatbot for Sensitive Souls")
st.markdown("Helping you feel heard, healed, and hopeful ✨")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("🎙️ Voice Input (Multilingual)")
audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹️ Stop", just_once=True, key='voice')

# Load Whisper only once
@st.cache_resource
def load_whisper():
    processor = WhisperProcessor.from_pretrained("openai/whisper-small")
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
    return processor, model

processor, model = load_whisper()

voice_text = ""

if audio:
    st.audio(audio["bytes"], format="audio/wav")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        tmpfile.write(audio["bytes"])
        tmpfile_path = tmpfile.name

    # Transcribe
    audio_waveform, sr = torchaudio.load(tmpfile_path)

# Resample if sampling rate is not 16000
    if sr != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
        audio_waveform = resampler(audio_waveform)
        sr = 16000  # Update to new rate

    input_features = processor(audio_waveform.squeeze(), sampling_rate=sr, return_tensors="pt").input_features
    predicted_ids = model.generate(input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

    voice_text = transcription
    st.success(f"📝 You said: **{voice_text}**")

# Combine voice + text input
#user_input = st.text_area("💬 Type your message here OR use your voice above", value=voice_text, height=100)
# Store user input (text or voice) in session state
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# If voice input is available, override the input
if voice_text:
    st.session_state.user_input = voice_text

# Input box (editable by user after voice transcription too)
user_input = st.text_area("💬 Type your message here OR use your voice above", value=st.session_state.user_input, height=100)

if st.button("Send") and user_input:
    st.session_state.chat_history.append(("You", user_input))
    if not api_key:
        st.warning("Please add your GROQ API key.")
    else:
        response = get_groq_response(user_input, personality, api_key)

        target_lang_code = language_codes.get(language, "en")

        if language != "English":
            response_translated = translate_text(response, target_lang=target_lang_code)
        else:
            response_translated = response

        mood_tag = detect_mood(user_input)
        st.session_state.chat_history.append(("EmoAid", f"{response_translated} \n\n💬 *Mood Detected: {mood_tag}*"))
        if speak:
           speak_text(response_translated, lang=target_lang_code)

# ------------------- CHAT DISPLAY -------------------
st.markdown("---")
st.subheader("🕊️ Chat History")
for sender, message in st.session_state.chat_history[::-1]:
    with st.chat_message(sender): 
        st.markdown(message)
