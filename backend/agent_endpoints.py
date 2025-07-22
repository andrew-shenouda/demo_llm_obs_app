"""
Clean, modular FastAPI agent ‑‑ ready for Datadog LLMObs
────────────────────────────────────────────────────────
Covers span types: workflow • agent • task • tool • llm
Categories supported: weather • stocks • sports • general chat
"""

from __future__ import annotations

import os
import json
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI

from ddtrace.llmobs.decorators import *

# ───────────────────────────────
# Environment / clients
# ───────────────────────────────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ───────────────────────────────
# Datadog LLMObs 
# ───────────────────────────────
# TODO: enable Datadog LLMObs
# LLMObs.enable(
#   ml_app="demo-llm-obs-app",
#   api_key=os.getenv("DATADOG_API_KEY"),
#   site="datad0g.com",
#   agentless_enabled=True,
# )

# ───────────────────────────────
# Public request / response models
# ───────────────────────────────
class ChatRequest(BaseModel):
    newest_message: str
    conversation_history: List[str] = []        # optional

class AgentResponse(BaseModel):
    reply: str                                  # only the answer text

# ───────────────────────────────
# TASK SPAN – tiny synchronous step
# ───────────────────────────────
# TODO: @task
def sanitize_input(text: str) -> str:
    """Strip whitespace and cap length."""
    return text.strip()[:8_000]

# ───────────────────────────────
# LLM SPAN – intent classification
# ───────────────────────────────
# TODO: @tool
def classify_intent_llm(question: str) -> str:
    """
    Ask an LLM to return one of: weather / stocks / sports / general.
    The reply *must* be exactly the category word; we parse it as‑is.
    """
    prompt = (
        "Classify the user's request into exactly one of the following "
        "categories: weather, stocks, sports, general. "
        "Reply with ONLY the category word.\n\n"
        f"USER: {question}\n\nCATEGORY:"
    )
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip().lower()

# ───────────────────────────────
# LLM SPAN – tool selection
# ───────────────────────────────
# TODO: @tool
def select_tool_llm(intent: str, question: str) -> Dict[str, Any]:
    """
    Use function calling to decide which specific API to call based on intent and question.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "call_weather_api",
                "description": "Get current weather information for a specific location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name e.g. New York, Paris, Tokyo"
                        }
                    },
                    "required": ["location"],
                    "additionalProperties": False
                },
                "strict": True
            }
        },
        {
            "type": "function",
            "function": {
                "name": "call_stock_api",
                "description": "Get current stock price and daily change for a ticker symbol.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol e.g. AAPL, GOOGL, TSLA"
                        }
                    },
                    "required": ["ticker"],
                    "additionalProperties": False
                },
                "strict": True
            }
        },
        {
            "type": "function",
            "function": {
                "name": "call_sports_api",
                "description": "Get current sports score for a team.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "team": {
                            "type": "string",
                            "description": "Team abbreviation e.g. LAL, BOS, NYK"
                        }
                    },
                    "required": ["team"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    ]
    
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system", 
                "content": "You are a tool selector. You MUST ALWAYS call one of the available tools. For sports questions, call call_sports_api with team='LAL'. For stock questions, call call_stock_api with ticker='AAPL'. For weather questions, call call_weather_api with location='New York'. If the question is vague like 'give me the latest on sports scores', use the default values. NEVER respond with text - ONLY call tools."
            },
            {"role": "user", "content": f"Intent: {intent}. Question: {question}. Call the appropriate API."}
        ],
        tools=tools,
        tool_choice="auto"
    )
    
    if resp.choices[0].message.tool_calls:
        tool_call = resp.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        # Execute the function
        if function_name == "call_weather_api":
            return call_weather_api(**function_args)
        elif function_name == "call_stock_api":
            return call_stock_api(**function_args)
        elif function_name == "call_sports_api":
            return call_sports_api(**function_args)
    
    return {"error": "No tool called"}

# ───────────────────────────────
# TOOL SPANs – external service stubs
# ───────────────────────────────
# TODO: @tool
def call_weather_api(location: str = "New York") -> Dict[str, Any]:
    """Return a mock weather report."""
    return {"location": location, "temperature_c": 24, "condition": "Partly cloudy"}

# TODO: @tool
def call_stock_api(ticker: str = "AAPL") -> Dict[str, Any]:
    """Return a mock daily stock quote."""
    return {"ticker": ticker.upper(), "price_usd": 218.37, "change_pct": +1.9}

# TODO: @tool
def call_sports_api(team: str = "LAL") -> Dict[str, Any]:
    """Return a mock sports score."""
    return {
        "team": team.upper(),
        "opponent": "BOS",
        "team_score": 102,
        "opponent_score": 99,
        "status": "final",
    }

# ───────────────────────────────
# LLM SPAN – answer formatting
# ───────────────────────────────
# TODO: @tool
def format_answer_llm(tool_name: str, tool_payload: Dict[str, Any], question: str) -> str:
    """Turn raw tool data into a friendly Markdown reply."""
    sys = (
        "You are a helpful assistant that formats structured API data "
        "into concise, user‑friendly answers. Respond in Markdown."
    )
    messages = [
        {"role": "system", "content": sys},
        {"role": "user", "content": question},
        {
            "role": "assistant",
            "content": f"The following {tool_name} data may help:\n```json\n{tool_payload}\n```",
        },
    ]
    return client.chat.completions.create(
        model="gpt-4o",
        temperature=0.4,
        messages=messages,
    ).choices[0].message.content

# ───────────────────────────────
# LLM SPAN – fallback chat
# ───────────────────────────────
# TODO: @tool 
def general_chat_llm(question: str, history: List[str]) -> str:
    """Normal conversational fallback when no tool is needed."""
    messages: List[Dict[str, str]] = []
    for i, msg in enumerate(history):
        role = "user" if i % 2 == 0 else "assistant"
        messages.append({"role": role, "content": msg})
    messages.append({"role": "user", "content": question})

    # System style guide
    messages.insert(
        0,
        {
            "role": "system",
            "content": (
                "Please format responses using Markdown when appropriate. "
                "Use **bold** for emphasis, *italic* for subtle emphasis, "
                "`code` for inline code, ```code blocks``` for multi‑line code, "
                "# ## ### for headers, and - or * for lists. Double line breaks "
                "between paragraphs."
            ),
        },
    )

    return client.chat.completions.create(
        model="gpt-4o", temperature=0.7, messages=messages
    ).choices[0].message.content

# ───────────────────────────────
# AGENT SPAN – dynamic orchestration
# ───────────────────────────────
# TODO: @agent
def decision_agent(question: str, history: List[str]) -> str:
    """
    1. Use LLM to classify intent
    2. Call the appropriate tool (if any)
    3. Ask LLM to craft final answer
    """
    intent = classify_intent_llm(question)

    if intent == "general":
        return general_chat_llm(question, history)
    
    # Use function calling to select and execute the appropriate tool
    data = select_tool_llm(intent, question)
    return format_answer_llm(intent, data, question)

# ───────────────────────────────
# WORKFLOW SPAN – top‑level flow
# ───────────────────────────────
# TODO: @workflow
def chat_workflow(user_msg: str, history: List[str]) -> str:
    """End‑to‑end processing for one incoming message."""
    cleaned = sanitize_input(user_msg)
    return decision_agent(cleaned, history)

# ───────────────────────────────
# FastAPI HTTP layer
# ───────────────────────────────
agent_router = APIRouter()

@agent_router.post("/agents/chat", response_model=AgentResponse)
async def chat(request: ChatRequest) -> AgentResponse:
    """
    HTTP entry‑point.  Delegates all work to the workflow function so
    span nesting is clean and predictable.
    """
    try:
        reply = chat_workflow(request.newest_message, request.conversation_history)
        return AgentResponse(reply=reply)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
