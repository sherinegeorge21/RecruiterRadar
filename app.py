import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from utils.pattern_infer import infer_pattern
from utils.recruiter_fetcher import fetch_recruiters
from emailer import send_bulk
import time 

st.markdown("""
<style>
/* round card edges & subtle shadow */
section.main > div:has(.stForm) {
    border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,.05);
}
/* bolder CTA button */
div.stButton > button:first-child {
    font-weight: 600; border-radius: 6px;
}
/* tighten table row height */
.row-widget.stDataFrame div[data-baseweb="table"] td {
    padding-top: 6px; padding-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)


def make_email(pattern: str, full_name: str) -> str:
    """Substitute {first}, {last}, {first[0]}, {firstlast} in *pattern*."""
    parts = full_name.split()
    if not parts:
        return ""
    first, last = parts[0].lower(), parts[-1].lower()
    return (pattern
            .replace("{first}", first)
            .replace("{last}", last)
            .replace("{first[0]}", first[:1])
            .replace("{firstlast}", f"{first}{last}"))

# ── basic setup ────────────────────────────────────────────────────────────
load_dotenv()
st.set_page_config(
    page_title="Recruiter Radar – AI-powered outreach",
    page_icon="💌",
    layout="wide"
)

# ------------------------------------------------------------------
#  TOP NAV BAR  – insert right after st.set_page_config(...)
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
      /* ── top bar ───────────────────────────────────────────── */
      .top-bar{
        position:fixed;top:0;left:0;right:0;height:56px;
        background:#0d6efd;display:flex;align-items:center;
        padding-left:1rem;                    /* no extra right-padding now */
        box-shadow:0 1px 3px rgba(0,0,0,.15);z-index:1000001;
      }
      .top-bar h2{
        color:#fff;margin:0;font-size:1.05rem;font-weight:600;
      }

      /* GitHub badge sits 70 px left of the viewport edge = clears “Deploy” */
      .github-btn{
        position:absolute;right:0px;top:0;height:56px;width:56px;
        display:flex;align-items:center;padding:0 14px;
        cursor:pointer;text-decoration:none;z-index:1000002;pointer-events:auto;
      }
      .github-btn:hover{background:rgba(255,255,255,.15);}
      .github-btn svg{pointer-events:none;}  /* let the <a> get the click */

      /* push Streamlit content below bar */
      div.block-container{margin-top:66px;}
      
    </style>

    <div class="top-bar">
      <h2>Recruiter Radar Dashboard</h2>

      <a  href="https://github.com/sherinegeorge21"
          target="_blank" rel="noopener noreferrer"
          class="github-btn" aria-label="GitHub">
        <!-- white GitHub mark -->
        <svg width="22" height="22" viewBox="0 0 16 16" fill="#ffffff"
             xmlns="http://www.w3.org/2000/svg">
          <path d="M8 .198a8 8 0 0 0-2.53 15.59c.4.074.547-.174.547-.386
                   0-.19-.007-.693-.01-1.36-2.226.483-2.695-1.073-2.695-1.073
                   -.364-.924-.89-1.17-.89-1.17-.727-.497.055-.487.055-.487
                   .803.056 1.226.825 1.226.825.715 1.223 1.874.87
                   2.332.665.072-.518.28-.87.508-1.07-1.777-.2-3.644-.888
                   -3.644-3.956 0-.874.312-1.588.823-2.15-.083-.202-.357-1.017
                   .078-2.12 0 0 .67-.215 2.2.82a7.518 7.518 0 0 1 2.003-.27
                   7.5 7.5 0 0 1 2.003.27c1.53-1.035 2.2-.82 2.2-.82.435 1.103
                   .161 1.918.08 2.12.513.562.823 1.276.823 2.15 0 3.077-1.87
                   3.753-3.65 3.95.288.248.543.738.543 1.488 0 1.074-.01
                   1.94-.01 2.2 0 .214.145.463.55.385A8.001 8.001 0 0 0 8 .198z"/>
        </svg>
      </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
      /* blur only the 'name' column inside the dataframe */
      .stDataFrame div[data-testid="stVerticalBlock"] > div:nth-child(1) {
          filter: blur(100px);      /* tweak px as needed */
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── header bar ─────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;margin-bottom:0'>Recruiter Radar – AI-powered outreach</h1>",
    unsafe_allow_html=True,
)

# Put the entire UI in a centred column (15 %-70 %-15 % grid)
left_spacer, main, right_spacer = st.columns([0.15, 0.7, 0.15])

with main:
    # ───────────────────────────────────────────────────────────────────────
    # ① INPUT FORM
    # ───────────────────────────────────────────────────────────────────────
    with st.form("inputs", border=True):
        col1, col2 = st.columns([2, 2])
        company       = col1.text_input("Company (lower-case)", "").strip().lower()
        search_phrase = col2.text_input("LinkedIn search phrase", "university recruiter")

        resume = st.file_uploader("Upload résumé (PDF)", type=["pdf"])

        subject_tpl = st.text_input(
            "Subject template",
            "Data Scientist → impact at {company_cap}",
            help="{company_cap} will be replaced by capitalised company name",
        )

        intro = st.text_area(
            "Intro paragraph",
            "I’m Firstname Lastname, a student at …",
            height=110,
        )
        closing = st.text_area(
            "Closing paragraph",
            "I’m open to Software Engineering /Data-Science / ML roles …",
            height=110,
        )

        submitted = st.form_submit_button("🔎 Fetch recruiters", type="primary")

    # ───────────────────────────────────────────────────────────────────────
    # ② BACK-END (runs once on submit)
    # ───────────────────────────────────────────────────────────────────────
    if submitted:
        if not company:
            st.warning("Please enter a company name.")
            st.stop()
        if resume is None:
            st.warning("Please upload a résumé PDF.")
            st.stop()

        # cache user inputs in session_state
        st.session_state.update({
            "resume_bytes": resume.getvalue(),
            "subject_tpl":  subject_tpl,
            "intro":        intro,
            "closing":      closing,
        })

        with st.spinner("✨ Inferring e-mail pattern …"):
            pattern = infer_pattern(company)
        with st.spinner("🔍 Scraping LinkedIn search results …"):
            names = fetch_recruiters(company, q_phrase=search_phrase)

        st.session_state["pattern"] = pattern
        emails = [make_email(pattern, n) for n in names]
        st.session_state["df"] = pd.DataFrame(
    {"name": names, "company": company, "email": emails}
)
        st.toast("Recruiters fetched!", icon="✅")

    # ───────────────────────────────────────────────────────────────────────
    # ③ RESULTS / MAILING
    # ───────────────────────────────────────────────────────────────────────
    if "df" in st.session_state:
        pattern = st.session_state["pattern"]
        df      = st.session_state["df"]

        st.success(f"Most likely e-mail pattern → **`{pattern}`**")
        st.markdown(f"### Recruiters ({len(df)})")
        st.dataframe(
            df,
            use_container_width=True,
            height=min(500, 37 + len(df) * 35),
        )

        # preview first-five addresses
        preview = [
            pattern.replace("{first}", n.split()[0].lower())
                   .replace("{last}",  n.split()[-1].lower())
                   .replace("{first[0]}", n[0].lower())
                   .replace("{firstlast}", "".join(n.split()).lower())
            for n in df["name"].head(5)
        ]
        st.caption("Preview → " + ", ".join(preview) + (" …" if len(df) > 5 else ""))

        

        # download button & send button on same row
        dl_col, send_col = st.columns([1, 1])
        with dl_col:
            st.download_button(
                "⬇️ CSV",
                data=df.to_csv(index=False).encode(),
                file_name=f"{company}_recruiters.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with send_col:
            demo = False
            if st.button("🚀 Send e-mails", use_container_width=True):
                with st.spinner("📤 Sending … this may take a minute" if not demo else "Simulating…"):
                     if demo:
                # pretend-send: just sleep 1 s per row
                        time.sleep(len(df) * 1)
                        sent = [f"(demo) {addr}" for addr in df.email]
                     else:
                        sent = send_bulk(
                            df,
                            pattern,
                            gmail_user = st.secrets["gmail_user"],
                            gmail_pwd  = st.secrets["gmail_pwd"],
                            subject_tpl=st.session_state["subject_tpl"],
                            intro      = st.session_state["intro"],
                            closing    = st.session_state["closing"],
                            resume_bytes=st.session_state["resume_bytes"],
                        )
                st.success(f"Done – {len(sent)} messages delivered 🚀")
                st.write(sent)

    else:
        st.info("Fill the form and press **Fetch recruiters** to continue.")
