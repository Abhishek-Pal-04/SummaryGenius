import os
import logging
from flask import Flask, render_template, request, jsonify
from services.youtube import get_video_transcript
from services.summarizer import generate_summary

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transcript', methods=['POST'])
def get_transcript():
    try:
        video_url = request.json.get('url')
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400

        transcript = get_video_transcript(video_url)
        if not transcript:
            return jsonify({'error': 'Could not fetch transcript'}), 404

        summary = generate_summary(transcript)
        
        return jsonify({
            'transcript': transcript,
            'summary': summary
        })
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500
