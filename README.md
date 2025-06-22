# Recruiter Radar 💌

> AI-powered Streamlit dashboard that **finds recruiter names + infers e-mail patterns** and can (optionally) bulk-send personalised messages with your résumé attached.

&nbsp;

---

## ✨ Features
* **Pattern inference** – GPT-4.1 guesses  email format - `{first}.{last}@company.com` etc.  
* **Recruiter scrape** – Google Programmable Search returns LinkedIn “university recruiter” titles.  
* **Bulk e-mail** – SMTP via Gmail App Password (demo-mode checkbox prevents real sends).  
* **Session-state UI** – Names & pattern persist, no accidental reruns.  
* **One-click CSV** – Download the recruiter list for offline use.  

---

## 🖥️ Local setup

```bash
# 1. clone
git clone https://github.com/sherinegeorge21/RecruiterRadar.git
cd RecruiterRadar

# 2. create env & install
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt          # streamlit, openai, requests, python-dotenv, ...

# 3. add API keys
cp .env.example .env          # edit with OPENAI_API_KEY, GOOGLE_CUSTOM_SEARCH_API_KEY
cp .streamlit/secrets.example.toml .streamlit/secrets.toml  # edit Gmail creds

# 4. run
streamlit run app.py
