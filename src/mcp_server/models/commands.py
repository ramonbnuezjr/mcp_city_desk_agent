from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

class CommandStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class CommandRequest(BaseModel):
    """Request model for MCP commands"""
    intent: str = Field(..., description="Command intent (e.g., 'data_query', 'report_generation')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    user_id: Optional[str] = Field(None, description="User identifier for audit purposes")
    priority: Optional[str] = Field("normal", description="Command priority level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent": "data_query",
                "parameters": {
                    "dataset": "311_service_requests",
                    "filters": {"status": "open"},
                    "limit": 100
                },
                "user_id": "analyst_001",
                "priority": "high"
            }
        }

class CommandResponse(BaseModel):
    """Response model for MCP commands"""
    command_id: str = Field(..., description="Unique command identifier")
    status: CommandStatus = Field(..., description="Current command status")
    result: Optional[Dict[str, Any]] = Field(None, description="Command execution result")
    timestamp: str = Field(..., description="ISO timestamp of response")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "command_id": "cmd_123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "result": {
                    "records_count": 150,
                    "data": [...],
                    "execution_time_ms": 245
                },
                "timestamp": "2025-01-27T10:30:00Z"
            }
        }

class CommandLog(BaseModel):
    """Audit log entry for commands"""
    command_id: str
    user_id: Optional[str]
    intent: str
    parameters: Dict[str, Any]
    status: CommandStatus
    start_time: datetime
    end_time: Optional[datetime]
    execution_time_ms: Optional[int]
    error_message: Optional[str]
    result_summary: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "command_id": "cmd_123e4567-e89b-12d3-a456-426614174000",
                "user_id": "analyst_001",
                "intent": "data_query",
                "parameters": {"dataset": "311_service_requests"},
                "status": "completed",
                "start_time": "2025-01-27T10:30:00Z",
                "end_time": "2025-01-27T10:30:00.245Z",
                "execution_time_ms": 245,
                "result_summary": "Retrieved 150 records from 311 service requests"
            }
        }
