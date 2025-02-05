import unittest
from unittest.mock import patch, MagicMock
from services.summarizer import (
    OllamaClient,
    extract_keywords,
    fallback_summary,
    generate_summary
)

class TestSummarizerService(unittest.TestCase):
    def setUp(self):
        self.sample_transcript = [
            {"timestamp": "00:00", "text": "Hello, this is a test video about machine learning.", "start": 0.0},
            {"timestamp": "00:05", "text": "Machine learning is a subset of artificial intelligence.", "start": 5.0},
            {"timestamp": "00:10", "text": "It allows computers to learn from data.", "start": 10.0}
        ]

    def test_extract_keywords(self):
        text = "Machine learning is a subset of artificial intelligence. It allows computers to learn from data."
        keywords = extract_keywords(text)
        self.assertIsInstance(keywords, list)
        self.assertTrue(all(isinstance(k, str) for k in keywords))
        self.assertGreater(len(keywords), 0)

    def test_fallback_summary(self):
        summary = fallback_summary(self.sample_transcript)
        self.assertIsInstance(summary, str)
        self.assertIn("# Summary", summary)
        self.assertIn("## Main Points", summary)
        self.assertIn("## Key Keywords", summary)
        self.assertIn("## Brief Overview", summary)

    @patch('services.summarizer.OllamaClient')
    def test_generate_summary_with_ollama(self, mock_ollama):
        # Mock successful Ollama response
        mock_instance = mock_ollama.return_value
        mock_instance.generate.return_value = "# Test Summary\n## Main Points\n- Point 1"
        
        summary = generate_summary(self.sample_transcript)
        self.assertIn("# Test Summary", summary)
        self.assertIn("## Main Points", summary)
        mock_instance.generate.assert_called_once()

    @patch('services.summarizer.OllamaClient')
    def test_generate_summary_fallback(self, mock_ollama):
        # Mock failed Ollama response
        mock_instance = mock_ollama.return_value
        mock_instance.generate.return_value = None
        
        summary = generate_summary(self.sample_transcript)
        self.assertIn("# Summary", summary)
        self.assertIn("## Main Points", summary)
        self.assertIn("This is an automated summary", summary)

class TestOllamaClient(unittest.TestCase):
    def setUp(self):
        self.client = OllamaClient()

    @patch('requests.post')
    def test_generate_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Test response"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        response = self.client.generate("Test prompt")
        self.assertEqual(response, "Test response")
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_generate_failure(self, mock_post):
        mock_post.side_effect = Exception("Test error")
        response = self.client.generate("Test prompt")
        self.assertIsNone(response)

if __name__ == '__main__':
    unittest.main()
