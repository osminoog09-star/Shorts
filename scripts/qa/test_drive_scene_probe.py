#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from drive_scene_probe import drive_id, hint_range


class ProbeTests(unittest.TestCase):
    def test_hint_hours_minutes(self):
        self.assertEqual(hint_range("~00:28–00:35"), (1680, 2100))
        self.assertEqual(hint_range("~02:05–02:22"), (7500, 8520))
        self.assertEqual(hint_range("~01:45–01:55"), (6300, 6900))

    def test_drive_id_allowlist(self):
        self.assertEqual(drive_id("https://drive.google.com/uc?id=ABCDEFGHIJKLMN"), "ABCDEFGHIJKLMN")
        for bad in ["https://evil.test/uc?id=ABCDEFGHIJKLMN",
                    "https://drive.google.com/file/d/ABCDEFGHIJKLMN",
                    "http://drive.google.com/uc?id=ABCDEFGHIJKLMN"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                drive_id(bad)


if __name__ == "__main__":
    unittest.main()
