#!/usr/bin/env python3
"""CLI to print Jarvis prompts (behavior_prompts and Reply_prompts).

Usage:
    python tools\print_prompts\print_prompts.py --reply     # print Reply_prompts
    python tools\print_prompts\print_prompts.py --behavior  # print behavior_prompts
    python tools\print_prompts\print_prompts.py --all       # print both
"""
import argparse
import importlib
import sys
from pathlib import Path

# Make sure repo root is importable
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

def main():
    parser = argparse.ArgumentParser(description="Print Jarvis prompts")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--reply', action='store_true', help='Print Reply_prompts')
    group.add_argument('--behavior', action='store_true', help='Print behavior_prompts')
    group.add_argument('--all', action='store_true', help='Print both prompts')
    args = parser.parse_args()

    try:
        mod = importlib.import_module('Jarvis_prompts')
    except Exception as e:
        print(f"Failed to import Jarvis_prompts: {e}")
        sys.exit(2)

    if not (args.reply or args.behavior or args.all):
        args.all = True

    if args.behavior or args.all:
        bp = getattr(mod, 'behavior_prompts', None)
        print('\n' + '='*10 + ' behavior_prompts ' + '='*10 + '\n')
        print(bp if bp is not None else 'behavior_prompts not found')

    if args.reply or args.all:
        rp = getattr(mod, 'Reply_prompts', None)
        print('\n' + '='*10 + ' Reply_prompts ' + '='*10 + '\n')
        print(rp if rp is not None else 'Reply_prompts not found')

if __name__ == '__main__':
    main()
