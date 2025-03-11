@echo off
echo Installing required system dependencies using Chocolatey...

:: Install Tesseract OCR
choco install tesseract -y

:: Install LibreOffice (for Word to PDF conversion)
choco install libreoffice -y

:: Install Poppler (for handling PDF files)
choco install poppler -y

echo System dependencies installed successfully!

echo Installing required Python libraries...
pip install -r requirements.txt

echo Setup complete! Restart CMD and verify installation.
pause
