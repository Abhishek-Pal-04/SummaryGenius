import os
import re
from collections import Counter
from openai import OpenAI
import logging

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def extract_keywords(text, num_keywords=5):
    """Extract main keywords from text"""
    # Remove common words and symbols
    words = re.findall(r'\w+', text.lower())
    common_words = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'}
    words = [word for word in words if word not in common_words and len(word) > 3]
    return [word for word, _ in Counter(words).most_common(num_keywords)]

def fallback_summary(transcript):
    """Generate a basic summary when OpenAI is unavailable"""
    # Combine all text
    full_text = " ".join([entry['text'] for entry in transcript])

    # Extract keywords
    keywords = extract_keywords(full_text)

    # Split into sentences
    sentences = re.split(r'[.!?]+', full_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    # Score sentences based on keyword presence
    sentence_scores = []
    for sentence in sentences:
        score = sum(1 for keyword in keywords if keyword in sentence.lower())
        sentence_scores.append((score, sentence))

    # Select top sentences
    top_sentences = sorted(sentence_scores, reverse=True)[:3]

    # Format the summary
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
    """Generate a summary of the transcript, falling back to basic summarization if OpenAI fails"""
    try:
        # Try OpenAI first
        full_text = " ".join([entry['text'] for entry in transcript])
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert summarizer. Create a structured summary with: "
                    "1. Main Points (3-5 bullet points) "
                    "2. Key Takeaways "
                    "3. Brief Overview "
                    "Format the response in markdown."
                },
                {
                    "role": "user",
                    "content": f"Summarize this transcript:\n\n{full_text}"
                }
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.warning(f"OpenAI summarization failed, using fallback: {str(e)}")
        return fallback_summary(transcript)