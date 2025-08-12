from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
from datetime import datetime
import uuid

from .models.commands import CommandRequest, CommandResponse, CommandStatus
from .connectors.nyc_open_data import NYCOpenDataConnector
from .utils.logger import CommandLogger
from .rag.chromadb_manager import ChromaDBManager
from .rag.document_processor import DocumentProcessor
from .rag.query_engine import RAGQueryEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP City Desk Agent",
    description="AI-powered interface for municipal data workflows",
    version="1.0.0"
)

# CORS middleware for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
nyc_connector = NYCOpenDataConnector()
command_logger = CommandLogger()

# Initialize RAG components
chroma_manager = ChromaDBManager()
document_processor = DocumentProcessor()
rag_engine = RAGQueryEngine(chroma_manager, document_processor)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MCP City Desk Agent"}

@app.get("/status")
async def status():
    """Service status and component health"""
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "nyc_open_data": nyc_connector.is_healthy(),
            "command_logger": command_logger.is_healthy(),
            "rag_engine": rag_engine.is_healthy()
        }
    }

@app.post("/command", response_model=CommandResponse)
async def execute_command(command: CommandRequest):
    """Execute a command through the MCP agent"""
    command_id = str(uuid.uuid4())
    
    try:
        # Log command start
        command_logger.log_command_start(command_id, command)
        
        # Route command based on intent
        if command.intent == "data_query":
            result = await nyc_connector.query_data(command.parameters)
        elif command.intent == "rag_query":
            result = await rag_engine.query_documents(
                command.parameters.get("query", ""),
                n_results=command.parameters.get("n_results", 5),
                filter_metadata=command.parameters.get("filters")
            )
        elif command.intent == "document_ingestion":
            result = await rag_engine.ingest_pdf(
                command.parameters.get("file_path", ""),
                metadata=command.parameters.get("metadata")
            )
        elif command.intent == "report_generation":
            result = await generate_report(command.parameters)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown intent: {command.intent}")
        
        # Log successful execution
        command_logger.log_command_success(command_id, result)
        
        return CommandResponse(
            command_id=command_id,
            status=CommandStatus.COMPLETED,
            result=result,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        # Log error
        command_logger.log_command_error(command_id, str(e))
        logger.error(f"Command execution failed: {e}")
        
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/commands/{command_id}")
async def get_command_status(command_id: str):
    """Get status and result of a specific command"""
    command_info = command_logger.get_command(command_id)
    if not command_info:
        raise HTTPException(status_code=404, detail="Command not found")
    return command_info

# RAG-specific endpoints
@app.post("/rag/ingest")
async def ingest_document(file_path: str, metadata: dict = None):
    """Ingest a PDF document into the RAG system"""
    try:
        result = await rag_engine.ingest_pdf(file_path, metadata)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/query")
async def query_documents(query: str, n_results: int = 5, filters: dict = None):
    """Query documents using RAG approach"""
    try:
        result = await rag_engine.query_documents(query, n_results, filters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rag/stats")
async def get_rag_stats():
    """Get RAG system statistics"""
    try:
        return rag_engine.get_system_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/reset")
async def reset_rag_system():
    """Reset the RAG system (use with caution)"""
    try:
        result = rag_engine.reset_system()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_report(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a report based on parameters"""
    # Placeholder for report generation logic
    return {
        "report_type": parameters.get("type", "unknown"),
        "generated_at": datetime.utcnow().isoformat(),
        "content": "Report generation not yet implemented"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
