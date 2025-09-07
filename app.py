# app.py
import streamlit as st 
import requests
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import uuid
import base64
from streamlit_mic_recorder import mic_recorder

# ------------------- CONFIG -------------------
st.set_page_config(page_title="🌸 EmoAid: Chatbot for Sensitive Souls", layout="centered")

# ------------------- HELPERS -------------------
def get_groq_chat(user_input, personality, api_key):
    """Call Groq Chat API"""
    prompt = f"""
You are a {personality} for someone who's emotionally sensitive. 
Follow this structure in your response:

1. Start with a gentle and supportive reply (about 7 lines, empathetic and understanding).
2. Then provide exactly 3 short practical tips in bullet points.
3. End with a heartfelt encouragement based on the user's feeling and also give a quote according to feelings of user.

Keep language simple, caring, and maximum 15-25 lines in total.

User feeling/message: {user_input}
"""
#Respond to: {user_input}"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    if r.status_code == 200:
        data = r.json()
        return data["choices"][0].get("message", {}).get("content", "❌ No response")

    else:
        return f"❌ Chat error: {r.text}"


def get_groq_transcription(audio_path, api_key):
    """Call Groq Whisper API"""
    headers = {"Authorization": f"Bearer {api_key}"}
    with open(audio_path, "rb") as f:
        files = {"file": f}
        data = {"model": "whisper-large-v3"}
        r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers=headers, files=files, data=data)
    if r.status_code == 200:
        return r.json()["text"]
    else:
        return ""


def translate_text(text, target_lang):
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
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
api_key = st.secrets.get("GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ Groq API key not found. Please set it in secrets.toml or as an environment variable.")
language_codes = {
    "Afrikaans": "af",
    "Arabic": "ar",
    "Bengali": "bn",
    "Bosnian": "bs",
    "Catalan": "ca",
    "Czech": "cs",
    "Welsh": "cy",
    "Danish": "da",
    "German": "de",
    "Greek": "el",
    "English": "en",
    "Esperanto": "eo",
    "Spanish": "es",
    "Estonian": "et",
    "Finnish": "fi",
    "French": "fr",
    "Gujarati": "gu",
    "Hindi": "hi",
    "Croatian": "hr",
    "Hungarian": "hu",
    "Indonesian": "id",
    "Icelandic": "is",
    "Italian": "it",
    "Japanese": "ja",
    "Javanese": "jw",
    "Khmer": "km",
    "Kannada": "kn",
    "Korean": "ko",
    "Latin": "la",
    "Latvian": "lv",
    "Macedonian": "mk",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Myanmar (Burmese)": "my",
    "Nepali": "ne",
    "Dutch": "nl",
    "Norwegian": "no",
    "Punjabi": "pa",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Sinhala": "si",
    "Slovak": "sk",
    "Albanian": "sq",
    "Serbian": "sr",
    "Sundanese": "su",
    "Swedish": "sv",
    "Swahili": "sw",
    "Tamil": "ta",
    "Telugu": "te",
    "Thai": "th",
    "Filipino": "tl",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Vietnamese": "vi",
    "Chinese (Mandarin)": "zh-CN"
}
language = st.sidebar.selectbox("🌍 Language", list(language_codes.keys()))

personality = st.sidebar.radio("🎭 Personality Mode",
    ["Therapist", "Motivator", "Funny Friend","Wise Elder","Gentle Listener",
     "Romantic Poet", "Spiritual Guide","Empathetic Sister", "Tough Love Coach",
     "Stoic Philosopher", "Inner Child"])
speak = st.sidebar.checkbox("🔊 Enable Voice Response")

# ------------------- MAIN APP -------------------
st.title("🌸 EmoAid: Chatbot for Sensitive Souls")
st.markdown("Helping you feel heard, healed, and hopeful ✨")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------- VOICE INPUT -------------------
st.subheader("🎙️ Voice Input")

voice = mic_recorder(start_prompt="🎤 Record", stop_prompt="⏹️ Stop", just_once=True)

voice_text = ""
if voice:
    st.audio(voice['bytes'])  # playback recorded audio
    with open("temp.wav", "wb") as f:
        f.write(voice['bytes'])
    voice_text = get_groq_transcription("temp.wav", api_key)
    if voice_text:
        st.success(f"🎤 Voice captured: {voice_text}")
    else:
        st.warning("⚠️ Could not transcribe voice.")

# ------------------- USER INPUT -------------------
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if voice_text:
    st.session_state.user_input = voice_text

user_input = st.text_area("💬 Type your message here OR use your voice above",
                          value=st.session_state.user_input, height=100)

# ------------------- PROCESS -------------------
if st.button("Send") and user_input:
    st.session_state.chat_history.append(("You", user_input))
    if not api_key:
        st.warning("Please add your GROQ API key.")
    else:
        response = get_groq_chat(user_input, personality, api_key)
        target_lang_code = language_codes.get(language, "en")
        response_translated = response if language == "English" else translate_text(response, target_lang_code)

        mood_tag = detect_mood(user_input)
        st.session_state.chat_history.append(("EmoAid", f"{response_translated} \n\n💬 *Mood: {mood_tag}*"))

        if speak:
            speak_text(response_translated, lang=target_lang_code)

    st.session_state.user_input = ""

# ------------------- CHAT DISPLAY -------------------
st.markdown("---")
st.subheader("🕊️ Chat History")
for sender, message in st.session_state.chat_history[::-1]:
    role = "user" if "You" in sender else "assistant"
    with st.chat_message(role):
        st.markdown(f"**{sender}:** {message}")
