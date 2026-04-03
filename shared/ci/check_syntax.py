#!/usr/bin/env python3
"""Batch py_compile check for CI.

Usage: python3 check_syntax.py dir1 [dir2 ...] [--recursive]
Exit codes: 0=all OK, 1=syntax errors found
"""
import os
import py_compile
import sys


def check_dir(directory, recursive=False):
    broken = []
    checked = 0
    if recursive:
        for root, _, files in os.walk(directory):
            if '__pycache__' in root or '.git' in root:
                continue
            for f in sorted(files):
                if f.endswith('.py') and not f.startswith('__'):
                    path = os.path.join(root, f)
                    checked += 1
                    try:
                        py_compile.compile(path, doraise=True)
                    except py_compile.PyCompileError as e:
                        broken.append((path, str(e)))
    else:
        if not os.path.isdir(directory):
            return 0, []
        for f in sorted(os.listdir(directory)):
            if f.endswith('.py') and not f.startswith('__'):
                path = os.path.join(directory, f)
                if os.path.isfile(path):
                    checked += 1
                    try:
                        py_compile.compile(path, doraise=True)
                    except py_compile.PyCompileError as e:
                        broken.append((path, str(e)))
    return checked, broken


def main():
    dirs = []
    recursive = False
    for arg in sys.argv[1:]:
        if arg == '--recursive':
            recursive = True
        else:
            dirs.append(arg)

    if not dirs:
        dirs = ['.']

    total_checked = 0
    all_broken = []
    for d in dirs:
        checked, broken = check_dir(d, recursive)
        total_checked += checked
        all_broken.extend(broken)

    print(f"Syntax check: {total_checked} files, {len(all_broken)} broken")
    for path, err in all_broken:
        print(f"  FAIL: {path}")
        print(f"        {err}")

    sys.exit(1 if all_broken else 0)


if __name__ == '__main__':
    main()
