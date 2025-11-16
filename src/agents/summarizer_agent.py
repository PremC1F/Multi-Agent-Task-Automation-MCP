import asyncio
from typing import List
from src.agents.base_agent import BaseAgent
from src.core.mcp_protocol import MCPMessage
from src.core.db_manager import db_manager


class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="summarizer_agent",
            input_channel="summarizer_input",
            output_channel="validator_input"
        )
        self.summarizer = None
    
    def _initialize_model(self):
        """Lazy load summarization model."""
        if self.summarizer is None:
            try:
                from transformers import pipeline
                self.logger.info("Loading summarization model...")
                self.summarizer = pipeline(
                    "summarization",
                    model="sshleifer/distilbart-cnn-12-6",
                    device=-1
                )
                self.logger.info("Summarization model loaded")
            except Exception as e:
                self.logger.error(f"Failed to load model: {e}")
                self.summarizer = None
    
    async def handle_message(self, message: MCPMessage):
        """Handle incoming summarization requests."""
        data = message.payload.get("data", [])
        query = message.payload.get("query", "")
        
        self.logger.info(f"Summarizing {len(data)} items", context_id=message.context_id)
        
        summary = await self.run(message.context_id, data=data, query=query)
        
        await self.send_message(
            context_id=message.context_id,
            receiver="validator_agent",
            payload={"summary": summary, "query": query}
        )
    
    async def run(self, context_id: str, data: List[str] = None, query: str = "", **kwargs) -> str:
        """Summarize collected data."""
        if not data:
            return ""
        
        self.logger.info(f"Processing {len(data)} documents", context_id=context_id)
        
        combined_text = " ".join(data)
        
        if len(combined_text) > 1000:
            self._initialize_model()
            
            if self.summarizer:
                try:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,
                        lambda: self.summarizer(
                            combined_text[:1024],
                            max_length=150,
                            min_length=50,
                            do_sample=False
                        )
                    )
                    summary = result[0]['summary_text']
                except Exception as e:
                    self.logger.warning(f"Model summarization failed, using fallback: {e}")
                    summary = self._fallback_summarize(combined_text)
            else:
                summary = self._fallback_summarize(combined_text)
        else:
            summary = self._fallback_summarize(combined_text)
        
        db_manager.save_result(
            context_id=context_id,
            agent_name=self.name,
            result_type="summary",
            result_data=summary
        )
        
        self.logger.info(f"Summary generated ({len(summary)} chars)", context_id=context_id)
        return summary
    
    def _fallback_summarize(self, text: str) -> str:
        """Simple fallback summarization."""
        sentences = text.split('.')
        return '. '.join(sentences[:3]) + '.'
