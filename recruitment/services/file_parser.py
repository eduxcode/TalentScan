import os
import logging
import PyPDF2
from docx import Document

logger = logging.getLogger(__name__)

class FileParser:
    """Service to extract text from various file formats"""

    @staticmethod
    def extract_text(file_path):
        """
        Extracts text from a file based on its extension.
        
        Args:
            file_path (str): Absolute path to the file.
            
        Returns:
            str: Extracted text or empty string on failure.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return ""

        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == '.pdf':
                return FileParser._read_pdf(file_path)
            elif ext == '.docx':
                return FileParser._read_docx(file_path)
            elif ext == '.txt':
                return FileParser._read_txt(file_path)
            else:
                logger.warning(f"Unsupported file extension: {ext}")
                return ""
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return ""

    @staticmethod
    def _read_pdf(file_path):
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()

    @staticmethod
    def _read_docx(file_path):
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs]).strip()

    @staticmethod
    def _read_txt(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read().strip()
