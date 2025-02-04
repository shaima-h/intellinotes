from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# origins = [
#     "http://127.0.0.1:5500/",
#     "http://127.0.0.1:8000",
#     "http://localhost",
#     "http://localhost:8000",
#     "http://localhost:8080",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['*'],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY"),
)

# input model
class SummarizeRequest(BaseModel):
    url: str

def get_video_title(url: str):
    """gets video title from youtube url"""

    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")

    link = soup.find_all(name="title")[0]
    title = str(link)
    title = title.replace("<title>","")
    title = title.replace("</title>","")

    return title

def extract_youtube_video_id(url: str):
    """extracts video ID from youtube url"""

    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    """fetches transcript from youtube api"""
    try:
        # transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies={"https": "http://127.0.0.1:8000"})
        return " ".join([t['text'] for t in transcript])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Transcript not available for this video. Error: {str(e)}")
    
def summarize_text(text: str):
    """uses openai api to generate summary and key takeaways"""
    prompt = f"Summarize this and generate key points and action items:\n{text}"
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )

    print(response)
    return response.choices[0].message.content

# router = APIRouter()

@app.post('/get_summary/')
async def get_summary(request: SummarizeRequest):
    # """API endpoint: accepts youtube url, fetches transcript, and summarizes."""

    print(request)
    video_title = get_video_title(request.url)
    print(video_title)

    video_id = extract_youtube_video_id(request.url)
    print(video_id)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL.")
    
    transcript = get_transcript(video_id)
    summary = summarize_text(transcript)
    # summary = "**Summary of the Transcript:**\n\nThe speaker welcomes attendees, both regulars and newcomers, to a session focused on spiritual growth and the avoidance of hypocrisy. The session involves reading from a text about seeking closeness to Allah and includes a Q&A segment. The main theme revolves around protecting one’s progress towards spiritual growth by avoiding hypocrisy, as hypocrisy can negate forward motion. The speaker discusses the importance of spiritual hygiene, which includes recognizing hypocrisy, valuing the truth, surrounding oneself with morally intelligent individuals, and engaging in self-reflection. Additionally, the speaker addresses the influence of social interactions on spiritual growth, emphasizing the need to be around people who remind one of Allah and inspire goodness. Other points touched on include being open to embracing truth despite discomfort and ensuring actions and claims are consistent with one's faith.\n\n**Key Points:**\n\n1. **Welcoming Participants**: The community is invited for reading and Q&A on spiritual guidance. \n\n2. **Hypocrisy**: Identified as a significant deterrent to spiritual growth; it involves a discrepancy between one's internal beliefs and external actions.\n\n3. **Positive Companionship**: Encouraged to seek the company of morally intelligent and God-conscious individuals to aid spiritual development.\n\n4. **Embracing Truth**: Importance of humility in accepting and acting upon the truth to foster personal growth.\n\n5. **Character Development**: Need for congruence between speech, actions, and religious tenets; highlighted through the example of not lying, gentle speech, and authenticity.\n\n6. **Community Influence**: Acknowledges the effect of friends and community in shaping behaviors and attitudes.\n\n7. **Parental Influence on Marriage**: Discussed challenges related to parental opposition in marriages across cultural lines.\n\n8. **Struggles and Self-improvement**: Participants are advised on reconciling personal struggles, like music and commitment to prayer, with spiritual aspirations.\n\n9. **Cultural Sensitivity in Relations**: Navigating family and cultural expectations, especially concerning marriage diversity.\n\n10. **Approaching Events with Mixed Elements (e.g., Music)**: Encouraged thoughtful engagement rather than outright rejection, emphasizing maintaining relationships while upholding personal spiritual standards.\n\n**Action Items:**\n\n1. **Participate in Q&A**: Engage with the Q&A segment to address personal queries on spirituality.\n\n2. **Reflect on Personal Actions**: Assess personal consistency in claims of faith and actual behavior.\n\n3. **Seek Positive Company**: Intentionally spend time with those who possess admirable traits in character and spirituality.\n\n4. **Open to Growth**: Embrace teachings from Allah and the Prophet without resistance, even if it means confronting personal shortcomings.\n\n5. **Balance Personal and Communal Obligations**: Attend events selectively while preserving relationships and spiritual integrity.\n\n6. **Engage with Truth**: Actively reflect on your receptivity to truth and consider areas of improvement.\n\n7. **Evaluate Personal Challenges**: Acknowledge personal struggles and work on finding replacements or solutions grounded in faith.\n\n8. **Embrace Diversity**: Balance cultural and religious factors in personal and familial decisions regarding marriage.\n\n9. **Contribute to Community Well-being**: Support others in their journey toward spiritual growth, including conversions and life milestones.\n\n10. **Assist at Events**: Help organize and clear venues post-event as a way of community service."

    return {"video_title": video_title, "video_id": video_id, "summary": summary}


@app.get("/")
async def root():
    return {"message": "FastAPI is running on Render!"}
