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