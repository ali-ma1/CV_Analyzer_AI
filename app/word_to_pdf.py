import subprocess
import os

LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.com"

def convert_word_to_pdf(file_path):
    """
    Converts a Word document (DOC/DOCX) to PDF using LibreOffice.
    Returns the path of the converted PDF file if successful, otherwise None.
    """
    if not os.path.exists(LIBREOFFICE_PATH):
        print("Error: LibreOffice (soffice.com) not found. Check installation.")
        return None

    output_dir = os.path.dirname(file_path)
    
    try:
        result = subprocess.run(
            [LIBREOFFICE_PATH, "--headless", "--convert-to", "pdf", file_path, "--outdir", output_dir],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )

        pdf_path = os.path.splitext(file_path)[0] + ".pdf"
        if os.path.exists(pdf_path):
            return pdf_path
        else:
            print("Error: Converted PDF file not found.")
            return None

    except subprocess.CalledProcessError as e:
        print(f"LibreOffice conversion failed: {e}")
        return None
