import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time
import json

from ..config.settings import settings

logger = logging.getLogger(__name__)

class OpenWeatherMapConnector:
    """Connector for OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = settings.weather_api_key
        self.base_url = settings.weather_base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "MCP-City-Desk-Agent/1.0"
        })
        self._health_status = True
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes cache
        
    def is_healthy(self) -> bool:
        """Check if the connector is healthy"""
        try:
            # Test with a simple endpoint
            response = self.session.get(f"{self.base_url}/weather", params={
                "q": "New York",
                "appid": self.api_key,
                "units": "metric"
            })
            self._health_status = response.status_code == 200
            return self._health_status
        except Exception as e:
            logger.error(f"OpenWeatherMap health check failed: {e}")
            self._health_status = False
            return False
    
    async def get_current_weather(self, city: str = "New York", 
                                 country_code: str = "US",
                                 units: str = "metric") -> Dict[str, Any]:
        """Get current weather for a city"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"current_{city}_{country_code}_{units}"
            if cache_key in self._cache:
                cached_data = self._cache[cache_key]
                if datetime.utcnow() - cached_data["timestamp"] < timedelta(seconds=self._cache_ttl):
                    logger.info(f"Returning cached weather data for {city}")
                    return cached_data["data"]
            
            # Build query parameters
            params = {
                "q": f"{city},{country_code}",
                "appid": self.api_key,
                "units": units
            }
            
            logger.info(f"Fetching current weather for {city}, {country_code}")
            
            # Make API call
            response = self.session.get(f"{self.base_url}/weather", params=params)
            response.raise_for_status()
            
            weather_data = response.json()
            execution_time = int((time.time() - start_time) * 1000)
            
            # Format the response
            result = {
                "city": city,
                "country": country_code,
                "timestamp": datetime.utcnow().isoformat(),
                "weather": {
                    "main": weather_data.get("weather", [{}])[0].get("main", "Unknown"),
                    "description": weather_data.get("weather", [{}])[0].get("description", "Unknown"),
                    "icon": weather_data.get("weather", [{}])[0].get("icon", ""),
                    "temperature": {
                        "current": weather_data.get("main", {}).get("temp"),
                        "feels_like": weather_data.get("main", {}).get("feels_like"),
                        "min": weather_data.get("main", {}).get("temp_min"),
                        "max": weather_data.get("main", {}).get("temp_max")
                    },
                    "humidity": weather_data.get("main", {}).get("humidity"),
                    "pressure": weather_data.get("main", {}).get("pressure"),
                    "wind": {
                        "speed": weather_data.get("wind", {}).get("speed"),
                        "direction": weather_data.get("wind", {}).get("deg")
                    },
                    "visibility": weather_data.get("visibility"),
                    "clouds": weather_data.get("clouds", {}).get("all")
                },
                "execution_time_ms": execution_time
            }
            
            # Cache the result
            self._cache[cache_key] = {
                "data": result,
                "timestamp": datetime.utcnow()
            }
            
            logger.info(f"Current weather for {city}: {result['weather']['main']} at {result['weather']['temperature']['current']}°C")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenWeatherMap API request failed: {e}")
            raise Exception(f"Weather data unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"Weather data retrieval failed: {e}")
            raise Exception(f"Weather query failed: {str(e)}")
    
    async def get_weather_forecast(self, city: str = "New York", 
                                  country_code: str = "US",
                                  days: int = 5,
                                  units: str = "metric") -> Dict[str, Any]:
        """Get weather forecast for a city"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"forecast_{city}_{country_code}_{days}_{units}"
            if cache_key in self._cache:
                cached_data = self._cache[cache_key]
                if datetime.utcnow() - cached_data["timestamp"] < timedelta(seconds=self._cache_ttl):
                    logger.info(f"Returning cached forecast data for {city}")
                    return cached_data["data"]
            
            # Build query parameters
            params = {
                "q": f"{city},{country_code}",
                "appid": self.api_key,
                "units": units,
                "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            logger.info(f"Fetching {days}-day weather forecast for {city}, {country_code}")
            
            # Make API call
            response = self.session.get(f"{self.base_url}/forecast", params=params)
            response.raise_for_status()
            
            forecast_data = response.json()
            execution_time = int((time.time() - start_time) * 1000)
            
            # Process forecast data
            forecasts = []
            for item in forecast_data.get("list", []):
                forecast = {
                    "datetime": datetime.fromtimestamp(item.get("dt")).isoformat(),
                    "weather": {
                        "main": item.get("weather", [{}])[0].get("main", "Unknown"),
                        "description": item.get("weather", [{}])[0].get("description", "Unknown"),
                        "icon": item.get("weather", [{}])[0].get("icon", "")
                    },
                    "temperature": {
                        "current": item.get("main", {}).get("temp"),
                        "feels_like": item.get("main", {}).get("feels_like"),
                        "min": item.get("main", {}).get("temp_min"),
                        "max": item.get("main", {}).get("temp_max")
                    },
                    "humidity": item.get("main", {}).get("humidity"),
                    "pressure": item.get("main", {}).get("pressure"),
                    "wind": {
                        "speed": item.get("wind", {}).get("speed"),
                        "direction": item.get("wind", {}).get("deg")
                    },
                    "clouds": item.get("clouds", {}).get("all"),
                    "pop": item.get("pop", 0)  # Probability of precipitation
                }
                forecasts.append(forecast)
            
            result = {
                "city": city,
                "country": country_code,
                "forecast_days": days,
                "timestamp": datetime.utcnow().isoformat(),
                "forecasts": forecasts,
                "execution_time_ms": execution_time
            }
            
            # Cache the result
            self._cache[cache_key] = {
                "data": result,
                "timestamp": datetime.utcnow()
            }
            
            logger.info(f"Forecast for {city}: {len(forecasts)} data points retrieved")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenWeatherMap forecast API request failed: {e}")
            raise Exception(f"Weather forecast unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"Weather forecast retrieval failed: {e}")
            raise Exception(f"Weather forecast query failed: {str(e)}")
    
    async def get_weather_alerts(self, city: str = "New York", 
                                country_code: str = "US") -> Dict[str, Any]:
        """Get weather alerts for a city"""
        start_time = time.time()
        
        try:
            # Build query parameters
            params = {
                "q": f"{city},{country_code}",
                "appid": self.api_key
            }
            
            logger.info(f"Fetching weather alerts for {city}, {country_code}")
            
            # Make API call
            response = self.session.get(f"{self.base_url}/onecall", params=params)
            response.raise_for_status()
            
            alert_data = response.json()
            execution_time = int((time.time() - start_time) * 1000)
            
            # Process alert data
            alerts = []
            if "alerts" in alert_data:
                for alert in alert_data["alerts"]:
                    alert_info = {
                        "sender": alert.get("sender_name", "Unknown"),
                        "event": alert.get("event", "Unknown"),
                        "start": datetime.fromtimestamp(alert.get("start")).isoformat(),
                        "end": datetime.fromtimestamp(alert.get("end")).isoformat(),
                        "description": alert.get("description", "No description"),
                        "tags": alert.get("tags", [])
                    }
                    alerts.append(alert_info)
            
            result = {
                "city": city,
                "country": country_code,
                "timestamp": datetime.utcnow().isoformat(),
                "alerts_count": len(alerts),
                "alerts": alerts,
                "execution_time_ms": execution_time
            }
            
            logger.info(f"Weather alerts for {city}: {len(alerts)} alerts found")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenWeatherMap alerts API request failed: {e}")
            raise Exception(f"Weather alerts unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"Weather alerts retrieval failed: {e}")
            raise Exception(f"Weather alerts query failed: {str(e)}")
    
    async def correlate_with_events(self, weather_data: Dict[str, Any], 
                                  event_type: str = "service_requests") -> Dict[str, Any]:
        """Correlate weather data with municipal events"""
        try:
            # This is a placeholder for weather-event correlation logic
            # In a real implementation, this would analyze patterns between
            # weather conditions and municipal service demand
            
            correlation_analysis = {
                "weather_condition": weather_data.get("weather", {}).get("main", "Unknown"),
                "temperature": weather_data.get("weather", {}).get("temperature", {}).get("current"),
                "event_type": event_type,
                "correlation_factors": {
                    "temperature_impact": "High temperatures may increase AC-related service requests",
                    "precipitation_impact": "Rain/snow may increase road maintenance requests",
                    "wind_impact": "High winds may increase tree/utility service requests"
                },
                "recommendations": [
                    "Monitor service request patterns during extreme weather",
                    "Prepare additional resources for weather-related incidents",
                    "Use weather data to predict service demand"
                ]
            }
            
            return {
                "correlation_analysis": True,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": correlation_analysis
            }
            
        except Exception as e:
            logger.error(f"Weather correlation analysis failed: {e}")
            return {
                "correlation_analysis": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_size = len(self._cache)
        cache_keys = list(self._cache.keys())
        
        return {
            "cache_size": cache_size,
            "cache_keys": cache_keys,
            "cache_ttl_seconds": self._cache_ttl,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def clear_cache(self) -> bool:
        """Clear the weather data cache"""
        try:
            self._cache.clear()
            logger.info("Weather data cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
