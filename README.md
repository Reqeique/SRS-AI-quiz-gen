---
title: AI-Powered SRS Quiz Generator
emoji: 🧠
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.35.0" # 
app_file: quiz_generator.py
pinned: false
---
# 🧠 AI-Powered SRS Quiz Generator

Instantly transform any text into interactive, shareable quizzes and a personal study deck. This application leverages the power of Google's Gemini AI for intelligent content parsing, Hugging Face Hub for persistent data storage, and Netlify for one-click deployment of your quizzes to the web.

---

## ✨ Core Features

*   **🤖 AI-Powered Parsing**: Simply paste your raw questions and answers. The Gemini API intelligently structures it into a valid quiz format, even determining the correct answer if you forget to mark it.
*   **🔁 Spaced Repetition System (SRS)**: Don't just take quizzes—learn from them. Every mistake you make is automatically converted into a flashcard and added to a personal review deck, using an SM-2 inspired algorithm to schedule future reviews.
*   **🚀 Automatic Web Deployment**: With a single click, your new quiz is deployed to a persistent, public website on Netlify, complete with a homepage listing all your quizzes.
*   **🔐 Private & Persistent Storage**: All your quiz data and SRS progress are stored securely and privately in a Hugging Face Dataset under your own account. You own your data.
*   **🎮 Gamified Learning**: Stay motivated with Experience Points (XP) and a Daily Streak tracker for completing quizzes and review sessions.
*   **Open & Self-Hosted**: Designed to run on Hugging Face Spaces or locally. Just provide your own API keys, and you're in full control. No data is shared with the app developer.

## ⚙️ How It Works: The Tech Flow

This application seamlessly integrates several services to create a powerful learning loop:

1.  **Input**: A user pastes raw text into the **Streamlit** interface.
2.  **AI Parsing**: The text is sent to the **Google Gemini API**, which returns a structured JSON object for the quiz.
3.  **Persistent Storage**: The new quiz JSON and the user's updated SRS deck (`srs_deck.csv`) are saved to a private **Hugging Face Dataset**.
4.  **Deployment**: The app generates all necessary HTML files and deploys the entire quiz site to **Netlify** via their API.
5.  **Interaction**: The user takes the quiz on the public Netlify site.
6.  **Feedback Loop**: Upon completion, the quiz results (specifically, the mistakes) are encoded and sent back to the original Streamlit app via a URL query parameter.
7.  **Learning**: The Streamlit app logs the mistakes, adding them as new cards to the user's SRS deck on Hugging Face Hub for future review.

## 🚀 Getting Started

You can run this application locally or deploy it as a Hugging Face Space.

### Prerequisites

You will need the following API keys and credentials:

*   **Google Gemini API Key**: Get one from [Google AI Studio](https://aistudio.google.com/app/apikey).
*   **Hugging Face User Access Token**: Create a token with `write` permissions in your [HF Account Settings](https://huggingface.co/settings/tokens).
*   **Netlify Personal Access Token**: Create one in your [Netlify User Settings](https://app.netlify.com/user/applications).

### Running on Hugging Face Spaces (Recommended)

1.  Click the "Deploy on Spaces" button or duplicate this repository to your own Hugging Face account.
2.  Choose "Streamlit" as the Space SDK.
3.  In your new Space's settings, go to "Secrets" and add your `GEMINI_API_KEY`, `HF_TOKEN`, and `NETLIFY_TOKEN`. The app will read these automatically.
4.  Launch the app! It will guide you through entering the remaining configuration (like your desired HF Dataset ID) in the sidebar.

### Running Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Reqeique/SRS-AI-quiz-gen.git
    cd SRS-AI-quiz-gen
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit app:**
    ```bash
    streamlit run quiz_generator.py
    ```

4.  **Configure in Sidebar**: Open the app in your browser and enter all the required keys and configuration values in the sidebar.

## 🛠️ Technology Stack

*   **Frontend**: [Streamlit](https://streamlit.io/)
*   **AI Model**: [Google Gemini](https://deepmind.google/technologies/gemini/)
*   **Data Storage**: [Hugging Face Hub (Datasets)](https://huggingface.co/docs/hub/datasets-overview)
*   **Web Hosting**: [Netlify](https://www.netlify.com/)
*   **Core Libraries**: `pandas`, `requests`, `huggingface-hub`

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
