import PyPDF2
import docx
from typing import Optional
import io


class DocumentProcessor:
    """Service for extracting text from various document formats"""
    
    @staticmethod
    def extract_text(file_content: bytes, filename: str) -> str:
        """
        Extract text from file based on file extension
        
        Args:
            file_content: File content as bytes
            filename: Name of the file with extension
            
        Returns:
            Extracted text as string
            
        Raises:
            ValueError: If file type is not supported
        """
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            return DocumentProcessor._extract_from_pdf(file_content)
        elif file_extension == 'docx':
            return DocumentProcessor._extract_from_docx(file_content)
        elif file_extension in ['txt', 'md']:
            return DocumentProcessor._extract_from_text(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    @staticmethod
    def _extract_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def _extract_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            raise ValueError(f"Error extracting text from DOCX: {str(e)}")
    
    @staticmethod
    def _extract_from_text(file_content: bytes) -> str:
        """Extract text from TXT or MD file"""
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                return file_content.decode('latin-1')
            except Exception as e:
                raise ValueError(f"Error decoding text file: {str(e)}")
    
    @staticmethod
    def get_mime_type(filename: str) -> str:
        """Get MIME type based on file extension"""
        file_extension = filename.lower().split('.')[-1]
        
        mime_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'md': 'text/markdown'
        }
        
        return mime_types.get(file_extension, 'application/octet-stream')
