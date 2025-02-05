import os
import re
import json
import logging
import requests
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class OllamaClient:
    def __init__(self):
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "deepseek-coder:1.5b")

    def generate_stream(self, prompt):
        """Generate text using Ollama API with streaming"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True
                },
                stream=True,
                timeout=120  # Increased timeout to 2 minutes
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        json_response = json.loads(line)
                        if 'response' in json_response:
                            yield json_response['response']
                    except json.JSONDecodeError:
                        logging.error("Failed to decode JSON response")
                        continue

        except Exception as e:
            logging.error(f"Ollama API error: {str(e)}")
            yield None

def extract_keywords(text, num_keywords=5):
    """Extract main keywords from text"""
    words = re.findall(r'\w+', text.lower())
    common_words = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'}
    words = [word for word in words if word not in common_words and len(word) > 3]
    return [word for word, _ in Counter(words).most_common(num_keywords)]

def fallback_summary(transcript):
    """Generate a basic summary when Ollama is unavailable"""
    full_text = " ".join([entry['text'] for entry in transcript])
    keywords = extract_keywords(full_text)
    sentences = re.split(r'[.!?]+', full_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    sentence_scores = []
    for sentence in sentences:
        score = sum(1 for keyword in keywords if keyword in sentence.lower())
        sentence_scores.append((score, sentence))

    top_sentences = sorted(sentence_scores, reverse=True)[:3]

    summary = "# Summary\n\n"
    summary += "## Main Points\n"
    for _, sentence in top_sentences:
        summary += f"- {sentence}\n"

    summary += "\n## Key Keywords\n"
    summary += ", ".join(keywords).capitalize()

    summary += "\n\n## Brief Overview\n"
    summary += "This is an automated summary generated using keyword extraction and sentence ranking."

    return summary

def generate_summary(transcript):
    """Generate a summary of the transcript using Ollama, falling back to basic summarization if needed"""
    try:
        full_text = " ".join([entry['text'] for entry in transcript])

        # Create the prompt for the model
        prompt = """Please create a structured summary of the following text with:
1. Main Points (3-5 bullet points)
2. Key Takeaways
3. Brief Overview

Format the response in markdown.

Text to summarize:

{text}""".format(text=full_text)

        # Initialize Ollama client and generate summary
        ollama = OllamaClient()
        return ollama.generate_stream(prompt)

    except Exception as e:
        logging.warning(f"Summarization failed, using fallback: {str(e)}")
        return iter([fallback_summary(transcript)])