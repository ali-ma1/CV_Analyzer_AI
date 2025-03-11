# CV Analyzer AI
A powerful AI-driven system designed to extract, structure, and analyze resumes using both **closed-source** (Azure OCR + OpenAI) and **open-source** (PyTesseract + Mistral) solutions. This project allows recruiters to upload CVs, extract structured data using OCR, and interact with candidate information through an LLM-powered chatbot.

## Design Process and Methods  

### Dual-Model Approach  
- **Closed-Source Solution (Azure OCR + OpenAI GPT-4)**  
  - Uses **Azure OCR API** to extract text from PDFs.  
  - Formats and structures resumes with **OpenAI's GPT-4**.  
  - Stores structured CVs for retrieval and querying.  

- **Open-Source Solution (PyTesseract + Mistral-7B)**  
  - Uses **PyTesseract** for OCR-based text extraction.  
  - Leverages a **fine-tuned Mistral-7B LLM** to structure and process resumes.  
  - Stores structured CVs in a local database for retrieval and queries.  

This dual approach provides **flexibility** for users to choose between proprietary and open-source AI solutions based on their requirements.

---

### OCR and Resume Processing  
- **Document Upload Handling**  
  - Supports **PDF, DOC, and DOCX** files.  
  - Converts Word documents to PDF using **LibreOffice CLI** for seamless processing.  
  - Uses **Azure OCR API** or **PyTesseract** to extract text from CVs.  

- **Resume Structuring with LLMs**  
  - OpenAI GPT-4 or Mistral-7B is used to format the extracted text into **clean, structured resumes**.  
  - Generates a **consistent, professional layout** to improve readability and searchability.  
  - Applies **real-time entity recognition** to highlight key resume sections.  

- **Efficient Data Storage**  
  - OpenAI-processed resumes are stored in `openai_resumes.txt`.  
  - Mistral-processed resumes are stored in `mistral_resumes.txt`.  
  - Resumes can be queried dynamically through **FastAPI**.

---

### Querying Resumes Using AI  
- Users can **ask questions** about candidates (e.g., *"Who has experience in AI?"*).  
- The system **retrieves and summarizes relevant resumes** based on the query.  
- Query responses include:
  - **Candidate Name**
  - **Key Skills**
  - **Relevant Experience**  
- Uses **GPT-4 or Mistral-7B** for intelligent query analysis and candidate matching.  

---

### User Interface & Interaction  
- **FastAPI Backend**  
  - Handles resume uploads, OCR processing, and AI-based structuring.  
  - Provides endpoints for querying resumes dynamically.  

- **Flask API (Mistral-7B Processing)**  
  - Runs an independent **Mistral-7B model via ngrok** for open-source processing.  
  - Exposes endpoints for processing and querying structured resumes.  

- **Streamlit Frontend**  
  - Provides a **user-friendly web interface** for resume uploads and queries.  
  - Users can choose between **OpenAI (Azure OCR + GPT-4)** or **Mistral (PyTesseract + Mistral-7B)** processing.  
  - Displays **formatted resumes and chatbot interactions** in real-time.  

---

## Results and Performance  
### Closed-Source (Azure OCR + OpenAI GPT-4)
- **High OCR Accuracy** (~99% for standard resumes).  
- **Well-structured resumes** with clear headings and bullet points.  
- **Strong query response quality** using GPT-4's advanced reasoning.  

### Open-Source (PyTesseract + Mistral-7B)
- **No API costs** (Fully open-source).  
- **Good OCR accuracy (~85%)**, dependent on resume formatting.  
- **Mistral-7B provides structured output**, ensuring readability.  

Both models were tested on many different resumes, ensuring high reliability in **text extraction, structuring, and candidate querying**.
