from googleapiclient.discovery import build
from transformers import pipeline
import csv
import re

API_KEY = "AIzaSyDgh-z4T0gc2EdqAPnfWqfNlA-ZFoMNisc"
MAX_COMMENTS = 100

# Load the advanced sentiment model once (CardiffNLP RoBERTa)
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

def get_video_id(url):
    """Extract the YouTube video ID from a URL."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def analyze_sentiment(comment):
    """Analyze sentiment using RoBERTa model."""
    try:
        result = sentiment_pipeline(comment[:512])[0]  # truncate long comments
        label = result['label']
        if "positive" in label.lower():
            return "Positive"
        elif "negative" in label.lower():
            return "Negative"
        else:
            return "Neutral"
    except Exception:
        return "Neutral"  # fallback


def build_dashboard(video_url):
    """Fetch comments, analyze sentiment, and build a dashboard dictionary."""
    VIDEO_ID = get_video_id(video_url)
    if not VIDEO_ID:
        return None, "Invalid YouTube URL!"

    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        comments = []
        next_page_token = None

        # Fetch comments
        while len(comments) < MAX_COMMENTS:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=VIDEO_ID,
                maxResults=min(100, MAX_COMMENTS - len(comments)),
                pageToken=next_page_token,
                textFormat="plainText"
            ).execute()

            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        # Sentiment analysis
        results = [(c, analyze_sentiment(c)) for c in comments]

        # Dashboard calculations
        positive_comments = [r for r in results if r[1] == "Positive"][:5]
        negative_comments = [r for r in results if r[1] == "Negative"][:5]
        neutral_comments = [r for r in results if r[1] == "Neutral"][:5]

        dashboard = {
            "total": len(results),
            "positive_count": len([r for r in results if r[1]=="Positive"]),
            "negative_count": len([r for r in results if r[1]=="Negative"]),
            "neutral_count": len([r for r in results if r[1]=="Neutral"]),
            "positive": positive_comments,
            "negative": negative_comments,
            "neutral": neutral_comments
        }

        # Optional: Save CSV
        with open("data/comments_sentiment.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Comment", "Sentiment"])
            writer.writerows(results)

        return dashboard, None

    except Exception as e:
        return None, str(e)
