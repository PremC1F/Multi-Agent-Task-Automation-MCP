from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict
import json
import uuid


class MCPMessage(BaseModel):
    context_id: str
    sender: str
    receiver: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


def encode_message(message: MCPMessage) -> str:
    """Serialize MCP message to JSON string."""
    return message.model_dump_json()


def decode_message(raw: str) -> MCPMessage:
    """Deserialize JSON string to MCP message."""
    data = json.loads(raw)
    if isinstance(data.get('timestamp'), str):
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
    return MCPMessage(**data)


def create_message(
    context_id: str,
    sender: str,
    receiver: str,
    payload: Dict[str, Any]
) -> MCPMessage:
    """Helper to create a new MCP message."""
    return MCPMessage(
        context_id=context_id,
        sender=sender,
        receiver=receiver,
        payload=payload
    )
