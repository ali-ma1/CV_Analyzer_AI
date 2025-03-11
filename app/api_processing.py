import requests
from fastapi import APIRouter, UploadFile, File, Query
import os
import openai
import json
from dotenv import load_dotenv
from app.word_to_pdf import convert_word_to_pdf

# Load environment variables from .env (OpenAI and Azure API Keys)
load_dotenv()

router = APIRouter()

UPLOAD_FOLDER = "uploaded_files"
OPENAI_RESUME_FILE = "openai_resumes.txt"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

conversation_history = []

AZURE_OCR_ENDPOINT = os.getenv("AZURE_OCR_ENDPOINT")
AZURE_OCR_KEY = os.getenv("AZURE_OCR_KEY")

def azure_ocr_extract_text(pdf_path):
    """Extracts text from a PDF using Azure OCR API."""
    with open(pdf_path, "rb") as file:
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_OCR_KEY,
            "Content-Type": "application/octet-stream",
        }
        response = requests.post(f"{AZURE_OCR_ENDPOINT}/vision/v3.2/read/analyze", headers=headers, data=file)

    if response.status_code == 202:
        operation_url = response.headers["Operation-Location"]
        import time
        time.sleep(5)

        result = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": AZURE_OCR_KEY}).json()
        extracted_text = ""
        if "analyzeResult" in result:
            for page in result["analyzeResult"]["readResults"]:
                for line in page["lines"]:
                    extracted_text += line["text"] + "\n"

        return extracted_text.strip()
    else:
        return ""

def refine_text_with_openai(raw_text):
    """Formats extracted resume text using OpenAI."""
    openai.api_key = os.getenv("OPENAI_API_KEY")

    messages = [
        {"role": "system", "content": "You are an AI that structures resumes professionally."},
        {"role": "user", "content": f"Format this resume properly:\n\n{raw_text}"}
    ]

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.3,
        max_tokens=1500
    )

    return response.choices[0].message.content.strip()

def store_cv_data_openai(filename, content):
    """Stores OpenAI-processed resumes in a local text file."""
    with open(OPENAI_RESUME_FILE, "a", encoding="utf-8") as file:
        file.write(f"--- Resume: {filename} ---\n{content}\n\n")

def load_cv_data_openai():
    """Loads stored resumes from a local text file."""
    if not os.path.exists(OPENAI_RESUME_FILE):
        return []
    
    with open(OPENAI_RESUME_FILE, "r", encoding="utf-8") as file:
        return file.read().split("\n\n")

@router.post("/process_cv")
async def process_cv(files: list[UploadFile] = File(...)):
    """Processes uploaded CVs using Azure OCR & OpenAI."""
    extracted_results = []

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        if file.filename.endswith((".doc", ".docx")):
            pdf_path = convert_word_to_pdf(file_path)
            if not pdf_path:
                return {"status": "error", "message": f"Failed to convert {file.filename}."}
        else:
            pdf_path = file_path

        extracted_text = azure_ocr_extract_text(pdf_path)

        if not extracted_text:
            return {"status": "error", "message": "OCR extraction failed."}

        structured_resume = refine_text_with_openai(extracted_text)
        store_cv_data_openai(file.filename, structured_resume)

        extracted_results.append({"filename": file.filename, "data": structured_resume})

    return {"status": "success", "results": extracted_results}

def query_openai_for_cv(user_query):
    """Queries OpenAI (GPT-4) for CV analysis."""
    resumes = load_cv_data_openai()
    if not resumes:
        return "No resumes available."

    messages = [
        {"role": "system", "content": (
            "You are an AI assistant that helps recruiters analyze resumes. "
            "Provide structured, intelligent responses with logical reasoning. "
            "Only list relevant candidates."
        )}
    ]

    messages.extend(conversation_history)
    messages.append({"role": "user", "content": f"Here are the resumes:\n{resumes}"})
    messages.append({"role": "user", "content": f"Answer this query: \"{user_query}\"."})

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.2,
        max_tokens=700
    )

    ai_response = response.choices[0].message.content.strip()
    conversation_history.append({"role": "user", "content": user_query})
    conversation_history.append({"role": "assistant", "content": ai_response})

    return ai_response

@router.get("/query_cv")
async def query_cv(q: str = Query(..., description="Ask about candidates")):
    """API endpoint to query OpenAI about resumes."""
    ai_response = query_openai_for_cv(q)
    return {"query": q, "response": ai_response}