import asyncio
from src.agents.base_agent import BaseAgent
from src.core.mcp_protocol import MCPMessage
from src.core.db_manager import db_manager


class ValidatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="validator_agent",
            input_channel="validator_input",
            output_channel=None
        )
    
    async def handle_message(self, message: MCPMessage):
        """Handle incoming validation requests."""
        summary = message.payload.get("summary", "")
        query = message.payload.get("query", "")
        
        self.logger.info(f"Validating summary", context_id=message.context_id)
        
        is_valid, validation_report = await self.run(
            message.context_id,
            summary=summary,
            query=query
        )
        
        db_manager.save_result(
            context_id=message.context_id,
            agent_name=self.name,
            result_type="validation",
            result_data=validation_report,
            validated=is_valid
        )
        
        status = "completed"
        success = is_valid
        error = None if is_valid else "Validation failed"
        
        db_manager.update_task_status(
            context_id=message.context_id,
            status=status,
            success=success,
            error=error
        )
    
    async def run(self, context_id: str, summary: str = "", query: str = "", **kwargs) -> tuple[bool, str]:
        """Validate summary quality."""
        self.logger.info(f"Running validation checks", context_id=context_id)
        
        await asyncio.sleep(0.2)
        
        checks = []
        is_valid = True
        
        if len(summary) < 10:
            checks.append("❌ Summary too short")
            is_valid = False
        else:
            checks.append("✓ Summary length acceptable")
        
        if len(summary) > 500:
            checks.append("❌ Summary too long")
            is_valid = False
        else:
            checks.append("✓ Summary length within limits")
        
        if query and query.lower() not in summary.lower():
            checks.append("⚠ Query term not found in summary")
        else:
            checks.append("✓ Query relevance confirmed")
        
        word_count = len(summary.split())
        if word_count < 5:
            checks.append("❌ Insufficient content")
            is_valid = False
        else:
            checks.append(f"✓ Word count: {word_count}")
        
        validation_report = "\n".join(checks)
        
        db_manager.log_agent_action(
            context_id=context_id,
            agent_name=self.name,
            action="validation_completed",
            details=f"Valid: {is_valid}\n{validation_report}"
        )
        
        self.logger.info(f"Validation result: {is_valid}", context_id=context_id)
        return is_valid, validation_report
