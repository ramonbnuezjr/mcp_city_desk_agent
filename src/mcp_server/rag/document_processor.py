import PyPDF2
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processes PDF documents for ingestion into the RAG system"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_pdf(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Process a PDF file and return chunks with metadata"""
        try:
            if not Path(file_path).exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            # Extract text from PDF
            text = self._extract_pdf_text(file_path)
            if not text.strip():
                logger.warning(f"No text extracted from PDF: {file_path}")
                return []
            
            # Generate document ID
            doc_id = self._generate_document_id(file_path, text)
            
            # Chunk the text
            chunks = self._chunk_text(text)
            
            # Prepare documents for ingestion
            documents = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "source_file": file_path,
                    "document_id": doc_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk),
                    "processed_at": datetime.utcnow().isoformat(),
                    "file_size_bytes": Path(file_path).stat().st_size,
                    "file_modified": datetime.fromtimestamp(Path(file_path).stat().st_mtime).isoformat()
                }
                
                # Merge with provided metadata
                if metadata:
                    chunk_metadata.update(metadata)
                
                documents.append({
                    "id": f"{doc_id}_chunk_{i}",
                    "text": chunk,
                    "metadata": chunk_metadata
                })
            
            logger.info(f"Processed PDF {file_path}: {len(chunks)} chunks created")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to process PDF {file_path}: {e}")
            return []
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            # Clean up the text
                            cleaned_text = self._clean_text(page_text)
                            text += f"\n--- Page {page_num + 1} ---\n{cleaned_text}\n"
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                        continue
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"PDF text extraction failed for {file_path}: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\-.,;:!?()]', '', text)
        
        # Normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        return text.strip()
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters of the chunk
                search_start = max(start + self.chunk_size - 100, start)
                sentence_end = self._find_sentence_boundary(text, search_start, end)
                if sentence_end > start:
                    end = sentence_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position, accounting for overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def _find_sentence_boundary(self, text: str, start: int, end: int) -> int:
        """Find a good sentence boundary within the given range"""
        # Look for sentence endings (. ! ?) followed by whitespace
        for i in range(end - 1, start, -1):
            if text[i] in '.!?' and i + 1 < len(text) and text[i + 1].isspace():
                return i + 1
        
        # If no sentence boundary found, return the original end
        return end
    
    def _generate_document_id(self, file_path: str, text: str) -> str:
        """Generate a unique document ID based on file path and content"""
        # Create a hash from file path and first 1000 characters of text
        content_hash = hashlib.md5(
            f"{file_path}:{text[:1000]}".encode()
        ).hexdigest()[:12]
        
        # Add timestamp for uniqueness
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        return f"doc_{timestamp}_{content_hash}"
    
    def process_directory(self, directory_path: str, 
                         file_pattern: str = "*.pdf",
                         metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Process all PDF files in a directory"""
        try:
            directory = Path(directory_path)
            if not directory.exists() or not directory.is_dir():
                raise ValueError(f"Invalid directory: {directory_path}")
            
            pdf_files = list(directory.glob(file_pattern))
            if not pdf_files:
                logger.warning(f"No PDF files found in {directory_path}")
                return []
            
            all_documents = []
            for pdf_file in pdf_files:
                try:
                    documents = self.process_pdf(str(pdf_file), metadata)
                    all_documents.extend(documents)
                except Exception as e:
                    logger.error(f"Failed to process {pdf_file}: {e}")
                    continue
            
            logger.info(f"Processed {len(pdf_files)} PDF files, created {len(all_documents)} chunks")
            return all_documents
            
        except Exception as e:
            logger.error(f"Directory processing failed for {directory_path}: {e}")
            return []
    
    def get_processing_stats(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about processed documents"""
        if not documents:
            return {"total_documents": 0, "total_chunks": 0}
        
        total_chunks = len(documents)
        total_text_length = sum(len(doc.get("text", "")) for doc in documents)
        
        # Group by source file
        source_files = {}
        for doc in documents:
            source = doc.get("metadata", {}).get("source_file", "unknown")
            if source not in source_files:
                source_files[source] = 0
            source_files[source] += 1
        
        return {
            "total_documents": len(source_files),
            "total_chunks": total_chunks,
            "total_text_length": total_text_length,
            "average_chunk_size": total_text_length / total_chunks if total_chunks > 0 else 0,
            "source_files": source_files
        }
