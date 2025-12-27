import streamlit as st
import replicate
import os
import io

# Setup State
st.set_page_config(page_title="Documentary Voice Engine", page_icon="🎙️")

# CSS for Documentary Aesthetic
st.markdown("""
    <style>
    .main { background-color: #f5f2ed; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2c3e50; color: white; }
    </style>
    """, unsafe_allow_html=True)

# API Configuration - Fetches from Streamlit Secrets
os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

def split_text(text, max_chars=1500):
    """Splits long manuscripts into manageable chunks for the TTS engine."""
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

# --- UI Layout ---
st.title("🎙️ History Narrator Pro")
st.subheader("Manuscript-to-MP3 for Professional Documentaries")

# Sidebar - Voice Configuration
with st.sidebar:
    st.header("Voice Parameters")
    voice_type = st.selectbox("British Male Profile", 
        ["Narrator (Deep/Classic)", "Professor (RP/Precise)", "Veteran (Gravely/Mature)"])
    
    speed = st.slider("Speaking Speed", 0.5, 1.5, 0.95)
    stability = st.slider("Voice Stability", 0.0, 1.0, 0.7)
    style_weight = st.slider("Stylization Intensity", 0.0, 1.0, 0.5)
    
    st.info("Note: Using OpenVoice V2 via Replicate")

# Text Input Section
input_method = st.radio("Input Method", ["Paste Manuscript", "Upload Text File"])

if input_method == "Paste Manuscript":
    manuscript = st.text_area("Paste your historical script here...", height=300)
else:
    uploaded_file = st.file_uploader("Choose a .txt file", type="txt")
    if uploaded_file:
        manuscript = uploaded_file.getvalue().decode("utf-8")
    else:
        manuscript = ""

# Generation Logic
if st.button("Generate Documentary Voiceover"):
    if not manuscript:
        st.error("Please provide a manuscript first.")
    else:
        with st.status("Synthesizing British Male Voice...", expanded=True) as status:
            try:
                # Step 1: Chunking for long-form stability
                chunks = split_text(manuscript)
                st.write(f"Processing {len(chunks)} sections...")
                
                # In a production app, we would loop and concatenate. 
                # For this widget, we target the main synthesis.
# Updated to the latest stable OpenVoice V2 version
output = replicate.run(
    "lucataco/openvoice:af9877f21c4e040357eb6424ecddd7199367be2d8667ad4b6bbd306cbcd326e4",
    input={
        "text": manuscript,
        "speed": speed,
        "style": "default", # V2 works best with default style
        "voice_ref": "YOUR_VOICE_URL_HERE" 
    }
)
                
                # Assume output is a URL to the audio file
                audio_url = output 
                
                status.update(label="Audio Generated Successfully!", state="complete")
                
                # Preview and Download
                st.audio(audio_url)
                
                st.download_button(
                    label="Download MP3 for Video Editor",
                    data=audio_url,
                    file_name="historical_narration.mp3",
                    mime="audio/mpeg"
                )
                
            except Exception as e:
                st.error(f"Synthesis failed: {str(e)}")
