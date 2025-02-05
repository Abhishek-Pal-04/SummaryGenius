import os
import logging
import json
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
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

        # Get transcript and video info
        result = get_video_transcript(video_url)
        if not result['transcript']:
            return jsonify({'error': 'Could not fetch transcript'}), 404

        # Start streaming the summary
        def generate():
            try:
                for chunk in generate_summary(result['transcript']):
                    if chunk:
                        yield f"data: {json.dumps({'type': 'summary', 'content': chunk})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

            # Send video info at the end
            yield f"data: {json.dumps({'type': 'video_info', 'content': result['video_info']})}\n\n"
            yield f"data: {json.dumps({'type': 'transcript', 'content': result['transcript']})}\n\n"
            yield "data: {\"type\": \"done\"}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500