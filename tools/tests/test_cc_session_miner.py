import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cc_session_miner import parse_session

FIX = Path(__file__).parent / "fixtures"

class TestParseSession(unittest.TestCase):
    def test_parses_sample_session(self):
        result = parse_session(FIX / "sample_session.jsonl")
        self.assertEqual(result["tool_call_count"], 3)
        self.assertEqual(result["tool_result_bytes_total"], 32 + 32 + 13)
        self.assertEqual(result["tool_result_bytes_max"], 32)

    def test_skips_corrupt_lines(self):
        result = parse_session(FIX / "corrupt_session.jsonl")
        self.assertEqual(result["tool_call_count"], 1)
        self.assertEqual(result["corrupt_lines"], 1)

    def test_repeat_call_rate(self):
        result = parse_session(FIX / "sample_session.jsonl")
        # 3 calls, 2 unique → repeat rate = (3-2)/3 = 1/3
        self.assertEqual(result["unique_calls"], 2)
        self.assertAlmostEqual(result["repeat_rate"], 1/3, places=5)

if __name__ == "__main__":
    unittest.main()
