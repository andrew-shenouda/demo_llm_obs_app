# Demo LLM OBS App

A demo application with a backend API and frontend interface.

## Setup Instructions

### Backend Setup

1. **Navigate to the backend directory:**
   ```
   cd backend
   ```

2. **Create a virtual environment (first time only):**
   ```
   python3 -m venv chatbot_venv
   ```

3. **Activate the virtual environment (every time you run the project):**
   ```
   source chatbot_venv/bin/activate
   ```

4. **Install dependencies (first time only):**
   ```
   pip install fastapi uvicorn openai python-dotenv ddtrace
   ```

5. **Start the backend server:**
   ```
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```
   cd frontend
   ```

2. **Open the application in your browser:**
   ```
   open index.html
   ```

## Development Notes

- **For instrumentation:** Only modify `backend/agent_endpoints.py`
- **Important:** Do not push your changes to the repository. Keep the template unchanged so others can start fresh.

Make sure you add a .env file with OPENAI_API_KEY and DATADOG_API_KEY.

## How to test

Ask the chatbot a question related to:
1. Sports (should result in a tool call using a stub api)
2. Stocks (should result in a tool call using a stub api)
3. Weather (should result in a tool call using a stub api)
4. General (ask about any topic you'd like, this is a normal chat completion)

If you've instrumented correctly, your results in LLMObs should look like the screenshot in fully_instrumented.png

## Project Structure

```
demo_llm_obs_app/
├── backend/
│   ├── agent_endpoints.py  # Main file to modify for instrumentation
│   ├── main.py
│   └── venv/
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
└── README
|__ env
```