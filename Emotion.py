import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="Whisper to the Forgotten", page_icon="🕊️")
st.title("🕊️ Whisper to the Forgotten")
st.markdown("""
A soul-first AI app to help you speak for those who couldn't. 
Write on behalf of someone whose voice was never heard — a grandparent with dementia, a lost child, or a stranger who couldn’t write their story.
""")

# User inputs
person = st.text_input("Who are you writing on behalf of?", placeholder="e.g., My father who had Alzheimer's")
memory = st.text_area("What might they have wanted to say?", placeholder="e.g., He loved music, feared forgetting us...")
emotion_hint = st.selectbox("Pick the emotion you want to convey:", ["Hope", "Grief", "Joy", "Anger", "Longing"])

# Load model
@st.cache_resource
def load_model():
    return pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.1")

generator = load_model()

# Generate letter
if st.button("📝 Generate Letter"):
    if not person or not memory:
        st.warning("Please fill in both fields above.")
    else:
        prompt = f"You are a compassionate storyteller. Write a heartfelt message to the world from the perspective of {person}. It should express {emotion_hint.lower()} and be inspired by the memory: {memory}"

        with st.spinner("Writing from the heart..."):
            response = generator(prompt, max_new_tokens=250)[0]['generated_text']

        st.success("Here is their voice, reimagined:")
        st.write(response)

        # Download button
        st.download_button("📥 Download Letter", data=response, file_name="whisper_letter.txt")

        # Craiyon integration link
        st.markdown("---")
        st.markdown("### 🎨 Generate Emotional Art")
        art_prompt = f"{emotion_hint} abstract art representing the voice of {person}"
        craiyon_url = f"https://www.craiyon.com/?prompt={art_prompt.replace(' ', '%20')}"
        st.markdown(f"[Click to generate emotional art on Craiyon ↗️]({craiyon_url})")

st.markdown("---")
st.caption("Created for 'AI vs H.I.' Hackathon — blending empathy, memory, and artificial intelligence")
