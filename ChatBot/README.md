# PustakaBot AI — Terminal Edition

A simple terminal chatbot powered by Google's Gemini API. It keeps conversation history in a local JSON file, supports Indonesian and English prompts, uses recent messages as context, performs lightweight bilingual sentiment detection, and provides basic analytics.

## 1. Requirements

- Python 3.10 or newer
- A Gemini API key from <https://aistudio.google.com/apikey>
- Internet connection when chatting with Gemini

## 2. Install

Run these commands from the repository root:

```bash
python -m venv ChatBot/.venv
```

Windows PowerShell:

```powershell
.\ChatBot\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
ChatBot\.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
source ChatBot/.venv/bin/activate
```

Install packages:

```bash
python -m pip install -r ChatBot/requirements.txt
```

## 3. Configure Gemini

1. Copy `ChatBot/.env.example` and name the copy `ChatBot/.env`.
2. Open `.env` and replace `put_your_api_key_here` with your Gemini API key.
3. Save the file. Do not share or commit `.env`.

Example:

```env
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-3.8-flash
MAX_CONTEXT_MESSAGES=12
```

## 4. Run

```bash
python -m ChatBot.app
```

## 5. Commands

| Command | Description |
|---|---|
| `/help` | Show available commands |
| `/history` | Show the latest saved messages |
| `/analytics` | Show message counts, sentiment groups, average length and common words |
| `/rupiah 1500000` | Format a number as Rupiah |
| `/clear` | Delete the current saved conversation |
| `/exit` | Exit the chatbot |

Conversation data is saved in `ChatBot/chat_history.json`. `/clear` removes the
saved conversation.

## 6. Shared functional library

The chatbot imports the single shared `fplib.py` from the repository root.
Its utilities support input cleanup, history filtering, context construction,
analytics, and Rupiah formatting. The library's unit tests are in the root
`test_fplib.py`; chatbot-specific offline tests are in `ChatBot/test_app.py`.

## 7. Notes

- Sentiment analysis is a simple keyword-based estimate, not a trained sentiment model.
- Gemini responses require an API key, internet access, and an available API quota.
- Recent conversation context is sent to Gemini; the complete local history remains in `chat_history.json`.
- This is intentionally a terminal application to keep the assignment straightforward and easy to explain.

## 8. Run the offline smoke tests

From the repository root, run:

```bash
python -m unittest ChatBot.test_app -v
```

These tests cover local input, sentiment, context, history, and command handling.
They do not require an API key or make a live Gemini request.
