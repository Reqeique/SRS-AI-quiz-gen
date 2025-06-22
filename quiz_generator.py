
import streamlit as st
import google.generativeai as genai
import json
import requests
import uuid
import csv
import io
import base64
import zipfile
import logging
import re
import hashlib
import pandas as pd
from datetime import datetime, timedelta
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.utils import RepositoryNotFoundError, HfHubHTTPError
from urllib.parse import unquote_plus

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Subject & Topic Data ---
SUBJECT_TOPICS = {
    "Biology": {
        
    },
    "Physics": {
        
    },
    "Math": {
        
    },
    "Chemistry": {
      
    },
    "Engineering": {},
    "Computer Science": {}
    ,
    "Humanities": {},
    "Literature": {},
    "Business": {},
    "Others": {}
}

# --- HTML Template ---
HTML_TEMPLATE = """
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Interactive Quiz</title>
<style>
body {{ font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color:#f0f2f5; color:#333; display:flex; justify-content:center; align-items:center; min-height:100vh; margin:0; padding:20px; }} #quiz-container {{ background-color:#ffffff; border-radius:10px; box-shadow:0 4px 8px rgba(0,0,0,0.1); width:100%; max-width:800px; padding:30px; }} h1 {{ color:#1e3a8a; text-align:center; margin-bottom:25px; }} .question-block {{ margin-bottom:25px; padding-bottom:20px; border-bottom:1px solid #e5e7eb; }} .question-block:last-child {{ border-bottom:none; }} .question-text {{ font-size:1.1em; font-weight:600; margin-bottom:15px; }} .options {{ display:flex; flex-direction:column; }} .option {{ margin-bottom:10px; }} .option label {{ display:flex; align-items:center; padding:10px; border-radius:5px; transition:background-color .3s, border-color .3s; border:1px solid #d1d5db; cursor:pointer; }} .option input[type="radio"] {{ display:none; }} .option .option-letter {{ font-weight:bold; margin-right:8px; color:#1e3a8a; }} .option input[type="radio"]:checked + label {{ background-color:#dbeafe; border-color:#60a5fa; }} #submit-btn, .log-results-btn {{ display:block; width:100%; padding:15px; font-size:1.2em; font-weight:bold; color:#fff; background-color:#1e3a8a; border:none; border-radius:5px; cursor:pointer; margin-top:20px; text-decoration:none; text-align:center; }} #results-container {{ margin-top:30px; text-align:center; font-size:1.5em; font-weight:bold; }} .correct-answer {{ background-color:#dcfce7 !important; border-color:#4ade80 !important; }} .incorrect-answer {{ background-color:#fee2e2 !important; border-color:#f87171 !important; }}
</style></head><body><div id="quiz-container"><h1>My Awesome Quiz</h1><form id="quiz-form">{quiz_questions_html}<button type="submit" id="submit-btn">Check Answers</button></form><div id="results-container"></div></div>
<script>
const quizData = {quiz_questions_js};
const streamlitAppUrl = "{streamlit_app_url}";
document.getElementById('quiz-form').addEventListener('submit', function(e) {{
e.preventDefault(); this.querySelector('#submit-btn').style.display = 'none'; let score = 0; const mistakes = [];
quizData.forEach((q, i) => {{ const selected = this.querySelector(`input[name="question${{i}}"]:checked`); document.querySelectorAll(`input[name="question${{i}}"]`).forEach(opt => opt.parentElement.querySelector('label').classList.remove('correct-answer', 'incorrect-answer')); const correctLabel = document.querySelector(`label[for='q${{i}}${{q.correctAnswer}}']`);
if (selected) {{ if (selected.value === q.correctAnswer) {{ score++; selected.parentElement.querySelector('label').classList.add('correct-answer'); }} else {{ selected.parentElement.querySelector('label').classList.add('incorrect-answer'); correctLabel.classList.add('correct-answer'); mistakes.push({{ subject: q.subject, topic: q.topic, question: q.question, yourAnswer: q.options[selected.value], correctAnswer: q.options[q.correctAnswer] }}); }} }} else {{ correctLabel.classList.add('correct-answer'); }} }});
const resultsContainer = document.getElementById('results-container'); resultsContainer.innerHTML = `You scored ${{score}} out of ${{quizData.length}}!`;
if (mistakes.length > 0 && streamlitAppUrl && streamlitAppUrl !== "NOT_CONFIGURED") {{
    const safeJsonString = encodeURIComponent(JSON.stringify(mistakes));
    const encodedData = btoa(safeJsonString);
    const returnUrl = `${{streamlitAppUrl}}?results=${{encodedData}}`;
    const logButton = document.createElement('a'); logButton.href = returnUrl; logButton.textContent = 'Click Here to Log Your Mistakes'; logButton.className = 'log-results-btn'; logButton.target = "_blank"; resultsContainer.appendChild(logButton);
}} }});
</script></body></html>
"""

# --- Streamlit App Setup ---
st.set_page_config(page_title="SRS Quiz Generator", layout="wide")
st.title("🧠 AI Quiz Generator with Spaced Repetition")

# --- Configuration Section ---
REQUIRED_KEYS = ["GEMINI_API_KEY", "HF_TOKEN", "NETLIFY_TOKEN", "LOG_DATASET_ID", "STREAMLIT_APP_URL"]

for key in REQUIRED_KEYS:
    if key not in st.session_state:
        st.session_state[key] = st.secrets.get(key, "")

keys_configured = all(st.session_state.get(key) for key in REQUIRED_KEYS)

with st.sidebar:
    st.header("⚙️ Configuration")
    with st.expander("Enter Your API Keys & Config", expanded=not keys_configured):
        st.info("Your credentials are only stored in this browser session.")
        
        gemini_key = st.text_input(
            "Gemini API Key", value=st.session_state.get("GEMINI_API_KEY", ""),
            type="password", help="Get from Google AI Studio."
        )
        hf_token = st.text_input(
            "Hugging Face Token (write role)", value=st.session_state.get("HF_TOKEN", ""),
            type="password", help="Get from your HF account settings -> Access Tokens."
        )
        netlify_token = st.text_input(
            "Netlify API Token", value=st.session_state.get("NETLIFY_TOKEN", ""),
            type="password", help="Create a Personal Access Token in your Netlify User settings -> Applications."
        )
        log_dataset_id = st.text_input(
            "Hugging Face Dataset ID", value=st.session_state.get("LOG_DATASET_ID", ""),
            help="The name for your data repository, e.g., 'YourUsername/MyQuizData'. It will be created if it doesn't exist."
        )
        st_app_url = st.text_input(
            "Streamlit App URL", value=st.session_state.get("STREAMLIT_APP_URL", ""),
            help="The full URL of this running Streamlit app. Required for quiz result callbacks."
        )

        if st.button("Save Configuration"):
            st.session_state["GEMINI_API_KEY"] = gemini_key
            st.session_state["HF_TOKEN"] = hf_token
            st.session_state["NETLIFY_TOKEN"] = netlify_token
            st.session_state["LOG_DATASET_ID"] = log_dataset_id
            st.session_state["STREAMLIT_APP_URL"] = st_app_url
            # --- CHANGE: Clear caches when config changes to be safe ---
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Configuration saved! The app will now re-initialize.")
            st.rerun()

if not keys_configured:
    st.warning("Please enter and save your configuration in the sidebar to start using the app. 👆")
    st.info(
        """
        **Why are these keys needed?**
        - **Gemini API Key**: To parse your raw text into structured quiz questions using AI.
        - **Hugging Face Token & Dataset ID**: To create a private dataset on the Hugging Face Hub where your quizzes and spaced repetition data will be permanently stored under your account.
        - **Netlify API Token**: To automatically create and deploy a public, shareable website with your quizzes.
        - **Streamlit App URL**: The URL of *this* app, which the deployed quiz website needs to send results back for processing into your spaced repetition deck.
        """
    )
    st.stop()

# --- Define Keys and Initialize APIs ---
GEMINI_API_KEY = st.session_state["GEMINI_API_KEY"]
LOG_DATASET_ID = st.session_state["LOG_DATASET_ID"]
STREAMLIT_APP_URL = st.session_state["STREAMLIT_APP_URL"]
HF_TOKEN = st.session_state["HF_TOKEN"]
NETLIFY_TOKEN = st.session_state["NETLIFY_TOKEN"]
QUIZZES_DIR = "quizzes"
LOG_FILENAME = "srs_deck.csv"
STATS_FILENAME = "user_stats.json"

hf_api = HfApi(token=HF_TOKEN)

# --- Helper Functions ---

# --- CHANGE: Pass config as arguments to cached functions ---
@st.cache_resource
def initial_setup(log_dataset_id, hf_token, netlify_token):
    """Ensures both HF Dataset and Netlify Site exist, creating them if needed."""
    try:
        hf_api.dataset_info(repo_id=log_dataset_id, token=hf_token)
    except RepositoryNotFoundError:
        st.info(f"First-time setup: Creating Hugging Face Dataset '{log_dataset_id}'...")
        hf_api.create_repo(repo_id=log_dataset_id, repo_type="dataset", private=True, token=hf_token)
        srs_header = "Card_ID,Question,CorrectAnswer,Subject,Topic,Review_Date,Interval,Ease_Factor,Repetitions\n"
        hf_api.upload_file(path_or_fileobj=srs_header.encode('utf-8'), path_in_repo=LOG_FILENAME, repo_id=log_dataset_id, repo_type="dataset", token=hf_token, commit_message="Initialize SRS deck")
        stats_initial = {"xp": 0, "streak": 0, "streak_last_active_date": "1970-01-01"}
        hf_api.upload_file(path_or_fileobj=json.dumps(stats_initial).encode('utf-8'), path_in_repo=STATS_FILENAME, repo_id=log_dataset_id, repo_type="dataset", token=hf_token, commit_message="Initialize user stats")
        hf_api.upload_file(path_or_fileobj=b"", path_in_repo=f"{QUIZZES_DIR}/.gitkeep", repo_id=log_dataset_id, repo_type="dataset", token=hf_token, commit_message="Initialize quizzes directory")
        st.success("Hugging Face setup complete.")

    SITE_ID_FILENAME = "netlify_site_id.txt"
    try:
        local_path = hf_hub_download(repo_id=log_dataset_id, repo_type="dataset", filename=SITE_ID_FILENAME, token=hf_token)
        with open(local_path, 'r') as f: site_id = f.read().strip()
        if site_id: return site_id
        else: raise FileNotFoundError
    except HfHubHTTPError as e:
        if e.response.status_code != 404:
            st.error(f"HTTP error fetching site ID: {e}"); return None
        st.info("First-time setup: Creating a persistent quiz website on Netlify...")
        headers = {"Authorization": f"Bearer {netlify_token}"}
        create_site_url = "https://api.netlify.com/api/v1/sites"
        try:
            response = requests.post(create_site_url, headers=headers)
            response.raise_for_status()
            new_site_id = response.json().get('site_id')
            if not new_site_id: st.error("Netlify returned no site_id."); return None
            hf_api.upload_file(path_or_fileobj=new_site_id.encode('utf-8'), path_in_repo=SITE_ID_FILENAME, repo_id=log_dataset_id, repo_type="dataset", token=hf_token, commit_message="Add Netlify site ID")
            st.success("Your personal quiz website has been created!")
            return new_site_id
        except Exception as create_err: st.error(f"Failed to create Netlify site: {create_err}"); return None

# --- CHANGE: Pass config as arguments ---
@st.cache_data(ttl=300)
def load_srs_deck(log_dataset_id, hf_token):
    srs_deck_columns = ["Card_ID","Question","CorrectAnswer","Subject","Topic","Review_Date","Interval","Ease_Factor","Repetitions"]
    try:
        local_path = hf_hub_download(repo_id=log_dataset_id, filename=LOG_FILENAME, repo_type="dataset", token=hf_token)
        return pd.read_csv(local_path)
    except HfHubHTTPError as e:
        if e.response.status_code == 404:
            logging.warning("srs_deck.csv not found. Returning an empty DataFrame.")
            return pd.DataFrame(columns=srs_deck_columns)
        else:
            st.error(f"Could not load SRS deck due to HTTP error: {e}")
            return pd.DataFrame(columns=srs_deck_columns)
    except Exception as e:
        st.error(f"Could not load SRS deck: {e}")
        return pd.DataFrame(columns=srs_deck_columns)

def save_srs_deck(df):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    hf_api.upload_file(path_or_fileobj=csv_buffer.getvalue().encode('utf-8'), path_in_repo=LOG_FILENAME, repo_id=LOG_DATASET_ID, repo_type="dataset", token=HF_TOKEN, commit_message="Update SRS deck")
    st.cache_data.clear()

# --- CHANGE: Pass config as arguments ---
@st.cache_data(ttl=300)
def load_user_stats(log_dataset_id, hf_token):
    try:
        local_path = hf_hub_download(repo_id=log_dataset_id, filename=STATS_FILENAME, repo_type="dataset", token=hf_token)
        with open(local_path, 'r') as f: return json.load(f)
    except Exception: return {"xp": 0, "streak": 0, "streak_last_active_date": "1970-01-01"}

def save_user_stats(stats):
    hf_api.upload_file(path_or_fileobj=json.dumps(stats).encode('utf-8'), path_in_repo=STATS_FILENAME, repo_id=LOG_DATASET_ID, repo_type="dataset", token=HF_TOKEN, commit_message="Update user stats")
    st.cache_data.clear()

def update_streak_and_xp(xp_to_add=0):
    # --- CHANGE: Pass config to the load function ---
    stats = load_user_stats(LOG_DATASET_ID, HF_TOKEN)
    today_str = datetime.now().strftime('%Y-%m-%d')
    last_active_date_str = stats.get('streak_last_active_date', '1970-01-01')
    
    if last_active_date_str != today_str:
        last_active_date = datetime.strptime(last_active_date_str, '%Y-%m-%d').date()
        if (datetime.now().date() - last_active_date).days == 1:
            stats['streak'] += 1
        else:
            stats['streak'] = 1
        stats['streak_last_active_date'] = today_str

    stats['xp'] += xp_to_add
    save_user_stats(stats)
    return stats

def calculate_srs_update(card, rating):
    card['Repetitions'] = int(card.get('Repetitions', 0))
    card['Ease_Factor'] = float(card.get('Ease_Factor', 2.5))
    card['Interval'] = int(card.get('Interval', 0))

    if rating == 'Hard':
        card['Repetitions'] = 0
        card['Interval'] = 1
        card['Ease_Factor'] = max(1.3, card['Ease_Factor'] - 0.2)
    else:
        if card['Repetitions'] == 0: card['Interval'] = 1
        elif card['Repetitions'] == 1: card['Interval'] = 6
        else: card['Interval'] = round(card['Interval'] * card['Ease_Factor'])
        card['Repetitions'] += 1
        if rating == 'Easy': card['Ease_Factor'] += 0.15

    card['Review_Date'] = (datetime.now() + timedelta(days=card['Interval'])).strftime('%Y-%m-%d')
    return card

def save_quiz_data_to_hf(quiz_uuid, quiz_data):
    try:
        path_in_repo = f"{QUIZZES_DIR}/{quiz_uuid}.json"; quiz_data_bytes = json.dumps(quiz_data, indent=2).encode('utf-8')
        hf_api.upload_file(path_or_fileobj=quiz_data_bytes, path_in_repo=path_in_repo, repo_id=LOG_DATASET_ID, repo_type="dataset", token=HF_TOKEN, commit_message=f"Add quiz {quiz_uuid}"); return True
    except Exception as e: st.error(f"Failed to save quiz data: {e}"); return False

def get_all_quizzes_from_hf():
    try:
        all_repo_files = hf_api.list_repo_files(repo_id=LOG_DATASET_ID, repo_type="dataset", token=HF_TOKEN)
        quiz_files = [f for f in all_repo_files if f.startswith(f"{QUIZZES_DIR}/") and f.endswith('.json')]
        all_quizzes = {}
        for file_path in quiz_files:
            quiz_uuid = file_path.split('/')[-1].replace('.json', '')
            local_path = hf_hub_download(repo_id=LOG_DATASET_ID, repo_type="dataset", filename=file_path, token=HF_TOKEN)
            with open(local_path, 'r', encoding='utf-8') as f: all_quizzes[quiz_uuid] = json.load(f)
        return all_quizzes
    except Exception as e: st.error(f"Could not retrieve existing quizzes: {e}"); return None

def deploy_full_site_to_netlify(site_id, all_quizzes, streamlit_app_url):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        homepage_links = ""; sorted_quizzes = sorted(all_quizzes.items(), key=lambda item: item[0], reverse=True)
        for quiz_uuid, quiz_data in sorted_quizzes:
            quiz_title = quiz_data[0].get('question', f"Quiz {quiz_uuid}")[:60] + "..."; quiz_subject = quiz_data[0].get('subject', 'General')
            homepage_links += f'<li><a href="/quizzes/{quiz_uuid}">{quiz_title}</a> <em>({quiz_subject})</em></li>\n'
        homepage_html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>My Quiz Collection</title><style>body{{font-family:sans-serif; max-width:800px; margin:40px auto; padding:20px;}} li{{margin-bottom:10px;}}</style></head><body><h1>All Quizzes</h1><ul>{homepage_links}</ul></body></html>"""
        zf.writestr("index.html", homepage_html)
        for quiz_uuid, quiz_data in all_quizzes.items():
            quiz_subject = quiz_data[0].get('subject', 'General'); quiz_html = generate_quiz_html_string(quiz_data, quiz_subject, streamlit_app_url)
            zf.writestr(f"quizzes/{quiz_uuid}.html", quiz_html)
        zf.writestr("_redirects", "/quizzes/:id /quizzes/:id.html 200")
    zip_buffer.seek(0)
    headers = {"Content-Type": "application/zip", "Authorization": f"Bearer {NETLIFY_TOKEN}"}
    deploy_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
    try: response = requests.post(deploy_url, headers=headers, data=zip_buffer.read()); response.raise_for_status(); return True
    except Exception as e: st.error(f"Failed to deploy to Netlify: {e}"); return False

def generate_quiz_html_string(quiz_data, subject, app_url):
    if not subject: return "Error: Subject not provided."
    quiz_data_copy = json.loads(json.dumps(quiz_data))
    for q in quiz_data_copy: q['subject'] = subject
    return HTML_TEMPLATE.format(quiz_questions_html="".join([f"""<div class="question-block"><div class="question-text">{i+1}. ({q.get('topic', 'General')}) {q['question']}</div><div class="options">{''.join([f'<div class="option"><input type="radio" id="q{i}{l}" name="question{i}" value="{l}"><label for="q{i}{l}"><span class="option-letter">{l}.</span>{t}</label></div>' for l, t in sorted(q['options'].items())])}</div></div>""" for i, q in enumerate(quiz_data_copy)]), quiz_questions_js=json.dumps(quiz_data_copy), streamlit_app_url=app_url)

def parse_questions_with_gemini(api_key, text, subject):
    try:
        genai.configure(api_key=api_key); model = genai.GenerativeModel('gemini-1.5-flash')
        has_predefined_topics = bool(SUBJECT_TOPICS.get(subject))
        topic_instruction = f"2. Classify each question into one of the provided topics for '{subject}'. You MUST choose a topic EXACTLY from this list:\n{''.join([f'- \\"{tn}\\"\\n' for tn in SUBJECT_TOPICS[subject]])}" if has_predefined_topics else "2. Assign a relevant 'topic' to each question by inferring a short, descriptive name."
        prompt = f"""
          You are an expert in '{subject}' and an expert quiz parser. Your task is to convert the plain text quiz content below into a valid JSON array of objects.
          For each question in the text, you will create a corresponding JSON object with four keys: "question", "options", "correctAnswer", and "topic".
          *** YOUR PRIMARY DIRECTIVE: DETERMINE THE CORRECT ANSWER ***
          You must act as a subject matter expert. For each question:
          1.  First, check if one of the options in the input text is marked with an asterisk (*). If it is, that is the correct answer.
          2.  If NO asterisk is provided, you MUST use your own knowledge of '{subject}' to determine which of the provided options is the correct one.
          3.  The "correctAnswer" key's value in your JSON output must ALWAYS be the letter (e.g., "A", "B", "C") corresponding to the correct option you identified.
          JSON FORMATTING RULES:
          - The "options" key's value MUST be a JSON object (a dictionary), where keys are the option letters and values are the option text strings. Example: "options": {{"A": "Paris", "B": "London"}}
          - {topic_instruction}
          Here is the text to parse: --- {text} --- Return ONLY the raw JSON array, with no other text or formatting.
        """
        response = model.generate_content(prompt)
        match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if match: return json.loads(match.group(0))
        else: st.error("Failed to parse from Gemini: Could not find JSON array."); return None
    except Exception as e: st.error(f"Failed to parse from Gemini: {e}"); return None

# --- Main Streamlit App Logic ---

for key in ['app_state', 'sharable_link', 'review_cards', 'current_card_index', 'show_answer']:
    if key not in st.session_state: st.session_state[key] = None
if st.session_state.app_state is None: st.session_state.app_state = 'input'
if st.query_params.get("results"): st.session_state.app_state = 'log_results'

def reset_app():
    st.query_params.clear()
    for key in ['sharable_link', 'review_cards', 'current_card_index', 'show_answer']: st.session_state[key] = None
    st.session_state.app_state = 'input'

# --- CHANGE: Pass config arguments to the initial setup call ---
NETLIFY_SITE_ID = initial_setup(LOG_DATASET_ID, HF_TOKEN, NETLIFY_TOKEN)
if not NETLIFY_SITE_ID:
    st.error("Could not complete initial setup. Please check your tokens, permissions, and dataset ID format."); st.stop()

with st.sidebar:
    st.divider()
    st.header("Your Progress")
    stats = update_streak_and_xp(xp_to_add=0)
    st.metric("Experience Points (XP)", f"{stats.get('xp', 0)} ✨")
    st.metric("Daily Streak", f"{stats.get('streak', 0)} 🔥")
    st.divider()
    st.header("Today's Review")
    # --- CHANGE: Pass config arguments to the load function ---
    srs_deck = load_srs_deck(LOG_DATASET_ID, HF_TOKEN)
    if not srs_deck.empty:
        srs_deck['Review_Date'] = pd.to_datetime(srs_deck['Review_Date']).dt.date
        due_cards = srs_deck[srs_deck['Review_Date'] <= datetime.now().date()]
        st.metric("Cards Due Today", len(due_cards))
        if not due_cards.empty and st.session_state.app_state != 'review_session' and st.button("🚀 Start Review Session", type="primary"):
            st.session_state.review_cards = due_cards.to_dict('records')
            st.session_state.current_card_index = 0
            st.session_state.show_answer = False
            st.session_state.app_state = 'review_session'
            st.rerun()
    else:
        st.write("Your review deck is empty. Make some mistakes to add cards!")


if st.session_state.app_state == 'input':
    st.header("Step 1: Create a New Quiz")
    selected_subject = st.selectbox("Select the subject:", options=list(SUBJECT_TOPICS.keys()))
    raw_text = st.text_area("Paste your quiz content here (mark correct answer with *):", height=250)
    if st.button("🚀 Generate & Add Quiz to Website", type="primary"):
        if not raw_text or not selected_subject: st.warning("Please select a subject and paste questions.")
        else:
            with st.spinner("🤖 Asking AI to parse your quiz..."): new_quiz_data = parse_questions_with_gemini(GEMINI_API_KEY, raw_text, selected_subject)
            if new_quiz_data:
                for q in new_quiz_data: q['subject'] = selected_subject
                quiz_uuid = str(uuid.uuid4())
                with st.spinner("💾 Saving new quiz data..."):
                    if not save_quiz_data_to_hf(quiz_uuid, new_quiz_data): st.stop()
                with st.spinner("📚 Retrieving all quizzes..."):
                    all_quizzes = get_all_quizzes_from_hf()
                    if all_quizzes is None: st.stop()
                with st.spinner("🚀 Deploying updated website..."):
                    if not deploy_full_site_to_netlify(NETLIFY_SITE_ID, all_quizzes, STREAMLIT_APP_URL): st.stop()
                site_info_url = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}"
                site_info = requests.get(site_info_url, headers={"Authorization": f"Bearer {NETLIFY_TOKEN}"}).json()
                site_url = site_info.get("ssl_url") or site_info.get("url")
                st.session_state.sharable_link = f"{site_url}/quizzes/{quiz_uuid}"
                st.session_state.app_state = 'show_link'
                update_streak_and_xp(xp_to_add=10)
                st.rerun()

elif st.session_state.app_state == 'show_link':
    st.header("✅ Success!"); st.success("Your new quiz has been added to your persistent website.")
    st.info("The link below goes directly to your new quiz:"); st.code(st.session_state.sharable_link)
    base_url = st.session_state.sharable_link.split('/quizzes/')[0]
    st.markdown(f"**[View your quiz collection homepage]({base_url})**")
    if st.button("➕ Create Another Quiz"): reset_app(); st.rerun()

elif st.session_state.app_state == 'log_results':
    st.header("✅ Processing Quiz Results...")
    try:
        encoded_data = st.query_params.get("results"); decoded_b64 = base64.b64decode(encoded_data)
        mistakes = json.loads(unquote_plus(decoded_b64.decode('utf-8')))
    except Exception: mistakes = []
    if mistakes:
        # --- CHANGE: Pass config arguments to the load function ---
        deck_df = load_srs_deck(LOG_DATASET_ID, HF_TOKEN)
        if 'Card_ID' in deck_df.columns: deck_df['Card_ID'] = deck_df['Card_ID'].astype(str)
        new_cards_count = 0
        for mistake in mistakes:
            card_id = hashlib.md5(mistake['question'].encode()).hexdigest()
            if 'Card_ID' not in deck_df.columns or card_id not in deck_df['Card_ID'].values:
                new_card = {"Card_ID": card_id, "Question": mistake['question'], "CorrectAnswer": mistake['correctAnswer'], "Subject": mistake['subject'], "Topic": mistake['topic'], "Review_Date": datetime.now().strftime('%Y-%m-%d'), "Interval": 0, "Ease_Factor": 2.5, "Repetitions": 0}
                deck_df = pd.concat([deck_df, pd.DataFrame([new_card])], ignore_index=True)
                new_cards_count += 1
        save_srs_deck(deck_df)
        st.success(f"Mistakes processed. {new_cards_count} new review cards added!"); st.balloons()
    else: st.info("No mistakes to log. Great job!")
    if st.button("⬅️ Back to Start"): reset_app(); st.rerun()

elif st.session_state.app_state == 'review_session':
    st.header("🧠 Review Session")
    if st.session_state.review_cards and st.session_state.current_card_index is not None and st.session_state.current_card_index < len(st.session_state.review_cards):
        card = st.session_state.review_cards[st.session_state.current_card_index]
        st.progress((st.session_state.current_card_index + 1) / len(st.session_state.review_cards))
        st.subheader(f"Question {st.session_state.current_card_index + 1} of {len(st.session_state.review_cards)}")
        st.markdown(f"**{card['Question']}**"); st.caption(f"Topic: {card['Topic']}")
        if st.session_state.show_answer:
            st.success(f"**Answer:** {card['CorrectAnswer']}"); st.write("---"); st.write("How well did you remember this?")
            c1, c2, c3 = st.columns(3)
            if c1.button("😭 Hard", key=f"hard_{card['Card_ID']}"):
                card = calculate_srs_update(card, 'Hard'); st.session_state.review_cards[st.session_state.current_card_index] = card
                st.session_state.current_card_index += 1; st.session_state.show_answer = False; st.rerun()
            if c2.button("🙂 Good", key=f"good_{card['Card_ID']}"):
                card = calculate_srs_update(card, 'Good'); st.session_state.review_cards[st.session_state.current_card_index] = card
                update_streak_and_xp(xp_to_add=5)
                st.session_state.current_card_index += 1; st.session_state.show_answer = False; st.rerun()
            if c3.button("😎 Easy", key=f"easy_{card['Card_ID']}"):
                card = calculate_srs_update(card, 'Easy'); st.session_state.review_cards[st.session_state.current_card_index] = card
                update_streak_and_xp(xp_to_add=10)
                st.session_state.current_card_index += 1; st.session_state.show_answer = False; st.rerun()
        else:
            if st.button("Show Answer"): st.session_state.show_answer = True; st.rerun()
    else:
        st.header("🎉 Review Complete!"); st.success("You've finished your review session for today!")
        with st.spinner("Saving your progress..."):
            # --- CHANGE: Pass config arguments to the load function ---
            deck_df = load_srs_deck(LOG_DATASET_ID, HF_TOKEN)
            if 'Card_ID' in deck_df.columns: deck_df['Card_ID'] = deck_df['Card_ID'].astype(str)
            for card in st.session_state.review_cards:
                card_id_str = str(card['Card_ID'])
                deck_df.loc[deck_df['Card_ID'] == card_id_str, ['Review_Date', 'Interval', 'Ease_Factor', 'Repetitions']] = [card['Review_Date'], card['Interval'], card['Ease_Factor'], card['Repetitions']]
            save_srs_deck(deck_df)
            update_streak_and_xp(xp_to_add=25)
        if st.button("Back to Main Page"): reset_app(); st.rerun()