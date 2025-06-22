---
title: AI-Powered SRS Quiz Generator
emoji: 🧠
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.35.0"
app_file: quiz_generator.py
pinned: false
---

# 🧠 AI-Powered SRS Quiz Generator

Instantly transform any text into interactive, shareable quizzes and a personal study deck. This application leverages the power of Google's Gemini AI for intelligent content parsing, Hugging Face Hub for persistent data storage, and Netlify for one-click deployment of your quizzes to the web.

**[🚀 Try the Live Demo](https://huggingface.co/spaces/AnaniyaX/SRS-AI-quiz-gen)**
<br>
[Deploy to Spaces](https://huggingface.co/spaces/AnaniyaX/SRS-AI-quiz-gen?duplicate=true)

---

## ✨ Core Features

*   **🤖 AI-Powered Parsing**: Simply paste your raw questions and answers. The Gemini API intelligently structures it into a valid quiz format, even determining the correct answer if you forget to mark it.
*   **🔁 Spaced Repetition System (SRS)**: Don't just take quizzes—learn from them. Every mistake you make is automatically converted into a flashcard and added to a personal review deck, using an SM-2 inspired algorithm to schedule future reviews.
*   **🚀 Automatic Web Deployment**: With a single click, your new quiz is deployed to a persistent, public website on Netlify, complete with a homepage listing all your quizzes.
*   **🔐 Private & Persistent Storage**: All your quiz data and SRS progress are stored securely and privately in a Hugging Face Dataset under your own account. You own your data.
*   **🎮 Gamified Learning**: Stay motivated with Experience Points (XP) and a Daily Streak tracker for completing quizzes and review sessions.
*   **Open & Self-Hosted**: Designed to run on Hugging Face Spaces. Just provide your own API keys, and you're in full control.

## 🚀 Getting Started

You have three main options to use this application, from easiest to most advanced:

### Option 1: Try the Live Demo

The quickest way to see the app in action. No setup is required. Note that data created in the public demo may be periodically cleared.

**[➡️ Click here to access the Live Demo](https://huggingface.co/spaces/AnaniyaX/SRS-AI-quiz-gen)**

### Option 2: Duplicate the Space (Recommended)

Create your own private copy of this application on Hugging Face. This is the best way to have your own persistent quiz library.

1.  Click the **[Deploy to Spaces](https://huggingface.co/spaces/AnaniyaX/SRS-AI-quiz-gen?duplicate=true)** button.
2.  Hugging Face will create a new Space under your account. Choose a name and select "Private" if you wish.
3.  In your new Space's settings, go to **Settings > Secrets**.
4.  Add the following as repository secrets:
    *   `GEMINI_API_KEY`
    *   `HF_TOKEN` (with `write` permissions)
    *   `NETLIFY_TOKEN`
5.  The Space will build, and you can launch the app. It will guide you through entering the remaining configuration (like your desired HF Dataset ID) in the sidebar.

### Option 3: Run Locally 
Run the application on your own machine for development or offline use.

1.  **Prerequisites**: Ensure you have Python 3.9+ installed.
2.  **Clone the repository:**
    ```bash
    git clone https://github.com/Reqeique/SRS-AI-quiz-gen.git
    cd SRS-AI-quiz-gen
    ```
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Streamlit app:**
    ```bash
    streamlit run quiz_generator.py
    ```
5.  **Configure in Sidebar**: Open the app in your browser and enter all the required keys and configuration values in the sidebar.

## ⚙️ How It Works: The Tech Flow

1.  **Input**: A user pastes raw text into the **Streamlit** interface.
2.  **AI Parsing**: The text is sent to the **Google Gemini API**, which returns a structured JSON object for the quiz.
3.  **Persistent Storage**: The new quiz JSON and the user's updated SRS deck (`srs_deck.csv`) are saved to a private **Hugging Face Dataset**.
4.  **Deployment**: The app generates all necessary HTML files and deploys the entire quiz site to **Netlify** via their API.
5.  **Interaction**: The user takes the quiz on the public Netlify site.
6.  **Feedback Loop**: Upon completion, the quiz results (mistakes) are sent back to the Streamlit app to update the SRS deck.

## 🛠️ Technology Stack

*   **Frontend**: [Streamlit](https://streamlit.io/)
*   **AI Model**: [Google Gemini](https://deepmind.google/technologies/gemini/)
*   **Data Storage**: [Hugging Face Hub (Datasets)](https://huggingface.co/docs/hub/datasets-overview)
*   **Web Hosting**: [Netlify](https://www.netlify.com/)
*   **Core Libraries**: `pandas`, `requests`, `huggingface-hub`

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.