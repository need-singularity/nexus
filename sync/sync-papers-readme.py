#!/usr/bin/env python3
"""papers/manifest.json (SSOT) → README.md 자동 생성

manifest.json이 원본. README 내 <!-- AUTO:PAPERS:START/END --> 마커 사이를 자동 갱신.
"""
import json
import os
import sys
from collections import Counter

PAPERS_DIR = os.path.expanduser("~/Dev/papers")
MANIFEST = os.path.join(PAPERS_DIR, "manifest.json")
README = os.path.join(PAPERS_DIR, "README.md")
MARKER_START = "<!-- AUTO:PAPERS:START -->"
MARKER_END = "<!-- AUTO:PAPERS:END -->"

def load_manifest():
    with open(MANIFEST) as f:
        return json.load(f)

def generate_table(papers):
    """Generate markdown table from papers list."""
    # Group by repo
    by_repo = {}
    for p in papers:
        repo = p.get("repo", "Unknown")
        by_repo.setdefault(repo, []).append(p)

    lines = []
    total = len(papers)
    published = sum(1 for p in papers if p.get("status") == "Published")
    
    lines.append(f"**Total: {total} papers** ({published} Published on Zenodo)")
    lines.append("")

    # Summary by repo
    repo_counts = Counter(p.get("repo", "?") for p in papers)
    summary = " + ".join(f"{r} ({c})" for r, c in sorted(repo_counts.items()))
    lines.append(f"Repos: {summary}")
    lines.append("")

    # Full table
    lines.append("| ID | Title | Zenodo | Status |")
    lines.append("|-----|-------|--------|--------|")
    
    for p in sorted(papers, key=lambda x: x.get("id", "")):
        pid = p.get("id", "?")
        title = p.get("title", "?")
        doi = p.get("doi", "")
        status = p.get("status", "Draft")
        
        if doi:
            zenodo = f"[{doi.split('/')[-1]}](https://doi.org/{doi})"
        else:
            zenodo = "-"
        
        lines.append(f"| {pid} | {title} | {zenodo} | {status} |")

    return "\n".join(lines)

def update_readme(table_content):
    """Update README between markers."""
    if not os.path.exists(README):
        print(f"README not found: {README}")
        return False

    with open(README) as f:
        content = f.read()

    if MARKER_START not in content:
        print(f"Marker {MARKER_START} not found in README. Adding at end.")
        content += f"\n\n{MARKER_START}\n{table_content}\n{MARKER_END}\n"
    else:
        start = content.index(MARKER_START) + len(MARKER_START)
        end = content.index(MARKER_END)
        content = content[:start] + "\n" + table_content + "\n" + content[end:]

    with open(README, "w") as f:
        f.write(content)
    return True

def sync_to_other_repos(papers):
    """Update paper counts in other repos' READMEs."""
    total = len(papers)
    published = sum(1 for p in papers if p.get("status") == "Published")
    badge = f"📄 Papers — {total} papers ({published} published)"
    
    for repo in ["TECS-L", "n6-architecture", "anima", "sedi", "brainwire", "nexus6"]:
        readme = os.path.expanduser(f"~/Dev/{repo}/README.md")
        if not os.path.exists(readme):
            continue
        with open(readme) as f:
            content = f.read()
        # Update paper count if marker exists
        if "<!-- AUTO:PAPER_COUNT:START -->" in content:
            start = content.index("<!-- AUTO:PAPER_COUNT:START -->") + len("<!-- AUTO:PAPER_COUNT:START -->")
            end = content.index("<!-- AUTO:PAPER_COUNT:END -->")
            content = content[:start] + f"\n{badge}\n" + content[end:]
            with open(readme, "w") as f:
                f.write(content)
            print(f"  ✅ {repo}: paper count updated")

def main():
    manifest = load_manifest()
    papers = manifest.get("papers", [])
    
    print(f"📄 manifest.json: {len(papers)} papers")
    
    table = generate_table(papers)
    
    if update_readme(table):
        print(f"✅ README.md updated ({len(papers)} papers)")
    
    sync_to_other_repos(papers)

if __name__ == "__main__":
    main()
