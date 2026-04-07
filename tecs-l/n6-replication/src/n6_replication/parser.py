"""Parse verification script output to extract pass/fail, grades, p-values."""

import re

_PASS_LINE = re.compile(r"✅|(?<!\w)[Pp]ass(?:ed)?(?!\w)|(?<!\w)PASS(?!\w)")
_FAIL_LINE = re.compile(r"❌|(?<!\w)[Ff]ail(?:ed)?(?!\w)|(?<!\w)FAIL(?!\w)")
_GRADE_MAP = {
    "green": re.compile(r"🟩"),
    "orange": re.compile(r"🟧"),
    "white": re.compile(r"⚪"),
    "black": re.compile(r"⬛"),
}
_STAR_PATTERN = re.compile(r"⭐|★")
_PVALUE_PATTERN = re.compile(r"p[-\s]*(?:value)?[=:\s]+([0-9]+\.?[0-9]*(?:e[+-]?[0-9]+)?)", re.IGNORECASE)


def parse_output(stdout: str) -> dict:
    """Parse script stdout and return structured results."""
    lines = stdout.splitlines()
    pass_count = sum(1 for line in lines if _PASS_LINE.search(line))
    fail_count = sum(1 for line in lines if _FAIL_LINE.search(line))
    grades = {name: len(pat.findall(stdout)) for name, pat in _GRADE_MAP.items()}
    stars = len(_STAR_PATTERN.findall(stdout))
    p_values = [float(m) for m in _PVALUE_PATTERN.findall(stdout)]
    total = pass_count + fail_count + sum(grades.values())
    status = "parse_error" if total == 0 else ("pass" if fail_count == 0 else "fail")
    return {
        "pass_count": pass_count,
        "fail_count": fail_count,
        "grades": grades,
        "p_values": p_values,
        "stars": stars,
        "status": status,
    }
