from fastapi import FastAPI

app = FastAPI(title="AI Agent Platform")

@app.get("/")
async def root():
    return {"message": "AI Agent Platform API"}