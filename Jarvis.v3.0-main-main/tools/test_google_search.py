#!/usr/bin/env python3
"""Quick tester for Jarvis_google_search.google_search

Usage:
  # ensure .env has GOOGLE_SEARCH_API_KEY and SEARCH_ENGINE_ID (or the alternate names)
  python tools/test_google_search.py "your query here"
"""
import sys
import asyncio
from dotenv import load_dotenv
load_dotenv()

from Jarvis_google_search import google_search

async def main():
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
    else:
        q = "python programming tutorials"
    print(f"Running google_search for: {q}\n")
    try:
        res = await google_search(q)
        print("--- RESULTS ---\n")
        print(res)
    except Exception as e:
        print(f"Error running google_search: {e}")

if __name__ == '__main__':
    asyncio.run(main())
