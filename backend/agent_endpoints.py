# endpoints for the agent
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

class AgentResponse(BaseModel):
    response: str

agent_router = APIRouter()

@agent_router.post("/agents/chat")
async def chat(request: ChatRequest) -> AgentResponse:
    """
    Chat with the agent
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": request.message}]
        )
        reply = response.choices[0].message.content
        return AgentResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 