#!/usr/bin/env python3
"""Apply n6 grades to ungraded TECS-L hypothesis files."""

import csv
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "auto_grade_results.csv")
HYPO_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "hypotheses")

GRADE_MARKERS = ["n6 Grade:", "🟩", "🟧", "⭐"]

def already_graded(text):
    for marker in GRADE_MARKERS:
        if marker in text:
            return True
    return False

def make_grade_line(suggested, unique_count):
    if suggested == "STRONG_CANDIDATE":
        return f"**n6 Grade: 🟩 EXACT** (auto-graded, {unique_count} unique n=6 constants)\n"
    elif suggested == "MODERATE":
        return f"**n6 Grade: 🟧 CLOSE** (auto-graded, {unique_count} unique n=6 constants)\n"
    return None

def insert_grade(filepath, grade_line):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find first heading line
    insert_idx = None
    for i, line in enumerate(lines):
        if line.startswith("# "):
            insert_idx = i + 1
            break

    if insert_idx is None:
        return False

    # Insert after heading (with blank line before/after)
    insert_block = ["\n", grade_line, "\n"]
    # If next line is already blank, skip adding leading blank
    if insert_idx < len(lines) and lines[insert_idx].strip() == "":
        insert_block = [grade_line, "\n"]

    lines[insert_idx:insert_idx] = insert_block

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return True

def main():
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    strong_count = 0
    moderate_count = 0
    skipped_existing = 0
    skipped_missing = 0

    for row in rows:
        grade = row["suggested_grade"]
        if grade not in ("STRONG_CANDIDATE", "MODERATE"):
            continue

        filename = row["file"]
        filepath = os.path.join(HYPO_DIR, filename)

        if not os.path.exists(filepath):
            skipped_missing += 1
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if already_graded(content):
            skipped_existing += 1
            continue

        unique_count = int(row["unique_n6_constants"])
        grade_line = make_grade_line(grade, unique_count)
        if grade_line is None:
            continue

        if insert_grade(filepath, grade_line):
            if grade == "STRONG_CANDIDATE":
                strong_count += 1
            else:
                moderate_count += 1

    total = strong_count + moderate_count
    print(f"=== n6 Auto-Grading Complete ===")
    print(f"EXACT  (STRONG): {strong_count}")
    print(f"CLOSE  (MODERATE): {moderate_count}")
    print(f"Total graded:    {total}")
    print(f"Skipped (already graded): {skipped_existing}")
    print(f"Skipped (file missing):   {skipped_missing}")

if __name__ == "__main__":
    main()
