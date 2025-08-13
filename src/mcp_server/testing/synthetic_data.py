import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
from pathlib import Path

logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    """Generates synthetic municipal data for testing and MVP validation"""
    
    def __init__(self):
        self.data_dir = Path("./synthetic_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Municipal document templates
        self.document_templates = {
            "building_codes": [
                "Municipal Building Code Section {section}: {title}",
                "All construction projects must comply with {requirement}",
                "Permits are required for projects exceeding {threshold}",
                "Inspections must be completed at {stages}",
                "Violations may result in {penalties}"
            ],
            "zoning_regulations": [
                "Zone {zone_type} permits {allowed_uses}",
                "Setback requirements: {setback_distance} from property lines",
                "Height restrictions: maximum {max_height} feet",
                "Parking requirements: {parking_spaces} spaces per {unit_type}",
                "Special use permits required for {special_uses}"
            ],
            "service_procedures": [
                "Service request {request_type} processing time: {processing_time}",
                "Required documentation: {documents}",
                "Approval workflow: {workflow_steps}",
                "Contact department: {department} at {contact_info}",
                "Follow-up procedures: {follow_up_steps}"
            ],
            "incident_reports": [
                "Incident {incident_id} reported at {location} on {date}",
                "Type: {incident_type}, Priority: {priority_level}",
                "Description: {description}",
                "Assigned to: {assigned_officer}",
                "Status: {status}, Resolution time: {resolution_time}"
            ]
        }
        
        # Weather correlation scenarios
        self.weather_scenarios = [
            {"condition": "Heavy Rain", "impact": "Increased road maintenance requests", "correlation": 0.85},
            {"condition": "High Winds", "impact": "Tree/utility service calls", "correlation": 0.78},
            {"condition": "Extreme Heat", "impact": "AC-related service requests", "correlation": 0.72},
            {"condition": "Snow/Ice", "impact": "Snow removal and road safety", "correlation": 0.91},
            {"condition": "Drought", "impact": "Water conservation enforcement", "correlation": 0.65}
        ]
    
    def generate_building_code_document(self, section_count: int = 5) -> str:
        """Generate a synthetic building code document"""
        sections = []
        
        for i in range(section_count):
            section_num = 100 + i
            title = random.choice([
                "Building Permits and Applications",
                "Construction Standards and Materials",
                "Safety Requirements and Inspections",
                "Environmental Compliance",
                "Accessibility Standards"
            ])
            
            requirements = random.choice([
                "structural integrity standards",
                "fire safety protocols",
                "energy efficiency guidelines",
                "accessibility compliance",
                "environmental impact assessment"
            ])
            
            thresholds = random.choice([
                "500 square feet",
                "2 stories in height",
                "$50,000 in value",
                "structural modifications",
                "occupancy changes"
            ])
            
            stages = random.choice([
                "foundation, framing, and final",
                "electrical, plumbing, and structural",
                "rough-in, insulation, and finish",
                "site work, building, and occupancy"
            ])
            
            penalties = random.choice([
                "fines up to $10,000",
                "work stoppage orders",
                "permit revocation",
                "legal enforcement action",
                "compliance deadlines"
            ])
            
            section_content = f"""
            Section {section_num}: {title}
            
            All construction projects within city limits must obtain proper building permits.
            Applications must be submitted to the Department of Building and Safety.
            Processing time is typically 5-10 business days.
            
            Requirements:
            - All construction projects must comply with {requirements}
            - Permits are required for projects exceeding {thresholds}
            - Inspections must be completed at {stages}
            - Violations may result in {penalties}
            
            Contact Information:
            Department of Building and Safety
            Phone: (555) 123-4567
            Email: building@city.gov
            Office Hours: Monday-Friday, 8:00 AM - 5:00 PM
            """
            
            sections.append(section_content)
        
        return "\n\n".join(sections)
    
    def generate_zoning_regulation_document(self, zone_count: int = 4) -> str:
        """Generate a synthetic zoning regulation document"""
        zones = []
        
        zone_types = ["Residential", "Commercial", "Industrial", "Mixed-Use", "Agricultural"]
        allowed_uses = [
            "single-family homes and duplexes",
            "retail, office, and light industrial use",
            "manufacturing and warehousing",
            "residential and commercial development",
            "farming and related activities"
        ]
        
        for i in range(zone_count):
            zone_type = random.choice(zone_types)
            allowed_use = random.choice(allowed_uses)
            setback = random.choice(["10 feet", "15 feet", "20 feet", "25 feet"])
            max_height = random.choice(["35 feet", "45 feet", "60 feet", "75 feet"])
            parking_spaces = random.choice(["1", "2", "3", "4"])
            unit_type = random.choice(["residential unit", "1,000 sq ft", "employee", "bedroom"])
            
            zone_content = f"""
            Zone {zone_type} Regulations
            
            Permitted Uses:
            {zone_type} zones permit {allowed_use}.
            
            Development Standards:
            - Setback requirements: {setback} from property lines
            - Height restrictions: maximum {max_height}
            - Parking requirements: {parking_spaces} spaces per {unit_type}
            
            Special Provisions:
            - Home occupation permits available for qualifying businesses
            - Variances may be granted for unique circumstances
            - Historical preservation requirements apply in designated areas
            
            Application Process:
            Submit zoning permit application with site plan and supporting documentation.
            Planning Commission review required for major developments.
            Public hearing may be required for controversial projects.
            """
            
            zones.append(zone_content)
        
        return "\n\n".join(zones)
    
    def generate_service_procedure_document(self, procedure_count: int = 3) -> str:
        """Generate a synthetic service procedure document"""
        procedures = []
        
        request_types = [
            "Building Permit",
            "Zoning Variance",
            "Business License",
            "Special Event Permit",
            "Code Violation Report"
        ]
        
        processing_times = [
            "5-10 business days",
            "10-15 business days",
            "3-5 business days",
            "7-14 business days",
            "2-3 business days"
        ]
        
        for i in range(procedure_count):
            request_type = random.choice(request_types)
            processing_time = random.choice(processing_times)
            documents = random.choice([
                "completed application form, site plan, property survey",
                "business plan, financial statements, background check",
                "event details, security plan, insurance certificate",
                "violation photos, witness statements, timeline"
            ])
            
            workflow_steps = random.choice([
                "submission, review, approval, issuance",
                "application, inspection, correction, final approval",
                "intake, processing, verification, decision"
            ])
            
            departments = random.choice([
                "Department of Building and Safety",
                "Planning and Zoning Commission",
                "Business Licensing Office",
                "Special Events Coordinator",
                "Code Enforcement Division"
            ])
            
            contact_info = random.choice([
                "(555) 123-4567",
                "(555) 234-5678",
                "(555) 345-6789",
                "(555) 456-7890"
            ])
            
            procedure_content = f"""
            {request_type} Procedure
            
            Processing Time:
            Service request {request_type} processing time: {processing_time}
            
            Required Documentation:
            {documents}
            
            Approval Workflow:
            {workflow_steps}
            
            Contact Information:
            {departments}
            Phone: {contact_info}
            Email: {request_type.lower().replace(' ', '_')}@city.gov
            
            Follow-up Procedures:
            - Status updates available online
            - Email notifications for major milestones
            - Appeal process for denied applications
            """
            
            procedures.append(procedure_content)
        
        return "\n\n".join(procedures)
    
    def generate_incident_report_document(self, incident_count: int = 5) -> str:
        """Generate a synthetic incident report document"""
        incidents = []
        
        incident_types = [
            "Traffic Accident",
            "Property Damage",
            "Noise Complaint",
            "Code Violation",
            "Public Safety Concern"
        ]
        
        priority_levels = ["Low", "Medium", "High", "Critical"]
        statuses = ["Open", "In Progress", "Under Review", "Resolved", "Closed"]
        
        for i in range(incident_count):
            incident_id = f"INC-{2025:04d}-{random.randint(1000, 9999)}"
            incident_type = random.choice(incident_types)
            priority = random.choice(priority_levels)
            status = random.choice(statuses)
            
            location = random.choice([
                "123 Main Street",
                "456 Oak Avenue",
                "789 Pine Road",
                "321 Elm Street",
                "654 Maple Drive"
            ])
            
            description = random.choice([
                "Vehicle collision at intersection, no injuries reported",
                "Loud music from residential property after 10 PM",
                "Graffiti on public building, requires cleanup",
                "Broken streetlight, safety hazard for pedestrians",
                "Illegal dumping in public park area"
            ])
            
            assigned_officer = random.choice([
                "Officer Johnson",
                "Officer Smith",
                "Officer Davis",
                "Officer Wilson",
                "Officer Brown"
            ])
            
            resolution_time = random.choice([
                "2 hours",
                "1 business day",
                "3-5 business days",
                "1 week",
                "Ongoing investigation"
            ])
            
            incident_content = f"""
            Incident Report {incident_id}
            
            Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            Location: {location}
            Type: {incident_type}
            Priority: {priority}
            
            Description:
            {description}
            
            Assignment:
            Assigned to: {assigned_officer}
            Status: {status}
            Resolution time: {resolution_time}
            
            Actions Taken:
            - Initial response and assessment completed
            - Evidence collected and documented
            - Witness statements recorded
            - Follow-up investigation scheduled
            
            Notes:
            Standard operating procedures followed.
            No immediate safety concerns identified.
            Public notification not required.
            """
            
            incidents.append(incident_content)
        
        return "\n\n".join(incidents)
    
    def generate_weather_correlation_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """Generate synthetic weather correlation data"""
        correlation_data = []
        
        base_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            current_date = base_date + timedelta(days=day)
            
            # Generate weather data
            weather_condition = random.choice(self.weather_scenarios)
            temperature = random.randint(20, 95)
            humidity = random.randint(30, 90)
            precipitation = random.choice([0, 0.1, 0.5, 1.0, 2.0])
            
            # Generate correlated service requests
            base_requests = random.randint(50, 150)
            weather_multiplier = weather_condition["correlation"]
            weather_impact = int(base_requests * weather_multiplier * random.uniform(0.8, 1.2))
            
            correlation_entry = {
                "date": current_date.strftime("%Y-%m-%d"),
                "weather": {
                    "condition": weather_condition["condition"],
                    "temperature_f": temperature,
                    "humidity_percent": humidity,
                    "precipitation_inches": precipitation
                },
                "service_requests": {
                    "total": weather_impact,
                    "weather_related": int(weather_impact * weather_condition["correlation"]),
                    "normal_volume": base_requests
                },
                "correlation_analysis": {
                    "weather_impact": weather_condition["impact"],
                    "correlation_strength": weather_condition["correlation"],
                    "trend": "increased" if weather_impact > base_requests else "normal"
                }
            }
            
            correlation_data.append(correlation_entry)
        
        return correlation_data
    
    def generate_all_test_data(self) -> Dict[str, Any]:
        """Generate comprehensive test data for MVP validation"""
        try:
            test_data = {
                "building_codes": self.generate_building_code_document(5),
                "zoning_regulations": self.generate_zoning_regulation_document(4),
                "service_procedures": self.generate_service_procedure_document(3),
                "incident_reports": self.generate_incident_report_document(5),
                "weather_correlation": self.generate_weather_correlation_data(30)
            }
            
            # Save to files
            for data_type, content in test_data.items():
                if data_type == "weather_correlation":
                    # Save as JSON
                    file_path = self.data_dir / f"{data_type}.json"
                    with open(file_path, 'w') as f:
                        json.dump(content, f, indent=2)
                else:
                    # Save as text
                    file_path = self.data_dir / f"{data_type}.txt"
                    with open(file_path, 'w') as f:
                        f.write(content)
                
                logger.info(f"Generated {data_type} test data: {file_path}")
            
            return {
                "success": True,
                "files_generated": list(self.data_dir.glob("*")),
                "data_types": list(test_data.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate test data: {e}")
            return {"success": False, "error": str(e)}
    
    def get_test_data_summary(self) -> Dict[str, Any]:
        """Get summary of available test data"""
        try:
            files = list(self.data_dir.glob("*"))
            data_summary = {}
            
            for file_path in files:
                file_size = file_path.stat().st_size
                data_summary[file_path.name] = {
                    "size_bytes": file_size,
                    "size_kb": round(file_size / 1024, 2),
                    "type": file_path.suffix,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
            
            return {
                "data_directory": str(self.data_dir),
                "total_files": len(files),
                "files": data_summary,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get test data summary: {e}")
            return {"error": str(e)}

# Global synthetic data generator instance
synthetic_data_generator = SyntheticDataGenerator()
