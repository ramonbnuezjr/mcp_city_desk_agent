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

- **Web Dashboard** - User interface for triggering RAG queries and viewing results
- **Report Generation Workflows** - Automate common reporting tasks using RAG context
- **Enhanced RAG Features** - Improve chunking strategies and search relevance

## Experimental Ideas

- Local LLM fallback (gpt-oss-20b) for offline ops
- Voice command support via ElevenLabs
- Integration with GIS mapping data
- “Explain Like I’m 5” mode for citizen-facing summaries
