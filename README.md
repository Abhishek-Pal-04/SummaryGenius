
# Youtube Summariser Using Local LLMs.

## Overview
This README outlines the project's purpose and structure for GitHub. The project aims to create a robust YouTube video
summary tool using Ollama and local LLMs.

## Structure
### Main Component: Fetching Transcripts
  - Description: The component fetches transcript data from YouTube's API.

### Integration with Ollama
- **API Call:** Integrates with Ollama and uses the local running models to generate summaries eleiminating the need of using the paid services of OpenAI etc. 
  - Description: Configures an API request and returns summary content for the video.

## Corrections (TODO)
### Summary Correction
- **Separate Thinking Section:** Clearly distinguish between the thought process and final answer (when using 'thinking' models).

### UI Update for History Items
- **Replace Previous Summaries:** When a history item is clicked, it replaces the previous summary instead of
appending.

### Fallback Summary
- **Correct after Failure:** Handles scenarios where the API call fails by returning a fallback summary.

