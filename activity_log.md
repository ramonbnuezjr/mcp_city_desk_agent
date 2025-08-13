# Activity Log – City Desk Agent

## 2025-08-10 – Project Kickoff

- Defined problem statement and KPIs
- Selected MCP + RAG hybrid architecture
- Created initial repo structure

## 2025-08-15 – API Research

- Validated NYC Open Data API endpoints
- Drafted ServiceNow connector plan

## 2025-08-20 – Prototype MCP Server

- Implemented FastAPI-based MCP skeleton
- Added `/ping` and `/status` endpoints

## 2025-08-28 – RAG Layer Init

- Integrated ChromaDB for PDF ingestion
- Tested with 3 sample agency reports

## 2025-09-05 – CLI Interface

- Built basic command-line client for triggering MCP tasks

## 2025-01-27 16:15 UTC – RAG Layer Implementation

- Implemented complete RAG layer with ChromaDB integration
- Added PDF document processing and semantic search capabilities
- Created dedicated RAG API endpoints for document ingestion and retrieval
- Integrated RAG system with MCP Server command routing
- Established foundation for intelligent document retrieval to improve query accuracy

## 2025-01-27 16:45 UTC – Project Documentation & GitHub Setup

- Updated project documentation to reflect completed RAG implementation
- Marked MVP milestones as complete in project specification
- Established GitHub repository for version control and collaboration
- Set next priorities: Web Dashboard and Report Generation Workflows

## 2025-01-27 18:00 UTC – Rate Limiting System Implementation

- Implemented comprehensive rate limiting system for API protection
- Added per-endpoint tracking with configurable limits (OpenAI: 50/min, Gemini: 50/min, Weather: 60/min)
- Created rate limiting endpoints for monitoring, control, and emergency overrides
- Integrated with main server status endpoint for system health monitoring
- Established production-ready infrastructure for municipal deployment requirements

## 2025-08-12 20:45 UTC – NYC Agency PDF Ingestion & RAG System Validation

- Successfully ingested 8 real NYC agency PDFs into RAG system (100% success rate)
- Fixed ChromaDB metadata type issues (Path objects → strings) and AES PDF decryption
- Upgraded pypdf to 6.0.0 with cryptography backend for encrypted document support
- Created 1,073 document chunks from municipal documents covering housing, health, transportation, and AI governance
- Validated full RAG pipeline with authentic NYC agency data for realistic testing and validation
- Established authentic baseline for 95% API query accuracy KPI validation with real municipal content
