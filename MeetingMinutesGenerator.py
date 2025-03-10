import tkinter as tk
from tkinter import filedialog, messagebox
from bs4 import BeautifulSoup
import pandas as pd
import os

def parse_transcript(html_file):
    with open(html_file, "r", encoding='utf-8') as file:
        soup = BeautifulSoup(file, "html.parser")

    entries = []
    for entry in soup.find_all('div', class_='baseEntry-443'):
        speaker_tag = entry.find_previous('span', class_='itemDisplayName-456')
        timestamp_tag = entry.find('span', class_='screenReaderFriendlyHiddenTag-397')
        text_tag = entry.find('div', class_='entryText-444')
        
        speaker = speaker_tag.get_text(strip=True) if speaker_tag else 'Unknown'
        timestamp = timestamp_tag.get_text(strip=True) if timestamp_tag else ""
        text = text_tag.get_text(strip=True) if text_tag else ""

        yield {"Speaker": speaker, "Timestamp": timestamp, "Text": text_tag.get_text(strip=True)}

    
def process_file():
    file_path = filedialog.askopenfilename(filetypes=[("HTML files", "*.html;*.htm;*.txt")])
    if file_path:
        try:
            transcript_data = list(parse_transcript(file_path))
            df = pd.DataFrame(transcript_data)
            output_path = os.path.splitext(file_path)[0] + '_transcript.xlsx'
            transcript_df = pd.DataFrame(transcript_data)

            # Additional analysis can be added here, such as NLP tasks for sentiment analysis, mentioned documents, etc.
            transcript_data_df = pd.DataFrame(transcript_data)
            transcript_data_df.to_excel(output_filename := file_path.replace('.html', '_transcript.xlsx').replace('.txt', '_transcript.xlsx'), index=False)
            messagebox.showinfo("Success", f"Transcript extracted successfully and saved as {output_filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process the file: {e}")

root = tk.Tk()
root.title("HTML Transcript Extractor")
root.geometry("300x100")

btn = tk.Button(root, text="Select HTML Transcript", command=process_file)
btn.pack(expand=True)

root.mainloop()
