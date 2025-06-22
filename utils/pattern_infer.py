#!/usr/bin/env python3
"""
Infer a company's e-mail pattern with GPT-4.1 (or gpt-4o).

Example:
    python pattern_infer.py --company nvidia
"""

import argparse, os
from typing import List

from dotenv import load_dotenv
import openai                         # ≥1.0.0

# 1 ▸ load env & instantiate client
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
#client = openai.Client()              # or openai.Client()

MODEL = "gpt-4.1"                     # change to gpt-4o if you wish
SYSTEM = (
    "You are an expert at inferring corporate e-mail address formats. "
    "Return one pattern using ONLY these placeholders: "
    "{first}, {first[0]}, {last}, {firstlast}. \n"
    "Use latest public data to infer this pattern.\n"
    "Example for company 'google' the output would be - {first[0]}{last}@google.com"
    "If unsure, answer \"unknown\"."
)
USER_TMPL = (
    "What is the most likely employee e-mail pattern at {company}? "
    "Return only the pattern."
)

def infer_pattern(company: str) -> str:
    """Query GPT and return its best-guess pattern string."""
    rsp = openai.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        max_tokens=25,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TMPL.format(company=company)}
        ],
    )
    return rsp.choices[0].message.content.strip()

def main(argv: List[str] | None = None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--company", required=True, help="e.g. nvidia")
    args = p.parse_args(argv)
    pattern = infer_pattern(args.company)
    print(f"{args.company}: {pattern}")

if __name__ == "__main__":
    main()
