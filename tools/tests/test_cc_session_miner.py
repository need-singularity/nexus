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

    def test_aggregate_sessions(self):
        from cc_session_miner import aggregate_sessions
        result = aggregate_sessions([FIX / "sample_session.jsonl", FIX / "corrupt_session.jsonl"])
        # sample: 3 calls, corrupt: 1 call → 4 total
        self.assertEqual(result["total_tool_calls"], 4)
        self.assertEqual(result["session_count"], 2)
        self.assertIn("mean_tool_result_bytes", result)
        self.assertIn("p95_tool_result_bytes", result)

    def test_render_metrics_md(self):
        from cc_session_miner import render_metrics_md, render_hypotheses_md
        agg = {
            "session_count": 2, "total_tool_calls": 4,
            "total_tool_result_bytes": 109, "mean_tool_result_bytes": 27.25,
            "p50_tool_result_bytes": 32, "p95_tool_result_bytes": 32,
            "mean_repeat_rate": 0.167, "corrupt_lines_total": 1,
        }
        md = render_metrics_md(agg, date_str="2026-04-05")
        self.assertIn("# Claude Code 효율 지표", md)
        self.assertIn("2026-04-05", md)
        self.assertIn("p95", md)
        self.assertIn("세션당", md)
        self.assertIn("##", md)
        self.assertIn("=", md)

        hyp = render_hypotheses_md(agg, date_str="2026-04-05")
        self.assertIn("# 돌파 가설", hyp)
        self.assertIn("H1", hyp)

if __name__ == "__main__":
    unittest.main()
