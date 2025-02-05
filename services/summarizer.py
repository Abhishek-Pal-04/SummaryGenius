import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def generate_summary(transcript):
    """Generate a summary of the transcript using OpenAI's GPT-3.5-turbo"""
    # Combine transcript text
    full_text = " ".join([entry['text'] for entry in transcript])

    try:
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
        raise Exception(f"Failed to generate summary: {str(e)}")