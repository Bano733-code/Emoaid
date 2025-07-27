# 🧠 EmoAid: The Gentle Chatbot for Sensitive Souls 💬

EmoAid is a multilingual, emotionally intelligent chatbot that supports users going through emotional 
distress. It understands sensitive emotions like loneliness, heartbreak, or anxiety and offers tailored responses 
like a kind friend, therapist, or motivator. Built with empathy at its core, EmoAid helps users express themselves 
through text or voice in English, Urdu, or Punjabi.

### 🏆 Submission for CS Girlies Hackathon 2025

---

## 🌟 Features

- 🗣️ **Voice Input & Output** – Speak your heart out and hear the bot’s comforting responses
- 🧠 **Emotion & Mood Detection** – Identifies moods such as sadness, breakup, anxiety, and more
- 🎭 **Personality Modes** – Choose from:  
  - Friendly Listener 🤗  
  - Therapist 🩺  
  - Motivator 💪  
  - Funny Friend 😂  
- 🌍 **Multilingual Support** – Communicate in **English**, **Urdu**, or **Punjabi**
- 📝 **Chat History Saving** – Log and review past emotional reflections
- 🤖 Powered by **Groq API** for real-time large language model (LLM) chat

---

## 🧰 Tech Stack

| Category             | Technology Used                    |
|----------------------|------------------------------------|
| Frontend             | Streamlit                          |
| Voice Recognition    | SpeechRecognition, Pyttsx3         |
| Translation          | Googletrans                        |
| AI Model             | Groq API (Mixtral-8x7B)            |
| Emotion Detection    | HuggingFace Sentiment Models       |
| Deployment           | Hugging Face Spaces (Streamlit)    |
| Platform             | Google Colab, GitHub               |

---

## 🚀 Run EmoAid Locally

#bash
git clone https://github.com/bano-733/emoaid.git
cd emoaid
pip install -r requirements.txt
streamlit run app.py

##Arcitecture Overview
Voice/Text Input → Whisper (Speech-to-Text)
↓
Translation (Urdu/Punjabi → English)
↓
Sentiment & Mood Tagging (HuggingFace)
↓
LLM (Groq API with Custom Prompting)
↓
Response (with Personality Mode)
↓
Output (Text + Voice + UI Display)

##Use Cases
Teenagers or students facing anxiety
Anyone struggling with emotional overwhelm
Daily emotional journaling & mental health check-ins

## Team & Contribution
| Member Name           | Contributions                                     |
| ---------------       | ------------------------------------------------- |
| Bano Rani (Leader)    | Voice-to-text, Groq API integration, Streamlit UI
|                       TTS, Voice Recorder, HuggingFace Deployment 
| Arooj Shehzadi        | Mood detection, Personality switch, Translation   |

🎯 Built for: CS Girlies Hackathon

## Future Enhancements
🧭 Daily Mood Tracker
🛋️ Therapist Mode Journaling
🤖 Telegram + WhatsApp Bot
📈 Mood Analytics Dashboard
