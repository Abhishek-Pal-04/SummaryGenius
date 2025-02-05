import unittest
from services.youtube import extract_video_id, get_video_transcript

class TestYouTubeService(unittest.TestCase):
    def test_extract_video_id_standard_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(extract_video_id(url), "dQw4w9WgXcQ")

    def test_extract_video_id_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        self.assertEqual(extract_video_id(url), "dQw4w9WgXcQ")

    def test_extract_video_id_embed_url(self):
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        self.assertEqual(extract_video_id(url), "dQw4w9WgXcQ")

    def test_extract_video_id_shorts_url(self):
        url = "https://youtube.com/shorts/dQw4w9WgXcQ"
        self.assertEqual(extract_video_id(url), "dQw4w9WgXcQ")

    def test_extract_video_id_invalid_url(self):
        url = "https://example.com/video"
        self.assertIsNone(extract_video_id(url))

    def test_extract_video_id_empty_url(self):
        self.assertIsNone(extract_video_id(""))
        self.assertIsNone(extract_video_id(None))

if __name__ == '__main__':
    unittest.main()
