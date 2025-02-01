from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os

# initialize FastAPI app
app = FastAPI()

client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY"),
)
# input model
class TranscriptRequest(BaseModel):
    url: str

def extract_youtube_video_id(url: str):
    """extracts video ID from a youtube url"""

    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    """fetches transcript from youtube api"""

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t['text'] for t in transcript])
    except Exception:
        raise HTTPException(status_code=400, detail="Transcript not available for this video.")
    
def summarize_text(text: str):
    """uses openai api to generate summary and key takeaways"""
    # TODO limit input size?
    prompt = f"Summarize this transcript and generate key points and action items:\n{text}"
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )

    return response["choices"][0]["message"]["content"]

@app.post("/get_summary/")
def get_summary(request: TranscriptRequest):
    """API endpoint: accepts youtube url, fetches transcript, and summarizes."""
    video_id = extract_youtube_video_id(request.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL.")
    
    transcript = get_transcript(video_id)
    summary = summarize_text(transcript)

    return {"video_id": video_id, "summary": summary}