#!/usr/bin/env python3
"""
Simple test script for MCP City Desk Agent
"""

import asyncio
import json
from src.mcp_server.models.commands import CommandRequest, CommandStatus
from src.mcp_server.connectors.nyc_open_data import NYCOpenDataConnector
from src.mcp_server.utils.logger import CommandLogger

async def test_nyc_connector():
    """Test NYC Open Data connector"""
    print("Testing NYC Open Data Connector...")
    
    connector = NYCOpenDataConnector()
    
    # Test health check
    is_healthy = connector.is_healthy()
    print(f"Connector healthy: {is_healthy}")
    
    if is_healthy:
        # Test data query
        try:
            result = await connector.query_data({
                "dataset": "erm2-nwe9",
                "limit": 5
            })
            print(f"Query successful: {result['records_count']} records")
            print(f"Execution time: {result['execution_time_ms']}ms")
        except Exception as e:
            print(f"Query failed: {e}")

async def test_command_logger():
    """Test command logger"""
    print("\nTesting Command Logger...")
    
    logger = CommandLogger("test_logs.db")
    
    # Test health check
    is_healthy = logger.is_healthy()
    print(f"Logger healthy: {is_healthy}")
    
    if is_healthy:
        # Test command logging
        test_command = CommandRequest(
            intent="data_query",
            parameters={"dataset": "test_dataset"},
            user_id="test_user"
        )
        
        command_id = "test_cmd_001"
        logger.log_command_start(command_id, test_command)
        print("Command start logged")
        
        # Simulate success
        result = {"records_count": 10, "dataset": "test_dataset"}
        logger.log_command_success(command_id, result)
        print("Command success logged")
        
        # Get stats
        stats = logger.get_command_stats()
        print(f"Command stats: {stats}")

async def main():
    """Run all tests"""
    print("MCP City Desk Agent - Test Suite")
    print("=" * 40)
    
    await test_nyc_connector()
    await test_command_logger()
    
    print("\nTest suite completed!")

if __name__ == "__main__":
    asyncio.run(main())
