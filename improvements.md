# Improvements – City Desk Agent

## MVP Scope

- MCP Server with:
    - NYC Open Data connector
    - PDF repository ingestion + RAG ✅
- CLI interface
- Command execution logging

## Post-MVP Enhancements

- **ServiceNow Connector** for ticket retrieval and update
- Slack/Teams bot integration
- Advanced PDF parsing (OCR for scanned docs)
- Scheduling: automated daily/weekly reports
- Fine-grained role-based access control (RBAC) - *Deferred for MVP*

## Next MVP Priorities

- ✅ **Web Dashboard** - User interface for triggering RAG queries and viewing results ✅ **COMPLETED**
- **Report Generation Workflows** - Automate common reporting tasks using RAG context
- **Enhanced RAG Features** - Improve chunking strategies and search relevance

## Recently Completed

- ✅ **Multi-API & Multi-LLM Architecture** - GPT-4o-mini + Gemini 2.5 Pro + OpenWeatherMap
- ✅ **Rate Limiting System** - API protection with configurable limits and monitoring
- ✅ **Enterprise-Grade Infrastructure** - Production-ready for municipal deployment
- ✅ **NYC Agency PDF Ingestion** - 8 real municipal documents successfully ingested (1,073 chunks)
- ✅ **RAG System Validation** - Full pipeline tested with authentic NYC agency data
- ✅ **Streamlit Dashboard** - Production-ready KPI-first control room with 5 pages and real-time monitoring

## Completed Infrastructure

- ✅ **GitHub Repository** - [https://github.com/ramonbnuezjr/mcp_city_desk_agent](https://github.com/ramonbnuezjr/mcp_city_desk_agent)
- ✅ **Version Control** - Git setup with proper .gitignore for Python project
- ✅ **Project Documentation** - Complete project specification and activity logging

## Experimental Ideas

- Local LLM fallback (gpt-oss-20b) for offline ops
- Voice command support via ElevenLabs
- Integration with GIS mapping data
- “Explain Like I’m 5” mode for citizen-facing summaries
