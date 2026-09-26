from fastapi import FastAPI

app = FastAPI(
    title="Devassist RAG API",
    description="AI-powered technical documentation assistant",
    version = "1.0.0"
)

@app.get("/")
def home():
    return{
        "message": "DevAssist RAG API is running"
    }