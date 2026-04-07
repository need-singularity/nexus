"""Tests for math atlas hypothesis parser."""
import sys, os, json, tempfile, sqlite3, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.shared'))

from scan_math_atlas import parse_hypothesis_md

def test_pattern_a_hypothesis_review():
    text = "# Hypothesis Review 056: Meta Recursion ✅\n\n## Hypothesis\n> Does infinite meta converge?"
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/056-meta-recursion.md")
    assert h["id"] == "TECS-L:056"
    assert "Meta Recursion" in h["title"]
    assert h["repo"] == "TECS-L"

def test_pattern_b_hypothesis_plain():
    text = "# Hypothesis 355: Prediction Error = Surprise\n\n## Hypothesis\n> Consciousness is a prediction engine."
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/355-prediction-error.md")
    assert h["id"] == "TECS-L:355"
    assert "Prediction Error" in h["title"]

def test_pattern_c_domain_prefix():
    text = "# H-CX-215: Brainwave Product\n\n> delta x theta = 96000\n"
    h = parse_hypothesis_md(text, "TECS-L", "math/docs/hypotheses/H-CX-215-brainwave.md")
    assert h["id"] == "TECS-L:H-CX-215"
    assert h["domain"] == "CX"

def test_pattern_c_sedi():
    text = "# H-CA-001: Anima Phi_max = 8\n\n> **Hypothesis**: Anima values.\n\n## Grade: 🟧★\n"
    h = parse_hypothesis_md(text, "SEDI", "docs/hypotheses/H-CA-001-phi-max.md")
    assert h["id"] == "SEDI:H-CA-001"
    assert h["domain"] == "CA"
    assert h["grade"] == "🟧★"

def test_pattern_d_yaml_frontmatter():
    text = '---\nid: H-STAT-1\ntitle: "Chi-Squared"\nstatus: "VERIFIED"\ngrade: "🟩⭐⭐⭐"\ndate: 2026-03-26\n---\n# H-STAT-1: Chi-Squared\n\n> **Hypothesis.** The chi-squared distribution\n'
    h = parse_hypothesis_md(text, "TECS-L", "math/docs/hypotheses/H-STAT-1-chi-squared.md")
    assert h["id"] == "TECS-L:H-STAT-1"
    assert "⭐⭐⭐" in h["grade"]

def test_grade_extraction():
    text = "# H-CX-651: TEE = ln(phi(6))\n\n> Hypothesis text\n\n## Grade: 🟩 CONFIRMED (exact)\n"
    h = parse_hypothesis_md(text, "SEDI", "docs/hypotheses/H-CX-651-tee.md")
    assert "🟩" in h["grade"]

def test_grade_from_status_line():
    text = "# H-TOP-1: Betti Numbers\n\n> **Hypothesis**: Betti numbers satisfy constraints.\n\n**Status: ⚪ Refuted (incompatibility proof)**\n"
    h = parse_hypothesis_md(text, "TECS-L", "math/docs/hypotheses/H-TOP-1-betti.md")
    assert "⚪" in h["grade"]

def test_grade_from_title_emoji():
    text = "# H-CX-215: 🟩 Brainwave Product\n\n> delta x theta\n"
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/H-CX-215-brainwave.md")
    assert "🟩" in h["grade"]

def test_cross_refs():
    text = "# Hypothesis Review 056: Meta\n\nRelated hypotheses: 041(Transcendence), 055(Eye), 067(1/2+1/3=5/6)\n"
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/056-meta.md")
    assert "041" in str(h["refs"])
    assert "055" in str(h["refs"])

def test_gz_dependent():
    text = "# H-CX-61: Maximum Divisor Entropy\n\n**Golden Zone dependency:** NONE for math basis\n"
    h = parse_hypothesis_md(text, "TECS-L", "math/docs/hypotheses/H-CX-61-max-entropy.md")
    assert h["gz_dependent"] is False

def test_gz_dependent_true():
    text = "# H-CX-100: Something\n\n**Golden Zone dependency:** YES\n"
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/H-CX-100-something.md")
    assert h["gz_dependent"] is True

def test_no_match_returns_fallback():
    text = "# Some random markdown\n\nNo hypothesis here.\n"
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/random.md")
    assert h["id"] == "TECS-L:random"
    assert h["title"] == "Some random markdown"

from scan_math_atlas import parse_anima_recommender


def test_anima_recommender_parser():
    source = '''
HYPOTHESIS_DB = [
    Hypothesis(
        code="B1",
        name="Bidirectional coupling",
        category="learning",
        expected_phi=3.2,
        description="Phi-guided bidirectional Hebbian coupling",
        conditions={"phi_min": 0.5},
        tags=["low_phi", "growth_stall"],
    ),
    Hypothesis(
        code="DD94",
        name="Wave+Phi mega combo",
        category="discovery",
        expected_phi=8.12,
        description="Combined wave modulation and phi feedback",
        conditions={"phi_min": 2.0, "cells_min": 8},
        tags=["mega"],
    ),
]
'''
    results = parse_anima_recommender(source)
    assert len(results) == 2
    assert results[0]["id"] == "anima:B1"
    assert results[0]["title"] == "Bidirectional coupling"
    assert results[1]["id"] == "anima:DD94"
    assert results[1]["grade"] is None


from scan_math_atlas import build_atlas, write_sqlite, write_dot


def test_build_atlas_returns_dict():
    atlas = build_atlas()
    assert "version" in atlas
    assert "hypotheses" in atlas
    assert isinstance(atlas["hypotheses"], list)
    assert len(atlas["hypotheses"]) > 1000


def test_build_atlas_no_duplicate_ids():
    atlas = build_atlas()
    ids = [h["id"] for h in atlas["hypotheses"]]
    dupes = [x for x in ids if ids.count(x) > 1]
    assert len(dupes) == 0, f"Duplicate IDs: {set(dupes)}"


def test_build_atlas_json_serializable():
    atlas = build_atlas()
    json.dumps(atlas, ensure_ascii=False)


def test_write_sqlite():
    atlas = build_atlas()
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        dbpath = f.name
    try:
        write_sqlite(atlas, dbpath)
        conn = sqlite3.connect(dbpath)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM hypotheses")
        count = cur.fetchone()[0]
        assert count == atlas["total"]
        cur.execute("SELECT COUNT(*) FROM edges")
        conn.close()
    finally:
        os.unlink(dbpath)


def test_write_dot():
    atlas = build_atlas()
    with tempfile.NamedTemporaryFile(suffix='.dot', delete=False, mode='w') as f:
        dotpath = f.name
    try:
        write_dot(atlas, dotpath)
        content = open(dotpath).read()
        assert content.startswith("digraph math_atlas {")
        assert "}" in content
        assert "label=" in content
    finally:
        os.unlink(dotpath)


from scan_math_atlas import extract_constants_from_py

_SEDI_TECS = "/Users/ghost/Dev/SEDI/sedi/tecs.py"
_skip_no_sedi = unittest.skipUnless(os.path.exists(_SEDI_TECS), "SEDI repo not available")


@_skip_no_sedi
def test_extract_constants():
    """Test constant extraction from a known file."""
    results = extract_constants_from_py(
        "/Users/ghost/Dev/SEDI/sedi/tecs.py", "SEDI"
    )
    names = [r["name"] for r in results]
    assert "TARGETS_BASIC" in names
    assert "PHYSICS_MATCHES" in names
    # Should have values for simple dicts
    tb = next(r for r in results if r["name"] == "TARGETS_BASIC")
    assert tb["type"] == "dict"
    assert tb["size"] > 0
    assert tb["category"] == "targets"


@_skip_no_sedi
def test_extract_constants_evaluable():
    """Test that simple dicts with only literals are evaluable."""
    results = extract_constants_from_py(
        "/Users/ghost/Dev/SEDI/sedi/tecs.py", "SEDI"
    )
    # SM_COUNTS has only integer literals - should be evaluable
    sm = next((r for r in results if r["name"] == "SM_COUNTS"), None)
    if sm:
        assert sm["evaluable"] is True
        assert isinstance(sm["values"], dict)
        assert sm["values"]["quark_flavors"] == 6
    # TARGETS_BASIC has 5/6, 1/6 etc. (BinOp) so may not be literal_eval-able
    tb = next(r for r in results if r["name"] == "TARGETS_BASIC")
    assert tb["type"] == "dict"
    assert tb["size"] > 0
    assert tb["keys"] is not None


@_skip_no_sedi
def test_extract_constants_non_evaluable():
    """Test that dicts with expressions are marked non-evaluable."""
    results = extract_constants_from_py(
        "/Users/ghost/Dev/SEDI/sedi/tecs.py", "SEDI"
    )
    # DIMENSION_MAP uses function calls like tau(6) - not literal_eval-able
    dm = next((r for r in results if r["name"] == "DIMENSION_MAP"), None)
    if dm:
        assert dm["evaluable"] is False
        assert dm["keys"] is not None


@_skip_no_sedi
def test_extract_constants_skips_lowercase():
    """Test that lowercase and non-constant names are skipped."""
    results = extract_constants_from_py(
        "/Users/ghost/Dev/SEDI/sedi/tecs.py", "SEDI"
    )
    names = [r["name"] for r in results]
    # Should not include lowercase variable names
    for name in names:
        assert name == name.upper() or name.replace("_", "").isupper()


@_skip_no_sedi
def test_extract_constants_list():
    """Test extraction of list constants."""
    results = extract_constants_from_py(
        "/Users/ghost/Dev/SEDI/sedi/tecs.py", "SEDI"
    )
    ef = next((r for r in results if r["name"] == "EGYPTIAN_FRACTIONS"), None)
    if ef:
        assert ef["type"] == "list"
        assert ef["size"] == 3


def test_build_atlas_has_constants():
    """Test that build_atlas includes constant_maps."""
    atlas = build_atlas()
    assert "constant_maps" in atlas
    assert len(atlas["constant_maps"]) > 50  # expect many across 3 repos
    assert "constant_stats" in atlas


def test_constants_json_serializable():
    """Test that constant maps are JSON-serializable."""
    atlas = build_atlas()
    json.dumps(atlas["constant_maps"], ensure_ascii=False)


def test_write_sqlite_with_constants():
    """Test that SQLite output includes constant_maps table."""
    atlas = build_atlas()
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        dbpath = f.name
    try:
        write_sqlite(atlas, dbpath)
        conn = sqlite3.connect(dbpath)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM constant_maps")
        count = cur.fetchone()[0]
        assert count == len(atlas["constant_maps"])
        cur.execute("SELECT DISTINCT category FROM constant_maps")
        categories = [row[0] for row in cur.fetchall()]
        assert len(categories) > 1
        conn.close()
    finally:
        os.unlink(dbpath)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
