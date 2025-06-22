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
```

## 🔐 Credentials & secrets
All private keys are kept in two local files:

| File                          | What goes here                         | Used by                           |
| ----------------------------- | -------------------------------------- | --------------------------------- |
| **`.env`**                    | OpenAI + Google search tokens          | 🧠 LLM calls & recruiter scraping |
| **`.streamlit/secrets.toml`** | Gmail username + 16-digit App Password | 📧 SMTP sender                    |


Both files are already in .gitignore, so you’re safe to commit the repo.

1. Create each key/password

| Purpose                                | Where to generate                                                                            | Docs                         |
| -------------------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------- |
| **OpenAI API key**                     | [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys) | ([platform.openai.com][1])   |
| **Google Programmable Search API key** | Google Cloud Console → “API & Services > Credentials > API key”                              | ([developers.google.com][2]) |
| **Google CX ID** (engine ID)           | Programmable Search → your search engine → *Setup* tab → **Search engine ID**                | ([stackoverflow.com][3])     |
| **Gmail App Password**                 | Google Account → Security → **App passwords** → pick “Mail”                                  | ([support.google.com][4])    |

[1]: https://platform.openai.com/account/api-keys?utm_source=chatgpt.com "Account API Keys - OpenAI Platform"
[2]: https://developers.google.com/custom-search/v1/introduction?utm_source=chatgpt.com "Custom Search JSON API: Introduction - Google for Developers"
[3]: https://stackoverflow.com/questions/6562125/getting-a-cx-id-for-custom-search-google-api-python?utm_source=chatgpt.com "Getting a cx ID for custom search, Google API - Python"
[4]: https://support.google.com/mail/answer/185833?hl=en&utm_source=chatgpt.com "Sign in with app passwords - Gmail Help"




Why an App Password? Google blocks normal passwords for SMTP; a 16-digit App Password bypasses that while 2-Step-Verification stays on. 


2. Edit .env
OPENAI_API_KEY=sk-...
GOOGLE_CUSTOM_SEARCH_API_KEY=AIza...
GOOGLE_CX_ID=96dc113b3b8004369
load_dotenv() in the code automatically picks these up. 

3. Edit .streamlit/secrets.toml
gmail_user = "your.name@gmail.com"
gmail_pwd  = "abcd efgh ijkl mnop"  # 16-digit App Password

Streamlit injects st.secrets["gmail_user"] and st.secrets["gmail_pwd"] at runtime; they never leave your machine or Streamlit Cloud’s encrypted store. 

4. Change the visible sender (optional)
Open emailer.py and edit the header:

msg["From"] = msg["Reply-To"] = st.secrets["gmail_user"]

You can swap in an alias like "Sherine George <jobs@mydomain.com>" — just keep gmail_user and gmail_pwd pointing to a real mailbox for authentication.

