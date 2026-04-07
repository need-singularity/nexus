"""Tests for output parser."""
from n6_replication.parser import parse_output

class TestParser:
    def test_pass_fail_counts(self):
        output = "Check 1: ✅ Pass\nCheck 2: ❌ Fail\nCheck 3: ✅ Pass\n"
        result = parse_output(output)
        assert result["pass_count"] == 2
        assert result["fail_count"] == 1

    def test_grade_counts(self):
        output = "🟩 H001 proven\n🟩 H002 proven\n🟧 H003 structural\n⚪ H004 coincidence\n⬛ H005 refuted\n"
        result = parse_output(output)
        assert result["grades"]["green"] == 2
        assert result["grades"]["orange"] == 1
        assert result["grades"]["white"] == 1
        assert result["grades"]["black"] == 1

    def test_p_value_extraction(self):
        output = "Texas Sharpshooter: p=0.0001\nAnother: p-value: 0.05\n"
        result = parse_output(output)
        assert len(result["p_values"]) == 2
        assert result["p_values"][0] < 0.001

    def test_empty_output_fallback(self):
        result = parse_output("")
        assert result["pass_count"] == 0
        assert result["fail_count"] == 0
        assert result["status"] == "parse_error"

    def test_star_discovery(self):
        output = "⭐ Major discovery: H090\n★ H067 confirmed\n"
        result = parse_output(output)
        assert result["stars"] == 2
