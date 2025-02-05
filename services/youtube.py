from youtube_transcript_api import YouTubeTranscriptApi
import re
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    if not url:
        return None
    
    # Regular expressions for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/shorts\/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Parse URL for standard format
    parsed_url = urlparse(url)
    if parsed_url.netloc in ['www.youtube.com', 'youtube.com']:
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    
    return None

def get_video_transcript(url):
    """Fetch transcript for a YouTube video"""
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        formatted_transcript = []
        
        for entry in transcript_list:
            # Convert seconds to MM:SS format
            minutes = int(entry['start']) // 60
            seconds = int(entry['start']) % 60
            timestamp = f"{minutes:02d}:{seconds:02d}"
            
            formatted_transcript.append({
                'timestamp': timestamp,
                'text': entry['text'],
                'start': entry['start']
            })
        
        return formatted_transcript
    except Exception as e:
        raise Exception(f"Failed to fetch transcript: {str(e)}")
