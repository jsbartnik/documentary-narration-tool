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
                
                # Step 2: Running the 2025-Stable XTTS-v2 model
                # This ID is the current "Latest" stable release on Replicate.
                output = replicate.run(
                    "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
                    input={
                        "text": manuscript,
                        "speaker": "https://tvandradiovoices.com/wp-content/uploads/Mike_C_NarrationDemo.mp3",
                        "language": "en",
                        "cleanup_voice": True
                    }
                )
                
                status.update(label="Audio Generated Successfully!", state="complete")
                
                # Preview and Download
                st.audio(output)
                
                st.download_button(
                    label="Download MP3 for Video Editor",
                    data=output,
                    file_name="historical_narration.mp3",
                    mime="audio/mpeg"
                )
                
            except Exception as e:
                # This is the "except" block the error was asking for
                st.error(f"Synthesis failed: {str(e)}")
