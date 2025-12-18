from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(title="SHL GenAI Assessment Recommender")

app.include_router(router)

# To run the app, use the command:
# uvicorn app.main:app --host
