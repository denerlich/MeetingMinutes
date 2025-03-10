import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import io
import re

# Function to parse transcript robustly with expanded coverage
def parse_transcript(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    entries = []

    for entry in soup.find_all('div', class_='baseEntry-406'):
        speaker_tag = entry.find_previous('span', class_='itemDisplayName-419')
        timestamp_tag = entry.find('span', class_=['screenReaderFriendlyHiddenTag-360', 'baseTimestamp-415'])
        text_tag = entry.find('div', class_=['entryText-407', 'eventText-414'])

        speaker = speaker_tag.get_text(strip=True) if speaker_tag else "Unknown"
        timestamp = timestamp_tag.get_text(strip=True) if timestamp_tag else ""
        text = text_tag.get_text(strip=True) if text_tag else ""

        # Ensure we capture alternative timestamps
        if not timestamp:
            timestamp_search = re.search(r"\d+\sminutes?\s\d+\sseconds?", entry.get_text())
            if timestamp_search:
                timestamp = timestamp_search.group(0)

        entries.append({
            "Speaker": speaker,
            "Timestamp": timestamp,
            "Text": text
        })

    return pd.DataFrame(entries)

# Streamlit app UI
st.title("📄 HTML Transcript Analyzer - Enhanced")

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
