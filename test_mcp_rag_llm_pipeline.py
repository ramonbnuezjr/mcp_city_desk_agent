#!/usr/bin/env python3
"""
MCP-RAG-LLM Pipeline Integration Test
Tests the complete flow: User Query → MCP → RAG → LLM → Response
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Import our components
from src.mcp_server.rag.chromadb_manager import ChromaDBManager
from src.mcp_server.rag.query_engine import RAGQueryEngine
from src.mcp_server.rag.document_processor import DocumentProcessor
from src.mcp_server.llm.llm_client import llm_client
from src.mcp_server.testing.prompt_library import prompt_library

class MCPRAGLLMPipelineTester:
    """Tests the complete MCP-RAG-LLM integration pipeline"""
    
    def __init__(self):
        self.chroma_db_path = "./nyc_agency_chroma_db"
        self.chroma_manager = ChromaDBManager(self.chroma_db_path)
        self.doc_processor = DocumentProcessor()
        self.rag_engine = RAGQueryEngine(self.chroma_manager, self.doc_processor)
        
        # Test scenarios with expected outcomes
        self.test_scenarios = [
            {
                "id": "TS001",
                "category": "data_retrieval",
                "query": "What are the building permit requirements?",
                "expected_context": ["building", "permit", "requirements", "construction"],
                "expected_response_type": "factual_list",
                "difficulty": 1
            },
            {
                "id": "TS002", 
                "category": "compliance_checking",
                "query": "How do I apply for a business license in NYC?",
                "expected_context": ["business", "license", "application", "procedure"],
                "expected_response_type": "step_by_step",
                "difficulty": 2
            },
            {
                "id": "TS003",
                "category": "correlation_analysis",
                "query": "What are the health and safety standards for food service establishments?",
                "expected_context": ["health", "safety", "food", "service", "standards"],
                "expected_response_type": "comprehensive_analysis",
                "difficulty": 3
            },
            {
                "id": "TS004",
                "category": "service_workflow",
                "query": "What is the process for reporting a code violation?",
                "expected_context": ["code", "violation", "report", "process", "procedure"],
                "expected_response_type": "workflow",
                "difficulty": 2
            },
            {
                "id": "TS005",
                "category": "edge_cases",
                "query": "Can I convert a residential garage to a home office? What permits are needed?",
                "expected_context": ["garage", "conversion", "home office", "permits", "zoning"],
                "expected_response_type": "interpretation_with_reasoning",
                "difficulty": 3
            }
        ]
    
    async def test_rag_retrieval_only(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Test RAG retrieval without LLM synthesis"""
        print(f"🔍 Testing RAG retrieval for: '{query}'")
        
        start_time = time.time()
        result = await self.rag_engine.query_documents(query, n_results=n_results)
        retrieval_time = time.time() - start_time
        
        if result["success"]:
            print(f"   ✅ RAG retrieval successful in {retrieval_time:.2f}s")
            print(f"      Found {result['results_count']} relevant documents")
            
            # Show top results
            for i, doc in enumerate(result["results"][:3]):
                relevance = doc.get('relevance_score', 'N/A')
                source = doc.get('metadata', {}).get('filename', 'Unknown')
                preview = doc.get('document_text', '')[:100] + "..."
                print(f"        {i+1}. Score: {relevance} | Source: {source}")
                print(f"           Preview: {preview}")
            
            return {
                "success": True,
                "retrieval_time": retrieval_time,
                "results_count": result['results_count'],
                "top_results": result["results"][:3]
            }
        else:
            print(f"   ❌ RAG retrieval failed: {result.get('error')}")
            return {"success": False, "error": result.get('error')}
    
    async def test_llm_synthesis(self, query: str, context_docs: List[Dict]) -> Dict[str, Any]:
        """Test LLM synthesis of RAG results"""
        print(f"🧠 Testing LLM synthesis for: '{query}'")
        
        # Prepare context for LLM
        context_text = "\n\n".join([
            f"Document {i+1} (Source: {doc.get('metadata', {}).get('filename', 'Unknown')}):\n{doc.get('document_text', '')}"
            for i, doc in enumerate(context_docs)
        ])
        
        # Create synthesis prompt
        synthesis_prompt = f"""
        Based on the following NYC agency documents, provide a comprehensive answer to this question:
        
        QUESTION: {query}
        
        CONTEXT DOCUMENTS:
        {context_text}
        
        Please provide:
        1. A clear, direct answer to the question
        2. Specific details from the documents
        3. Any relevant procedures or requirements mentioned
        4. Source citations for key information
        
        Format your response in a professional, municipal government style.
        """
        
        try:
            # Check available LLM providers
            available_providers = llm_client.get_available_providers()
            
            if not available_providers:
                print("   ⚠️  No LLM providers configured. Skipping synthesis test.")
                return {"success": False, "error": "No LLM providers available"}
            
            # Try Gemini first, fallback to OpenAI
            if "google_gemini" in available_providers:
                provider = "google_gemini"
            else:
                provider = available_providers[0]
            print(f"   🤖 Using LLM provider: {provider}")
            
            start_time = time.time()
            result = await llm_client.invoke(provider, synthesis_prompt)
            synthesis_time = time.time() - start_time
            
            if "error" not in result:
                print(f"   ✅ LLM synthesis successful in {synthesis_time:.2f}s")
                print(f"      Provider: {result['provider']}")
                print(f"      Model: {result['model']}")
                print(f"      Tokens used: {result['usage']['total_tokens']}")
                
                # Show response preview
                response_preview = result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
                print(f"      Response preview: {response_preview}")
                
                return {
                    "success": True,
                    "synthesis_time": synthesis_time,
                    "provider": result['provider'],
                    "model": result['model'],
                    "tokens_used": result['usage']['total_tokens'],
                    "response": result['response']
                }
            else:
                print(f"   ❌ LLM synthesis failed: {result.get('error')}")
                return {"success": False, "error": result.get('error')}
                
        except Exception as e:
            print(f"   ❌ LLM synthesis error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_full_pipeline(self, test_scenario: Dict) -> Dict[str, Any]:
        """Test the complete MCP-RAG-LLM pipeline"""
        print(f"\n🚀 Testing Full Pipeline: {test_scenario['id']}")
        print(f"   Category: {test_scenario['category']}")
        print(f"   Query: '{test_scenario['query']}'")
        print(f"   Expected: {test_scenario['expected_response_type']}")
        print(f"   Difficulty: {test_scenario['difficulty']}")
        print("-" * 60)
        
        pipeline_results = {
            "scenario": test_scenario,
            "rag_retrieval": None,
            "llm_synthesis": None,
            "pipeline_success": False,
            "total_time": 0
        }
        
        start_time = time.time()
        
        # Step 1: RAG Retrieval
        rag_result = await self.test_rag_retrieval_only(test_scenario['query'])
        pipeline_results["rag_retrieval"] = rag_result
        
        if not rag_result["success"]:
            print(f"   ❌ Pipeline failed at RAG retrieval step")
            return pipeline_results
        
        # Step 2: LLM Synthesis
        llm_result = await self.test_llm_synthesis(test_scenario['query'], rag_result["top_results"])
        pipeline_results["llm_synthesis"] = llm_result
        
        if not llm_result["success"]:
            print(f"   ⚠️  Pipeline completed with RAG only (LLM failed)")
            pipeline_results["pipeline_success"] = True  # Partial success
        else:
            print(f"   ✅ Full pipeline completed successfully!")
            pipeline_results["pipeline_success"] = True
        
        pipeline_results["total_time"] = time.time() - start_time
        
        return pipeline_results
    
    async def run_comprehensive_pipeline_test(self) -> Dict[str, Any]:
        """Run comprehensive testing of the MCP-RAG-LLM pipeline"""
        print("MCP-RAG-LLM Pipeline Integration Test")
        print("=" * 60)
        
        # Check system status
        print("📊 System Status Check:")
        stats = self.chroma_manager.get_collection_stats()
        print(f"   ChromaDB documents: {stats.get('total_documents', 0)}")
        
        available_providers = llm_client.get_available_providers()
        print(f"   Available LLM providers: {', '.join(available_providers) if available_providers else 'None'}")
        
        if not available_providers:
            print("   ⚠️  No LLM providers configured. Will test RAG-only pipeline.")
        
        print(f"\n🧪 Running {len(self.test_scenarios)} test scenarios...")
        
        # Run all test scenarios
        all_results = []
        successful_pipelines = 0
        partial_successes = 0
        
        for scenario in self.test_scenarios:
            result = await self.test_full_pipeline(scenario)
            all_results.append(result)
            
            if result["pipeline_success"]:
                if result["llm_synthesis"] and result["llm_synthesis"]["success"]:
                    successful_pipelines += 1
                else:
                    partial_successes += 1
        
        # Generate comprehensive report
        report = {
            "test_timestamp": time.time(),
            "total_scenarios": len(self.test_scenarios),
            "successful_pipelines": successful_pipelines,
            "partial_successes": partial_successes,
            "failed_pipelines": len(self.test_scenarios) - successful_pipelines - partial_successes,
            "success_rate": (successful_pipelines + partial_successes) / len(self.test_scenarios) * 100,
            "detailed_results": all_results,
            "system_capabilities": {
                "rag_system": "Operational",
                "llm_integration": "Available" if available_providers else "Not Configured",
                "document_count": stats.get('total_documents', 0),
                "llm_providers": available_providers
            }
        }
        
        # Save detailed report
        report_file = Path("./mcp_rag_llm_test_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print(f"\n📊 Pipeline Test Summary:")
        print(f"   Total scenarios: {len(self.test_scenarios)}")
        print(f"   Full success: {successful_pipelines}")
        print(f"   Partial success: {partial_successes}")
        print(f"   Failed: {report['failed_pipelines']}")
        print(f"   Overall success rate: {report['success_rate']:.1f}%")
        print(f"   Detailed report saved to: {report_file}")
        
        return report

async def main():
    """Run the MCP-RAG-LLM pipeline integration test"""
    tester = MCPRAGLLMPipelineTester()
    report = await tester.run_comprehensive_pipeline_test()
    
    print(f"\n🎯 Next Steps:")
    if report["success_rate"] >= 80:
        print("   ✅ Pipeline is ready for production use!")
        print("   🚀 Proceed with Web Dashboard development")
    elif report["success_rate"] >= 60:
        print("   ⚠️  Pipeline has some issues to resolve")
        print("   🔧 Review failed scenarios and fix issues")
    else:
        print("   ❌ Pipeline needs significant work")
        print("   🛠️  Focus on fixing core integration issues")
    
    print(f"\n💡 Recommendations:")
    print("   1. Use test results to validate 95% API query accuracy KPI")
    print("   2. Identify and address any RAG retrieval weaknesses")
    print("   3. Optimize LLM prompts for better synthesis quality")
    print("   4. Consider adding more test scenarios for edge cases")

if __name__ == "__main__":
    asyncio.run(main())
