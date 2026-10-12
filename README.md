# DeadlineMate AI – Smart Academic Deadline Tracker

## About the Project
DeadlineMate AI is an AI-powered web application that helps students organize and track academic deadlines. It uses Google Gemini AI to extract deadline information from text and uploaded academic documents and displays the results in a dashboard.

## Features
- Extract academic deadlines from text.
- Upload academic documents and identify deadline information.
- View extracted deadlines in a dashboard.
- Send deadline summaries through Telegram notifications.
- Track upcoming deadlines.

## Technologies Used
- Python
- Streamlit
- Google Gemini AI
- Telegram Bot API
- Pandas

## Project Setup

### 1. Clone the Repository
```bash
git clone https://github.com/KSruthi-15/smart-academic-deadline-tracker.git
cd smart-academic-deadline-tracker
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
```

On Linux/macOS:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Secrets
Create `.streamlit/secrets.toml` and configure your Gemini API key, model, Telegram bot token, and Telegram chat ID.

**Important:** Never commit API keys or bot tokens to GitHub.

### 5. Run the Application
```bash
streamlit run app.py
```

## GitHub Repository
https://github.com/KSruthi-15/smart-academic-deadline-tracker

## Future Improvements
- Conversational AI assistant for academic deadlines.
- Automatic reminders for upcoming deadlines.
- Improved deadline prioritization and scheduling.
