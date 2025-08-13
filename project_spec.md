# Project Spec – City Desk Agent

## Multi-Channel MCP Agent for Government Data Workflows

## 1. Problem Statement

Government analysts, clerks, and field officers often juggle multiple data sources (ServiceNow, Open Data portals, PDF regulations, email threads) with siloed workflows.

This leads to:

- Duplicated effort
- Missed deadlines
- Delays in public service delivery

We need a **single AI-powered interface** that can:

- Pull from multiple sources
- Understand government-specific queries
- Automate repetitive research & reporting tasks
- Push results back into official channels

## 2. Goals

- Create an **MCP-based AI Agent** that connects to multiple municipal data APIs and document stores.
- Support **multi-channel interfaces**:
    - CLI (for IT staff)
    - Web dashboard (for analysts)
    - Optional chat (Slack/Teams) integration
- Automate common workflows:
    - Summarizing incident reports
    - Pulling stats from Open Data
    - Generating weekly compliance summaries
- Log all actions for audit & accountability.

## 3. KPIs

- **≥ 90% task completion** without human correction for pre-defined workflows.
- **Reduce research/report prep time by 60%** for pilot users.
- **API query accuracy ≥ 95%** when matching retrieved data to user requests.
- Time-to-answer for complex queries **< 20 seconds**.

## 4. Core Tech Stack

| Component | Technology |
| --- | --- |
| **Agent Framework** | MCP Server (FastAPI) |
| **LLM** | GPT-4o or gpt-oss-20b for on-prem |
| **RAG** | ChromaDB or Weaviate |
| **Data Sources** | NYC Open Data API, ServiceNow REST API, internal PDF repository |
| **Auth** | API key + OAuth2 for internal systems |
| **UI** | Streamlit or React (dashboard), Slack/Teams bot for chat |
| **Hosting** | Docker, optional on-prem for compliance |
| **Logs** | SQLite or PostgreSQL |

## 5. Architecture

1. **User Input Layer** (CLI, Dashboard, Chat)
2. **MCP Command Router** (task intent recognition)
3. **RAG Retrieval Layer** (vector DB lookups for docs)
4. **API Connectors** (Open Data, ServiceNow, internal DB)
5. **LLM Reasoning Engine** (task orchestration, summarization)
6. **Output Layer** (reports, messages, data visualizations)

## 6. Constraints

- Must meet municipal IT security requirements (audit logs, on-prem deployment option)
- No PII leaves the system without encryption
- MVP must run locally on developer laptop for testing

## 7. Milestones

1. **MVP MCP Server** with at least 2 API connectors ✅
2. **Basic RAG Layer** for PDF repository ✅
3. **Command Execution Logging** ✅
4. **Rate Limiting & API Protection** ✅
5. **Web Dashboard** for triggering tasks ✅
6. **Multi-Channel Integration** (optional for MVP)

## 8. Success Criteria

- Pilot group completes ≥ 90% of weekly tasks fully via the agent.
- End-users prefer agent workflow over legacy manual method in feedback survey.

## 9. Current Status

**Completed MVP Components:**
- ✅ MCP Server with FastAPI
- ✅ NYC Open Data API connector
- ✅ Command execution logging and audit trails
- ✅ RAG Layer with ChromaDB integration
- ✅ PDF document processing and semantic search
- ✅ Multi-API & Multi-LLM Architecture (GPT-4o-mini + Gemini 2.5 Pro)
- ✅ OpenWeatherMap integration with municipal correlation
- ✅ Rate limiting system with API protection
- ✅ Enterprise-grade infrastructure for production deployment
- ✅ NYC Agency PDF Ingestion (8 real municipal documents, 1,073 chunks)
- ✅ RAG System Validation with authentic municipal data
- ✅ Streamlit Dashboard with KPI-first control room and real-time monitoring

**Next Priority:** Report Generation Workflows and Enhanced RAG Features

**System Capabilities:**
- **Data Sources**: NYC Open Data, Weather API, PDF Repository
- **AI Models**: GPT-4o-mini, Gemini 2.5 Pro with fallback and cross-validation
- **Security**: Rate limiting, API key management, audit logging
- **Architecture**: MCP Server, RAG Layer, Multi-API connectors
- **User Interface**: Streamlit Dashboard with 5 specialized pages for operations management

## 10. Version Control

**Repository:** [https://github.com/ramonbnuezjr/mcp_city_desk_agent](https://github.com/ramonbnuezjr/mcp_city_desk_agent)

**Current Version:** v1.0.0-beta (MVP with RAG Layer + Dashboard)

**Branch Strategy:** 
- `main` - Stable releases
- `develop` - Active development
- Feature branches for new components
