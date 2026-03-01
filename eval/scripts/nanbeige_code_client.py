#!/usr/bin/env python3
"""
Nanbeige4.1-3B Code Completion Client

Usage:
    python nanbeige_code_client.py "def two_sum(nums, target):"
    python nanbeige_code_client.py --file test.py
"""

import argparse
import requests
import sys

DEFAULT_URL = "http://localhost:8889/v1/completions"
DEFAULT_MODEL = "Nanbeige.Nanbeige4.1-3B.Q8_0.gguf"


def complete_code(prompt: str, url: str = DEFAULT_URL, model: str = DEFAULT_MODEL,
                  temperature: float = 0.3, max_tokens: int = 1000) -> str:
    """Complete code using Nanbeige4.1-3B"""
    response = requests.post(
        url,
        json={
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        },
        timeout=120
    )
    response.raise_for_status()
    return response.json()["choices"][0]["text"]


def main():
    parser = argparse.ArgumentParser(description="Nanbeige code completion")
    parser.add_argument("prompt", nargs="?", help="Code prompt to complete")
    parser.add_argument("-f", "--file", help="Read prompt from file")
    parser.add_argument("-u", "--url", default=DEFAULT_URL, help="API URL")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument("-t", "--temperature", type=float, default=0.3, help="Temperature")
    parser.add_argument("-n", "--max-tokens", type=int, default=1000, help="Max tokens")

    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            prompt = f.read()
    elif args.prompt:
        prompt = args.prompt
    else:
        print("Error: Please provide prompt or --file", file=sys.stderr)
        sys.exit(1)

    try:
        result = complete_code(
            prompt,
            url=args.url,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )
        print(result)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
