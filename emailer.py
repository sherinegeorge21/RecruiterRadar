"""
emailer.py – stateless helper used by Streamlit app.
Send a DataFrame of recruiter names with a single GPT-inferred pattern.

Public function
---------------
send_bulk(df, pattern, gmail_user, gmail_pwd,
          subject_tpl, intro, closing, resume_bytes)

Returns a list of addresses successfully mailed.
"""
from __future__ import annotations
import ssl, smtplib, certifi, os
from email.message import EmailMessage
from pathlib import Path
from typing import List

# ------------ defaults (fallback if UI fields empty) -----------------------
SUBJECT_TPL = "Data Scientist → impact at {company_cap}"

INTRO_DEFAULT = (
    "I’m FirstName LastName, a student at ....”. "
)

CLOSING_DEFAULT = (
    "I’m open to Data-Science / Machine-Learning roles and would love to explore "
    "how my background could contribute to {company_cap}.\n\n"
    "Best regards,\nYour name\n\n"
)

# ------------ small helpers -------------------------------------------------
def _split(name: str) -> tuple[str, str]:
    parts = name.split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[-1]

def _addr(pattern: str, first: str, last: str) -> str:
    return (pattern
        .replace("{first}", first.lower())
        .replace("{last}",  last.lower())
        .replace("{first[0]}", first[:1].lower())
        .replace("{firstlast}", f"{first}{last}".lower())
    )

def _compose(to_addr: str, company: str, first: str,
             subject_tpl: str, intro: str, closing: str,
             resume_bytes: bytes) -> EmailMessage:

    body = (
        f"Hello {first or 'there'},\n\n"
        + intro.strip() + "\n\n"
        + closing.strip().format(company_cap=company.capitalize())
    )

    msg = EmailMessage()
    msg["From"] = msg["Reply-To"] = os.getenv("GMAIL_ADDRESS", to_addr)
    msg["To"]   = to_addr
    msg["Subject"] = subject_tpl.format(company_cap=company.capitalize())
    msg.set_content(body)

    msg.add_attachment(
        resume_bytes,
        maintype="application",
        subtype="pdf",
        filename="Resume.pdf",
    )
    return msg

# ------------ main callable -------------------------------------------------
def send_bulk(
    df,
    pattern: str,
    *,
    gmail_user: str,
    gmail_pwd: str,
    subject_tpl: str | None = None,
    intro: str | None = None,
    closing: str | None = None,
    resume_bytes: bytes,
) -> List[str]:
    """
    df             – Pandas DataFrame with columns ['name','company']
    pattern        – String like '{first}.{last}@stripe.com'
    resume_bytes   – Raw PDF bytes from Streamlit uploader
    Returns list   – Addresses successfully mailed
    """
    subject_tpl = subject_tpl or SUBJECT_TPL
    intro       = intro       or INTRO_DEFAULT
    closing     = closing     or CLOSING_DEFAULT

    sent: List[str] = []
    ctx  = ssl.create_default_context(cafile=certifi.where())

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
        server.login(gmail_user, gmail_pwd)

        for _, row in df.iterrows():
            first, last = _split(row["name"])
            to_addr     = _addr(pattern, first, last)
            msg         = _compose(
                to_addr, row["company"], first,
                subject_tpl, intro, closing, resume_bytes
            )
            try:
                server.send_message(msg)
                sent.append(to_addr)
            except Exception as exc:
                print("ERROR", to_addr, exc)

    return sent
