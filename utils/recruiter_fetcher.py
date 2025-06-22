# utils/recruiter_fetcher.py
import os, re, requests
from typing import List
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
GOOGLE_CX_ID   = os.getenv("GOOGLE_CX_ID")
SEARCH_ENDPOINT = "https://customsearch.googleapis.com/customsearch/v1"
NAME_RE = re.compile(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b")

# --- constants -------------------------------------------------------------
NAME_RE     = re.compile(r"^(?!Hi\b|Hey\b|Hello\b)[A-Z][a-z]{2,15} [A-Z][a-z]{2,15}$")
GREETINGS   = {"hi", "hey", "hello"}
ROLE_WORDS  = {"recruiter", "university", "student", "community", "friends",
               "team", "cohort", "class", "talent", "intern","grad","cycle","specialist","hiring","developer","senior","technical","relations","manager","scientist","partner"
               ,"solutions","architect","engineer","associate","analyst","human","san","one","zuckerberg","your","differenciate"}

def looks_like_person(candidate: str) -> bool:
    first, last = candidate.lower().split()
    return (
        first not in GREETINGS
        and first not in ROLE_WORDS
        and last  not in ROLE_WORDS
        and 2 < len(first) < 16
        and 2 < len(last)  < 16
    )


def fetch_recruiters(company: str, q_phrase: str = "university recruiter", pages: int = 3) -> List[str]:
    results, start = [], 1
    for _ in range(pages):
        params = {
            "key": GOOGLE_API_KEY,
            "cx":  GOOGLE_CX_ID,
           "q":   f'site:linkedin.com "{q_phrase}" {company}',
            "start": str(start),
        }
        data = requests.get(SEARCH_ENDPOINT, params=params, timeout=15).json()
        for item in data.get("items", []):
            title = item.get("title", "")
            # grab the FIRST Title-Cased pair in the title string
            if (m := re.search(r"[A-Z][a-z]+ [A-Z][a-z]+", title)):
                candidate = m.group()
                if NAME_RE.match(candidate) and looks_like_person(candidate):
                    results.append(candidate)
        start = data.get("queries", {}).get("nextPage", [{}])[0].get("startIndex", 0)
        if not start:
            break
    return list(dict.fromkeys(results))      # dedupe, keep order
