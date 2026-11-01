"""Unit tests for the audio-only dead-window heuristic (no movie content)."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from qa.movie_short_audio_guard import dead_windows  # noqa: E402


class QuietWindowTests(unittest.TestCase):
    def test_long_quiet_passage_without_words_is_rejected(self):
        with patch("qa.movie_short_audio_guard.integrated_lufs", return_value=-34.0):
            self.assertEqual(dead_windows("dummy.wav", [], 9, window=3, hop=1.5),
                             [(0.0, 9.0, -34.0)])

    def test_spoken_dialogue_does_not_create_quiet_failure(self):
        with patch("qa.movie_short_audio_guard.integrated_lufs", return_value=-35.0):
            self.assertFalse(dead_windows("dummy.wav", [(0, 10, "Здравствуйте")], 9,
                                          window=3, hop=1.5))

    def test_audible_ambience_is_not_marked_dead(self):
        with patch("qa.movie_short_audio_guard.integrated_lufs", return_value=-25.0):
            self.assertFalse(dead_windows("dummy.wav", [], 9, window=3, hop=1.5))


if __name__ == "__main__":
    unittest.main()
