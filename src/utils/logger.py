import logging
import sys
from datetime import datetime
from typing import Optional


class AgentLogger:
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str, context_id: Optional[str] = None):
        msg = f"[{context_id}] {message}" if context_id else message
        self.logger.info(msg)
    
    def error(self, message: str, context_id: Optional[str] = None, exc_info: bool = False):
        msg = f"[{context_id}] {message}" if context_id else message
        self.logger.error(msg, exc_info=exc_info)
    
    def warning(self, message: str, context_id: Optional[str] = None):
        msg = f"[{context_id}] {message}" if context_id else message
        self.logger.warning(msg)
    
    def debug(self, message: str, context_id: Optional[str] = None):
        msg = f"[{context_id}] {message}" if context_id else message
        self.logger.debug(msg)


def get_logger(name: str, level: str = "INFO") -> AgentLogger:
    return AgentLogger(name, level)
