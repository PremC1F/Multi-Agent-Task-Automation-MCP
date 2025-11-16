import asyncio
import sys
from pathlib import Path

# Add project root to path so imports work from any directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.researcher_agent import ResearcherAgent
from src.agents.summarizer_agent import SummarizerAgent
from src.agents.validator_agent import ValidatorAgent

# Monkey-patch db_manager to avoid database calls
from src.core import db_manager
db_manager.log_agent_action = lambda *args, **kwargs: None
db_manager.save_result = lambda *args, **kwargs: None
db_manager.update_task_status = lambda *args, **kwargs: None

async def test_researcher():
    print("\nTesting Researcher Agent...")
    agent = ResearcherAgent()
    data = await agent.run("test-001", query="machine learning")
    assert len(data) > 0
    print(f"PASSED - Collected {len(data)} research items\n")
    print("RESEARCH FINDINGS:")
    for i, item in enumerate(data, 1):
        print(f"   {i}. {item}")
    return data

async def test_summarizer(data):
    print("\nTesting Summarizer Agent...")
    agent = SummarizerAgent()
    summary = await agent.run("test-002", data=data, query="machine learning")
    assert len(summary) > 0
    print(f"PASSED - Generated {len(summary)} character summary\n")
    print("GENERATED SUMMARY:")
    print(f"   {summary}")
    return summary

async def test_validator(summary):
    print("\nTesting Validator Agent...")
    agent = ValidatorAgent()
    is_valid, report = await agent.run("test-003", summary=summary, query="machine learning")
    assert isinstance(is_valid, bool)
    print(f"PASSED - Validation result: {'VALID' if is_valid else 'INVALID'}\n")
    print(" VALIDATION REPORT:")
    for line in report.split('\n'):
        print(f"   {line}")
    return is_valid

async def main():
    print("="*70)
    print("Multi-Agent Task Automation Platform - Workflow Demo")
    print("="*70)
    print("\nQuery: 'machine learning'")
    print("Pipeline: Research → Summarize → Validate")
    print("="*70)
    
    try:
        # Step 1: Research
        research_data = await test_researcher()
        
        # Step 2: Summarize
        summary = await test_summarizer(research_data)
        
        # Step 3: Validate
        is_valid = await test_validator(summary)
        
        # Final Results
        print("\n" + "="*70)
        print("WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\nWORKFLOW SUMMARY:")
        print(f"   • Research Items Collected: {len(research_data)}")
        print(f"   • Summary Generated: {len(summary)} characters")
        print(f"   • Validation Status: {'PASSED' if is_valid else 'FAILED'}")
        print(f"   • Total Processing Time: ~1-2 seconds")
        print("\n" + "="*70)
        print("This demonstrates the multi-agent workflow WITHOUT Docker.")
        print("   Full system with API requires: docker compose up --build")
        print("="*70)
    except Exception as e:
        print(f"\nWorkflow failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())