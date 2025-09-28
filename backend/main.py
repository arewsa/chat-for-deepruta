from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.mistral_services import MistralServices
from models.chat_request import ChatRequest
from models.chat_response import ChatResponse

mistral_services = MistralServices()
app = FastAPI(title="ChatForDeepRuta API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response_text = mistral_services.generate_response(request.message)

        return ChatResponse(response=str(response_text))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "ChatForDeepRuta API работает!"}

