# endpoints for the agent
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    newest_message: str
    conversation_history: list[str]

class AgentResponse(BaseModel):
    reply: str

agent_router = APIRouter()

@agent_router.post("/agents/chat")
async def chat(request: ChatRequest) -> AgentResponse:
    """
    Chat with the agent. 
    """
    try:
        # Build messages array with conversation history
        messages = []
        
        # Add conversation history if provided
        if request.conversation_history:
            for i, message in enumerate(request.conversation_history):
                # Alternate between user and assistant roles
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({"role": role, "content": message})
        
        # Add the newest message
        messages.append({"role": "user", "content": request.newest_message})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages + [
                {
                    "role": "system", 
                    "content": "Please format your responses using markdown when appropriate. Use **bold** for emphasis, *italic* for subtle emphasis, `code` for inline code, ```code blocks``` for multi-line code, # ## ### for headers, and - or * for lists. Use double line breaks (\\n\\n) to separate paragraphs for better readability. Make your responses well-structured and easy to read."
                }
            ]
        )
        reply = response.choices[0].message.content
        return AgentResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

    