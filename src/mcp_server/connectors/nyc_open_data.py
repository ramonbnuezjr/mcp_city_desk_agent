import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class NYCOpenDataConnector:
    """Connector for NYC Open Data API"""
    
    def __init__(self):
        self.base_url = "https://data.cityofnewyork.us/resource"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "MCP-City-Desk-Agent/1.0"
        })
        self._health_status = True
        
    def is_healthy(self) -> bool:
        """Check if the connector is healthy"""
        try:
            # Test with a simple endpoint
            response = self.session.get(f"{self.base_url}/erm2-nwe9.json?$limit=1")
            self._health_status = response.status_code == 200
            return self._health_status
        except Exception as e:
            logger.error(f"NYC Open Data health check failed: {e}")
            self._health_status = False
            return False
    
    async def query_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Query NYC Open Data based on parameters"""
        start_time = time.time()
        
        try:
            dataset = parameters.get("dataset", "erm2-nwe9")  # Default to 311 service requests
            filters = parameters.get("filters", {})
            limit = parameters.get("limit", 100)
            offset = parameters.get("offset", 0)
            
            # Build query URL
            query_url = f"{self.base_url}/{dataset}.json"
            
            # Add query parameters
            query_params = {"$limit": limit, "$offset": offset}
            
            # Add filters
            for key, value in filters.items():
                if isinstance(value, str):
                    query_params[f"{key}"] = value
                else:
                    query_params[f"{key}"] = str(value)
            
            logger.info(f"Querying NYC Open Data: {query_url} with params {query_params}")
            
            # Execute query
            response = self.session.get(query_url, params=query_params)
            response.raise_for_status()
            
            data = response.json()
            execution_time = int((time.time() - start_time) * 1000)
            
            result = {
                "dataset": dataset,
                "records_count": len(data),
                "data": data,
                "execution_time_ms": execution_time,
                "query_timestamp": datetime.utcnow().isoformat(),
                "filters_applied": filters
            }
            
            logger.info(f"NYC Open Data query successful: {len(data)} records in {execution_time}ms")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NYC Open Data API request failed: {e}")
            raise Exception(f"Data source unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"NYC Open Data query failed: {e}")
            raise Exception(f"Query execution failed: {str(e)}")
    
    async def get_available_datasets(self) -> List[Dict[str, Any]]:
        """Get list of available datasets"""
        try:
            # This would typically come from a metadata endpoint
            # For now, return common NYC datasets
            common_datasets = [
                {
                    "id": "erm2-nwe9",
                    "name": "311 Service Requests",
                    "description": "NYC 311 service requests and complaints",
                    "last_updated": "2025-01-27"
                },
                {
                    "id": "5uac-w243",
                    "name": "NYPD Motor Vehicle Collisions",
                    "description": "Motor vehicle collision data from NYPD",
                    "last_updated": "2025-01-27"
                },
                {
                    "id": "uvbq-3m68",
                    "name": "Street Tree Census",
                    "description": "Street tree data from NYC Parks",
                    "last_updated": "2025-01-27"
                }
            ]
            return common_datasets
        except Exception as e:
            logger.error(f"Failed to get available datasets: {e}")
            return []
    
    async def get_dataset_schema(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get schema information for a specific dataset"""
        try:
            # Query the dataset with $limit=0 to get metadata
            response = self.session.get(f"{self.base_url}/{dataset_id}.json?$limit=0")
            response.raise_for_status()
            
            # Extract column information from response headers or metadata
            # This is a simplified approach - actual implementation would parse metadata
            return {
                "dataset_id": dataset_id,
                "columns": ["Column information would be extracted here"],
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get dataset schema for {dataset_id}: {e}")
            return None
