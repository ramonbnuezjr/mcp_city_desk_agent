import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class PromptLibrary:
    """Comprehensive prompt library for testing and MVP validation"""
    
    def __init__(self):
        self.prompts_dir = Path("./prompt_library")
        self.prompts_dir.mkdir(exist_ok=True)
        
        # Initialize prompt categories
        self.prompt_categories = {
            "data_retrieval": self._get_data_retrieval_prompts(),
            "report_generation": self._get_report_generation_prompts(),
            "correlation_analysis": self._get_correlation_analysis_prompts(),
            "compliance_checking": self._get_compliance_checking_prompts(),
            "service_workflow": self._get_service_workflow_prompts(),
            "edge_cases": self._get_edge_case_prompts(),
            "performance_testing": self._get_performance_testing_prompts()
        }
        
        # Save prompts to files
        self._save_prompts_to_files()
    
    def _get_data_retrieval_prompts(self) -> List[Dict[str, Any]]:
        """Get data retrieval prompts for testing"""
        return [
            {
                "id": "DR001",
                "category": "data_retrieval",
                "complexity": "simple",
                "description": "Basic building permit information lookup",
                "prompt": "What are the requirements for obtaining a building permit?",
                "expected_response_type": "factual_list",
                "context_required": "building_codes",
                "difficulty": 1
            },
            {
                "id": "DR002",
                "category": "data_retrieval",
                "complexity": "simple",
                "description": "Zoning regulations for specific property type",
                "prompt": "What can I build in a residential zone?",
                "expected_response_type": "factual_list",
                "context_required": "zoning_regulations",
                "difficulty": 1
            },
            {
                "id": "DR003",
                "category": "data_retrieval",
                "complexity": "medium",
                "description": "Multi-document information synthesis",
                "prompt": "Compare the requirements for building permits vs. zoning variances",
                "expected_response_type": "comparison_table",
                "context_required": "building_codes,zoning_regulations",
                "difficulty": 2
            },
            {
                "id": "DR004",
                "category": "data_retrieval",
                "complexity": "complex",
                "description": "Cross-reference multiple data sources",
                "prompt": "What are the environmental compliance requirements for a commercial building project in a mixed-use zone?",
                "expected_response_type": "comprehensive_analysis",
                "context_required": "building_codes,zoning_regulations,service_procedures",
                "difficulty": 3
            }
        ]
    
    def _get_report_generation_prompts(self) -> List[Dict[str, Any]]:
        """Get report generation prompts for testing"""
        return [
            {
                "id": "RG001",
                "category": "report_generation",
                "complexity": "simple",
                "description": "Weekly service request summary",
                "prompt": "Generate a weekly summary of all service requests by type and priority",
                "expected_response_type": "structured_report",
                "context_required": "incident_reports",
                "difficulty": 2
            },
            {
                "id": "RG002",
                "category": "report_generation",
                "complexity": "medium",
                "description": "Compliance status report",
                "prompt": "Create a compliance status report for all active building permits, highlighting any violations or pending actions",
                "expected_response_type": "status_report",
                "context_required": "building_codes,incident_reports",
                "difficulty": 3
            },
            {
                "id": "RG003",
                "category": "report_generation",
                "complexity": "complex",
                "description": "Executive summary with recommendations",
                "prompt": "Prepare an executive summary of municipal operations for the past month, including key metrics, trends, and recommendations for improvement",
                "expected_response_type": "executive_summary",
                "context_required": "all",
                "difficulty": 4
            }
        ]
    
    def _get_correlation_analysis_prompts(self) -> List[Dict[str, Any]]:
        """Get correlation analysis prompts for testing"""
        return [
            {
                "id": "CA001",
                "category": "correlation_analysis",
                "complexity": "simple",
                "description": "Weather impact on service demand",
                "prompt": "How does weather affect the volume of service requests?",
                "expected_response_type": "correlation_analysis",
                "context_required": "weather_correlation",
                "difficulty": 2
            },
            {
                "id": "CA002",
                "category": "correlation_analysis",
                "complexity": "medium",
                "description": "Seasonal patterns in municipal operations",
                "prompt": "Analyze seasonal patterns in building permit applications and identify peak periods",
                "expected_response_type": "trend_analysis",
                "context_required": "building_codes,weather_correlation",
                "difficulty": 3
            },
            {
                "id": "CA003",
                "category": "correlation_analysis",
                "complexity": "complex",
                "description": "Multi-factor impact analysis",
                "prompt": "What factors contribute to delays in service request resolution, and how do they interact with weather conditions?",
                "expected_response_type": "multivariate_analysis",
                "context_required": "incident_reports,weather_correlation,service_procedures",
                "difficulty": 4
            }
        ]
    
    def _get_compliance_checking_prompts(self) -> List[Dict[str, Any]]:
        """Get compliance checking prompts for testing"""
        return [
            {
                "id": "CC001",
                "category": "compliance_checking",
                "complexity": "simple",
                "description": "Basic permit compliance check",
                "prompt": "Is a building permit required for a 200 sq ft garden shed?",
                "expected_response_type": "yes_no_with_explanation",
                "context_required": "building_codes",
                "difficulty": 1
            },
            {
                "id": "CC002",
                "category": "compliance_checking",
                "complexity": "medium",
                "description": "Multi-regulation compliance assessment",
                "prompt": "Check if a proposed commercial development complies with all zoning, building, and environmental regulations",
                "expected_response_type": "compliance_assessment",
                "context_required": "building_codes,zoning_regulations",
                "difficulty": 3
            },
            {
                "id": "CC003",
                "category": "compliance_checking",
                "complexity": "complex",
                "description": "Compliance audit with recommendations",
                "prompt": "Conduct a comprehensive compliance audit of all active projects and provide recommendations for addressing any violations",
                "expected_response_type": "audit_report",
                "context_required": "all",
                "difficulty": 4
            }
        ]
    
    def _get_service_workflow_prompts(self) -> List[Dict[str, Any]]:
        """Get service workflow prompts for testing"""
        return [
            {
                "id": "SW001",
                "category": "service_workflow",
                "complexity": "simple",
                "description": "Service request status check",
                "prompt": "What is the current status of incident report INC-2025-1234?",
                "expected_response_type": "status_update",
                "context_required": "incident_reports",
                "difficulty": 1
            },
            {
                "id": "SW002",
                "category": "service_workflow",
                "complexity": "medium",
                "description": "Workflow optimization suggestion",
                "prompt": "Analyze the current service request workflow and suggest improvements to reduce processing time",
                "expected_response_type": "workflow_analysis",
                "context_required": "service_procedures,incident_reports",
                "difficulty": 3
            },
            {
                "id": "SW003",
                "category": "service_workflow",
                "complexity": "complex",
                "description": "End-to-end process mapping",
                "prompt": "Map the complete process from initial service request to final resolution, identifying bottlenecks and optimization opportunities",
                "expected_response_type": "process_mapping",
                "context_required": "all",
                "difficulty": 4
            }
        ]
    
    def _get_edge_case_prompts(self) -> List[Dict[str, Any]]:
        """Get edge case prompts for testing robustness"""
        return [
            {
                "id": "EC001",
                "category": "edge_cases",
                "complexity": "medium",
                "description": "Ambiguous regulation interpretation",
                "prompt": "A property owner wants to convert a residential garage to a home office. Does this require a permit?",
                "expected_response_type": "interpretation_with_reasoning",
                "context_required": "building_codes,zoning_regulations",
                "difficulty": 3
            },
            {
                "id": "EC002",
                "category": "edge_cases",
                "complexity": "medium",
                "description": "Conflicting requirements",
                "prompt": "What happens when building code requirements conflict with zoning regulations?",
                "expected_response_type": "conflict_resolution",
                "context_required": "building_codes,zoning_regulations",
                "difficulty": 3
            },
            {
                "id": "EC003",
                "category": "edge_cases",
                "complexity": "high",
                "description": "Emergency situation handling",
                "prompt": "How should code enforcement handle an emergency situation where immediate action is required but proper procedures cannot be followed?",
                "expected_response_type": "emergency_protocol",
                "context_required": "all",
                "difficulty": 4
            }
        ]
    
    def _get_performance_testing_prompts(self) -> List[Dict[str, Any]]:
        """Get performance testing prompts for system validation"""
        return [
            {
                "id": "PT001",
                "category": "performance_testing",
                "complexity": "simple",
                "description": "Large dataset query",
                "prompt": "Retrieve all incident reports from the past year and categorize them by type and priority",
                "expected_response_type": "categorized_data",
                "context_required": "incident_reports",
                "difficulty": 2
            },
            {
                "id": "PT002",
                "category": "performance_testing",
                "complexity": "medium",
                "description": "Complex multi-source query",
                "prompt": "Analyze the relationship between weather conditions, service request volume, and resolution times over the past 6 months",
                "expected_response_type": "comprehensive_analysis",
                "context_required": "weather_correlation,incident_reports",
                "difficulty": 3
            },
            {
                "id": "PT003",
                "category": "performance_testing",
                "complexity": "high",
                "description": "Real-time data processing",
                "prompt": "Monitor incoming service requests in real-time and provide instant analysis and recommendations",
                "expected_response_type": "real_time_analysis",
                "context_required": "all",
                "difficulty": 4
            }
        ]
    
    def _save_prompts_to_files(self):
        """Save all prompts to JSON files for easy access"""
        try:
            for category, prompts in self.prompt_categories.items():
                file_path = self.prompts_dir / f"{category}_prompts.json"
                with open(file_path, 'w') as f:
                    json.dump(prompts, f, indent=2)
                logger.info(f"Saved {len(prompts)} prompts to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save prompts to files: {e}")
    
    def get_prompts_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get prompts for a specific category"""
        return self.prompt_categories.get(category, [])
    
    def get_prompts_by_complexity(self, complexity: str) -> List[Dict[str, Any]]:
        """Get prompts by complexity level"""
        all_prompts = []
        for category_prompts in self.prompt_categories.values():
            all_prompts.extend([p for p in category_prompts if p["complexity"] == complexity])
        return all_prompts
    
    def get_prompts_by_difficulty(self, min_difficulty: int = 1, max_difficulty: int = 4) -> List[Dict[str, Any]]:
        """Get prompts within a difficulty range"""
        all_prompts = []
        for category_prompts in self.prompt_categories.values():
            all_prompts.extend([
                p for p in category_prompts 
                if min_difficulty <= p["difficulty"] <= max_difficulty
            ])
        return all_prompts
    
    def get_random_prompt(self, category: Optional[str] = None, complexity: Optional[str] = None) -> Dict[str, Any]:
        """Get a random prompt with optional filtering"""
        import random
        
        if category:
            prompts = self.get_prompts_by_category(category)
        elif complexity:
            prompts = self.get_prompts_by_complexity(complexity)
        else:
            prompts = []
            for category_prompts in self.prompt_categories.values():
                prompts.extend(category_prompts)
        
        if prompts:
            return random.choice(prompts)
        else:
            return {"error": "No prompts found with specified criteria"}
    
    def get_test_suite(self, categories: Optional[List[str]] = None, 
                       complexity_levels: Optional[List[str]] = None,
                       difficulty_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Get a comprehensive test suite based on criteria"""
        test_suite = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "total_prompts": 0,
                "categories_included": [],
                "complexity_levels": complexity_levels or ["simple", "medium", "complex", "high"],
                "difficulty_range": difficulty_range or (1, 4)
            },
            "prompts": {}
        }
        
        # Determine which categories to include
        if categories:
            categories_to_include = categories
        else:
            categories_to_include = list(self.prompt_categories.keys())
        
        test_suite["metadata"]["categories_included"] = categories_to_include
        
        # Filter prompts based on criteria
        for category in categories_to_include:
            if category in self.prompt_categories:
                category_prompts = self.prompt_categories[category]
                
                # Apply complexity filter
                if complexity_levels:
                    category_prompts = [p for p in category_prompts if p["complexity"] in complexity_levels]
                
                # Apply difficulty filter
                if difficulty_range:
                    min_diff, max_diff = difficulty_range
                    category_prompts = [p for p in category_prompts if min_diff <= p["difficulty"] <= max_diff]
                
                test_suite["prompts"][category] = category_prompts
                test_suite["metadata"]["total_prompts"] += len(category_prompts)
        
        return test_suite
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the prompt library"""
        stats = {
            "total_prompts": 0,
            "by_category": {},
            "by_complexity": {},
            "by_difficulty": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Count by category
        for category, prompts in self.prompt_categories.items():
            stats["by_category"][category] = len(prompts)
            stats["total_prompts"] += len(prompts)
        
        # Count by complexity
        complexity_counts = {}
        difficulty_counts = {}
        
        for category_prompts in self.prompt_categories.values():
            for prompt in category_prompts:
                # Complexity counts
                complexity = prompt["complexity"]
                complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
                
                # Difficulty counts
                difficulty = prompt["difficulty"]
                difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
        
        stats["by_complexity"] = complexity_counts
        stats["by_difficulty"] = difficulty_counts
        
        return stats
    
    def export_prompts_for_testing(self, output_file: str = "test_prompts.json") -> bool:
        """Export all prompts to a single file for testing"""
        try:
            all_prompts = []
            for category, prompts in self.prompt_categories.items():
                for prompt in prompts:
                    prompt_copy = prompt.copy()
                    prompt_copy["category"] = category
                    all_prompts.append(prompt_copy)
            
            output_path = self.prompts_dir / output_file
            with open(output_path, 'w') as f:
                json.dump(all_prompts, f, indent=2)
            
            logger.info(f"Exported {len(all_prompts)} prompts to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export prompts: {e}")
            return False

# Global prompt library instance
prompt_library = PromptLibrary()
