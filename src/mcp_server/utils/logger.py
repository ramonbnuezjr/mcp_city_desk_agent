import sqlite3
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from ..models.commands import CommandRequest, CommandStatus, CommandLog

logger = logging.getLogger(__name__)

class CommandLogger:
    """Audit logger for MCP commands"""
    
    def __init__(self, db_path: str = "command_logs.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with command logs table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_logs (
                    command_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    intent TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    execution_time_ms INTEGER,
                    error_message TEXT,
                    result_summary TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create index for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_command_logs_status 
                ON command_logs(status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_command_logs_user 
                ON command_logs(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_command_logs_timestamp 
                ON command_logs(start_time)
            """)
            
            conn.commit()
            conn.close()
            logger.info("Command logger database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize command logger database: {e}")
            raise
    
    def is_healthy(self) -> bool:
        """Check if the logger is healthy"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM command_logs")
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Command logger health check failed: {e}")
            return False
    
    def log_command_start(self, command_id: str, command: CommandRequest):
        """Log the start of a command execution"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO command_logs (
                    command_id, user_id, intent, parameters, status, 
                    start_time, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                command_id,
                command.user_id,
                command.intent,
                json.dumps(command.parameters),
                CommandStatus.IN_PROGRESS.value,
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Command {command_id} started: {command.intent}")
            
        except Exception as e:
            logger.error(f"Failed to log command start for {command_id}: {e}")
    
    def log_command_success(self, command_id: str, result: Dict[str, Any]):
        """Log successful command completion"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate execution time
            cursor.execute("""
                SELECT start_time FROM command_logs WHERE command_id = ?
            """, (command_id,))
            
            start_time_str = cursor.fetchone()[0]
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.utcnow()
            execution_time = int((end_time - start_time).total_seconds() * 1000)
            
            # Generate result summary
            result_summary = self._generate_result_summary(result)
            
            cursor.execute("""
                UPDATE command_logs SET 
                    status = ?, end_time = ?, execution_time_ms = ?, 
                    result_summary = ?
                WHERE command_id = ?
            """, (
                CommandStatus.COMPLETED.value,
                end_time.isoformat(),
                execution_time,
                result_summary,
                command_id
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Command {command_id} completed successfully in {execution_time}ms")
            
        except Exception as e:
            logger.error(f"Failed to log command success for {command_id}: {e}")
    
    def log_command_error(self, command_id: str, error_message: str):
        """Log command execution error"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate execution time
            cursor.execute("""
                SELECT start_time FROM command_logs WHERE command_id = ?
            """, (command_id,))
            
            start_time_str = cursor.fetchone()[0]
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.utcnow()
            execution_time = int((end_time - start_time).total_seconds() * 1000)
            
            cursor.execute("""
                UPDATE command_logs SET 
                    status = ?, end_time = ?, execution_time_ms = ?, 
                    error_message = ?
                WHERE command_id = ?
            """, (
                CommandStatus.FAILED.value,
                end_time.isoformat(),
                execution_time,
                error_message,
                command_id
            ))
            
            conn.commit()
            conn.close()
            logger.error(f"Command {command_id} failed after {execution_time}ms: {error_message}")
            
        except Exception as e:
            logger.error(f"Failed to log command error for {command_id}: {e}")
    
    def get_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve command log by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM command_logs WHERE command_id = ?
            """, (command_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "command_id": row[0],
                    "user_id": row[1],
                    "intent": row[2],
                    "parameters": json.loads(row[3]),
                    "status": row[4],
                    "start_time": row[5],
                    "end_time": row[6],
                    "execution_time_ms": row[7],
                    "error_message": row[8],
                    "result_summary": row[9],
                    "created_at": row[10]
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve command {command_id}: {e}")
            return None
    
    def get_command_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get command execution statistics for KPI tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate time threshold
            threshold = datetime.utcnow().isoformat()
            
            # Total commands
            cursor.execute("""
                SELECT COUNT(*) FROM command_logs 
                WHERE created_at >= ?
            """, (threshold,))
            total_commands = cursor.fetchone()[0]
            
            # Successful commands
            cursor.execute("""
                SELECT COUNT(*) FROM command_logs 
                WHERE status = ? AND created_at >= ?
            """, (CommandStatus.COMPLETED.value, threshold))
            successful_commands = cursor.fetchone()[0]
            
            # Failed commands
            cursor.execute("""
                SELECT COUNT(*) FROM command_logs 
                WHERE status = ? AND created_at >= ?
            """, (CommandStatus.FAILED.value, threshold))
            failed_commands = cursor.fetchone()[0]
            
            # Average execution time
            cursor.execute("""
                SELECT AVG(execution_time_ms) FROM command_logs 
                WHERE status = ? AND created_at >= ?
            """, (CommandStatus.COMPLETED.value, threshold))
            avg_execution_time = cursor.fetchone()[0] or 0
            
            conn.close()
            
            accuracy = (successful_commands / total_commands * 100) if total_commands > 0 else 0
            
            return {
                "total_commands": total_commands,
                "successful_commands": successful_commands,
                "failed_commands": failed_commands,
                "accuracy_percentage": round(accuracy, 2),
                "avg_execution_time_ms": round(avg_execution_time, 2),
                "time_period_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Failed to get command stats: {e}")
            return {}
    
    def _generate_result_summary(self, result: Dict[str, Any]) -> str:
        """Generate a human-readable summary of command results"""
        if "records_count" in result:
            return f"Retrieved {result['records_count']} records from {result.get('dataset', 'unknown dataset')}"
        elif "report_type" in result:
            return f"Generated {result['report_type']} report"
        else:
            return "Command executed successfully"
