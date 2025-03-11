import requests
from fastapi import APIRouter, UploadFile, File, Query
import os
import re
import httpx

router = APIRouter()

COLAB_BASE_URL = "https://b502-34-125-11-8.ngrok-free.app"

COLAB_PROCESSING_URL = f"{COLAB_BASE_URL}/process_cv"
COLAB_STORE_URL = f"{COLAB_BASE_URL}/store_cv"
COLAB_QUERY_URL = f"{COLAB_BASE_URL}/query_cv"


UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def clean_response(text):
    """Cleans up Mistral API response."""
    text = text.strip()
    text = re.sub(r"^\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"Structure the following resume text into a clean, professional format\.\n*", "", text)
    text = re.sub(r"\*\*Resume Text:\*\*\n*", "", text)
    text = re.sub(r"\*\*Instructions:\*\*.*", "", text, flags=re.DOTALL)
    text = re.sub(r"[\u2022\u00a2]", "-", text)
    text = text.replace("status: success", "").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

@router.post("/process_cv_local")
async def process_cv_local(files: list[UploadFile] = File(...)):
    """Processes CVs using Mistral (Colab) and returns structured JSON."""
    extracted_results = []

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        with open(file_path, "rb") as pdf_file:
            file_payload = {"file": pdf_file}
            response = requests.post(COLAB_PROCESSING_URL, files=file_payload)

        if response.status_code == 200:
            structured_resume = response.text.strip()
            cleaned_resume = clean_response(structured_resume)

            if cleaned_resume:
                extracted_results.append({"filename": file.filename, "data": cleaned_resume})

                store_payload = {"resume": cleaned_resume}
                store_response = requests.post(COLAB_STORE_URL, json=store_payload)

                if store_response.status_code != 200:
                    print(f"Failed to store resume in Colab: {store_response.text}")
            else:
                extracted_results.append({"filename": file.filename, "data": "No structured data returned."})
        else:
            extracted_results.append({"filename": file.filename, "data": f"Colab processing failed: {response.text}"})

    return {"status": "success", "results": extracted_results}

@router.get("/query_cv_local")
async def query_cv_local(q: str = Query(..., description="Ask about candidates")):
    """Queries stored resumes in Colab."""
    
    query_payload = {"query": q}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(COLAB_QUERY_URL, json=query_payload)

        if response.status_code == 200:
            try:
                return response.json()
            except Exception:
                return {"query": q, "response": response.text.strip()}
        else:
            return {"error": f"Mistral API request failed: {response.status_code}, {response.text}"}
    
    except httpx.RequestError as e:
        return {"error": f"Request failed: {str(e)}"}
