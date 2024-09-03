import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq
import re
import os

os.environ['GROQ_API_KEY'] = st.secrets['groq_api_key']


def extract_video_id(url):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        return video_id_match.group(1)
    return None

def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")
        return None

def analyze_text_with_groq(extracted_text):
    client = Groq()
    prompt = f"Summarize the following YouTube video transcript:\n\n{extracted_text}\n\nProvide a concise summary that captures the main points and key ideas discussed in the video."
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
            top_p=1,
            stream=True,
            stop=None,
        )
        summary = ""
        for chunk in completion:
            summary += chunk.choices[0].delta.content or ""
        return summary
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

st.title("YouTube Video Transcript Summarizer")

youtube_url = st.text_input("Enter YouTube Video URL:")

if st.button("Summarize"):
    if youtube_url:
        video_id = extract_video_id(youtube_url)
        if video_id:
            with st.spinner("Fetching transcript..."):
                transcript = get_youtube_transcript(video_id)
            
            if transcript:
                st.subheader("Transcript:")
                st.text_area("Full Transcript", transcript, height=200)
                
                with st.spinner("Generating summary..."):
                    summary = analyze_text_with_groq(transcript)
                
                if summary:
                    st.subheader("Summary:")
                    st.write(summary)
            else:
                st.error("Failed to fetch transcript. Please check the URL and try again.")
        else:
            st.error("Invalid YouTube URL. Please enter a valid URL.")
    else:
        st.warning("Please enter a YouTube URL.")