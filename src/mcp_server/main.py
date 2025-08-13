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
from .llm.llm_client import llm_client
from .connectors.weather_api import OpenWeatherMapConnector
from .utils.rate_limiter import rate_limiter

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

# Initialize LLM and Weather components
weather_connector = OpenWeatherMapConnector()

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
            "rag_engine": rag_engine.is_healthy(),
            "llm_client": len(llm_client.get_available_providers()) > 0,
            "weather_api": weather_connector.is_healthy(),
            "rate_limiter": True
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

# LLM endpoints
@app.post("/llm/invoke")
async def invoke_llm(provider: str, prompt: str, context: str = None, model_params: dict = None):
    """Invoke a specific LLM provider"""
    try:
        result = await llm_client.invoke(provider, prompt, context, model_params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/llm/invoke-with-fallback")
async def invoke_llm_with_fallback(primary_provider: str, prompt: str, context: str = None, model_params: dict = None):
    """Invoke LLM with automatic fallback"""
    try:
        result = await llm_client.invoke_with_fallback(primary_provider, prompt, context, model_params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/llm/cross-validate")
async def cross_validate_llm(prompt: str, context: str = None, model_params: dict = None):
    """Get responses from multiple LLM providers for validation"""
    try:
        result = await llm_client.cross_validate(prompt, context, model_params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/llm/stats")
async def get_llm_stats():
    """Get LLM usage statistics and cost tracking"""
    try:
        return llm_client.get_usage_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/llm/providers")
async def get_llm_providers():
    """Get available LLM providers and their information"""
    try:
        providers = {}
        for provider in llm_client.get_available_providers():
            providers[provider] = llm_client.get_provider_info(provider)
        return {"available_providers": providers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Weather API endpoints
@app.get("/weather/current")
async def get_current_weather(city: str = "New York", country_code: str = "US", units: str = "metric"):
    """Get current weather for a city"""
    try:
        result = await weather_connector.get_current_weather(city, country_code, units)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/forecast")
async def get_weather_forecast(city: str = "New York", country_code: str = "US", days: int = 5, units: str = "metric"):
    """Get weather forecast for a city"""
    try:
        result = await weather_connector.get_weather_forecast(city, country_code, days, units)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/alerts")
async def get_weather_alerts(city: str = "New York", country_code: str = "US"):
    """Get weather alerts for a city"""
    try:
        result = await weather_connector.get_weather_alerts(city, country_code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/weather/correlate")
async def correlate_weather_with_events(city: str = "New York", country_code: str = "US", event_type: str = "service_requests"):
    """Correlate weather data with municipal events"""
    try:
        # Get current weather first
        weather_data = await weather_connector.get_current_weather(city, country_code)
        # Then correlate with events
        result = await weather_connector.correlate_with_events(weather_data, event_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/stats")
async def get_weather_stats():
    """Get weather API cache statistics"""
    try:
        return weather_connector.get_cache_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint for connectivity testing"""
    return {"message": "MCP server is accessible", "timestamp": datetime.utcnow().isoformat()}

# Rate Limiting endpoints
@app.get("/rate-limits/stats")
async def get_rate_limit_stats(endpoint: str = None):
    """Get rate limiting statistics"""
    try:
        return rate_limiter.get_stats(endpoint)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rate-limits/set-limit")
async def set_rate_limit(endpoint: str, requests_per_minute: int):
    """Set custom rate limit for endpoint"""
    try:
        rate_limiter.set_custom_limit(endpoint, requests_per_minute)
        return {"success": True, "endpoint": endpoint, "limit": requests_per_minute}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rate-limits/reset")
async def reset_rate_limits(endpoint: str = None):
    """Reset rate limits for endpoint or all endpoints"""
    try:
        rate_limiter.reset_limits(endpoint)
        return {"success": True, "endpoint": endpoint or "all"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rate-limits/emergency-override")
async def emergency_override(endpoint: str, allow: bool = True):
    """Emergency override for rate limits (use with caution)"""
    try:
        rate_limiter.emergency_override(endpoint, allow)
        return {"success": True, "endpoint": endpoint, "action": "allowed" if allow else "blocked"}
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
