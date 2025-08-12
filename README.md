# MCP City Desk Agent

AI-powered interface for municipal data workflows using MCP (Model Context Protocol) architecture.

## Quick Start

### Prerequisites
- Python 3.8+
- Docker and Docker Compose (optional)

### Environment Setup
1. **Copy environment template:**
   ```bash
   cp env.example .env
   ```

2. **Edit .env file with your API keys:**
   ```bash
   # NEVER commit .env files to version control!
   OPENAI_API_KEY=your_actual_openai_key_here
   WEATHER_API_KEY=your_actual_weather_key_here
   GOOGLE_GEMINI_API_KEY=your_actual_gemini_key_here
   ```

### Local Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the MCP server:**
   ```bash
   python -m uvicorn src.mcp_server.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Test the system:**
   ```bash
   python test_mcp_server.py
   ```

### Docker Setup

1. **Start services:**
   ```bash
   docker-compose up -d
   ```

2. **Check status:**
   ```bash
   curl http://localhost:8000/status
   ```

## API Endpoints

- `GET /` - Health check
- `GET /status` - Service status and component health
- `POST /command` - Execute MCP commands
- `GET /commands/{command_id}` - Get command status and results

### RAG Endpoints

- `POST /rag/ingest` - Ingest PDF documents into the RAG system
- `POST /rag/query` - Query documents using semantic search
- `GET /rag/stats` - Get RAG system statistics
- `POST /rag/reset` - Reset the RAG system (use with caution)

### LLM Endpoints

- `POST /llm/invoke` - Invoke a specific LLM provider (GPT-4o-mini or Gemini 2.5 Pro)
- `POST /llm/invoke-with-fallback` - Invoke with automatic fallback to other providers
- `POST /llm/cross-validate` - Get responses from multiple providers for validation
- `GET /llm/stats` - Get usage statistics and cost tracking
- `GET /llm/providers` - Get available LLM providers and their information

### Weather API Endpoints

- `GET /weather/current` - Get current weather for a city
- `GET /weather/forecast` - Get weather forecast for a city
- `GET /weather/alerts` - Get weather alerts for a city
- `POST /weather/correlate` - Correlate weather data with municipal events
- `GET /weather/stats` - Get weather API cache statistics

## Example Usage

### Query NYC Open Data

```bash
curl -X POST "http://localhost:8000/command" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "data_query",
    "parameters": {
      "dataset": "erm2-nwe9",
      "filters": {"status": "open"},
      "limit": 100
    },
    "user_id": "analyst_001"
  }'
```

### Query Documents with RAG

```bash
curl -X POST "http://localhost:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "building permit requirements",
    "n_results": 5
  }'
```

### Ingest PDF Documents

```bash
curl -X POST "http://localhost:8000/rag/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/municipal_code.pdf",
    "metadata": {"document_type": "municipal_code", "department": "planning"}
  }'
```

### Invoke LLM with Context

```bash
curl -X POST "http://localhost:8000/llm/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "prompt": "Summarize the building permit requirements",
    "context": "Building permits are required for all construction projects..."
  }'
```

### Get Weather Data

```bash
curl "http://localhost:8000/weather/current?city=New%20York&country_code=US&units=metric"
```

### Correlate Weather with Events

```bash
curl -X POST "http://localhost:8000/weather/correlate" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "New York",
    "country_code": "US",
    "event_type": "service_requests"
  }'
```

### Check Command Status

```bash
curl "http://localhost:8000/commands/{command_id}"
```

## Architecture

- **MCP Server**: FastAPI-based server handling command routing
- **Connectors**: API adapters for external data sources (NYC Open Data, ServiceNow)
- **RAG Layer**: ChromaDB-based document retrieval and semantic search
- **Command Logger**: SQLite-based audit trail for all operations
- **Models**: Pydantic models for type safety and validation

## Development

### Project Structure
```
src/
├── mcp_server/
│   ├── main.py              # FastAPI application
│   ├── models/              # Data models
│   ├── connectors/          # External API connectors
│   └── utils/               # Utilities (logging, etc.)
├── requirements.txt         # Python dependencies
└── docker-compose.yml      # Local development setup
```

### Running Tests
```bash
# Test basic MCP server functionality
python test_mcp_server.py

# Test RAG system specifically
python test_rag_system.py
```

## Next Steps

- [x] Implement RAG layer with ChromaDB
- [ ] Build web dashboard
- [ ] Add authentication and RBAC
- [ ] Implement report generation workflows
- [ ] Add ServiceNow connector (future enhancement)
