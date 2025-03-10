import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import io
import re

# Function to parse transcript with enhanced heuristics
def parse_transcript(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    entries = []

    for entry in soup.find_all("div", class_=["baseEntry-406", "eventText-414", "entryText-407"]):
        # Identify speaker
        speaker_tag = entry.find_previous("div", class_=["speakerProfile-369"])
        speaker = speaker_tag.get_text(strip=True) if speaker_tag else "Unknown"

        # Identify timestamp
        timestamp_tag = entry.find("span", class_=["screenReaderFriendlyHiddenTag-360", "baseTimestamp-415"])
        timestamp = timestamp_tag.get_text(strip=True) if timestamp_tag else ""
        if not timestamp:
            timestamp_search = re.search(r"\d+\sminutes?\s\d+\sseconds?", entry.get_text())
            if timestamp_search:
                timestamp = timestamp_search.group(0)

        # Identify text content
        text_tag = entry.find("div", class_=["entryText-407", "eventText-414", "currentEntryText-408"])
        text = text_tag.get_text(strip=True) if text_tag else ""

        # Filter out metadata lines
        if "started transcription" in text.lower():
            continue

        entries.append({
            "Speaker": speaker,
            "Timestamp": timestamp,
            "Text": text
        })
    
    return pd.DataFrame(entries)

# Streamlit app UI
st.title("📄 HTML Transcript Analyzer - Fully Optimized")

uploaded_file = st.file_uploader("Choose your HTML or TXT transcript file", type=["html", "htm", "txt"])

if uploaded_file:
    try:
        html_content = uploaded_file.getvalue().decode('utf-8')
        transcript_df = parse_transcript(html_content)

        if transcript_df.empty:
            st.warning("⚠️ No data extracted. Please check the file structure.")
        else:
            st.subheader("📋 Transcript Preview")
            st.dataframe(transcript_df.head(50))

            # Excel download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                transcript_df.to_excel(writer, index=False, sheet_name='Transcript')

            st.download_button(
                label="📥 Download Transcript as Excel",
                data=buffer.getvalue(),
                file_name="transcript_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
