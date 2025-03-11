from fastapi import FastAPI, UploadFile, File, Query, HTTPException
import os
import requests
from app.api_processing import process_cv as process_openai_cv, query_openai_for_cv
from app.local_processing import process_cv_local as process_mistral_cv, query_cv_local

app = FastAPI()

# Create an upload directory if it doesn't exist
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def home():
    return {"message": "FastAPI with dynamic AI model selection is running"}

@app.post("/api/process_cv")
async def process_cv(
    files: list[UploadFile] = File(...),
    model_choice: str = Query(..., description="Choose 'openai' for Azure OCR + GPT or 'mistral' for PyTesseract + Mistral")
):
    """
    Processes CVs using either OpenAI (Azure OCR + GPT) or Mistral (PyTesseract + Mistral).
    """
    if model_choice not in ["openai", "mistral"]:
        raise HTTPException(status_code=400, detail="Invalid model_choice. Choose 'openai' or 'mistral'.")

    if model_choice == "openai":
        return await process_openai_cv(files)
    else:
        return await process_mistral_cv(files)

@app.get("/api/query_cv")
async def query_cv(
    query: str = Query(..., description="Ask about candidates"),
    model_choice: str = Query(..., description="Choose 'openai' for GPT or 'mistral' for Mistral")
):
    """
    Queries processed CVs using OpenAI (GPT-4) or Mistral.
    """
    if model_choice not in ["openai", "mistral"]:
        raise HTTPException(status_code=400, detail="Invalid model_choice. Choose 'openai' or 'mistral'.")

    if model_choice == "openai":
        return {"query": query, "response": query_openai_for_cv(query)}
    else:
        return {"query": query, "response": query_cv_local(query)}
