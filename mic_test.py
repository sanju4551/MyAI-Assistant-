
import streamlit as st

st.title("MyAI - Microphone Test")

audio = st.audio_input("Click here to record your voice")

if audio:
    st.success("Recording received successfully!")
    st.audio(audio)
