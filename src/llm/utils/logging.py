import logging
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

class TherapyBotLogger:
    def __init__(self, log_dir: Path = Path("logs")):
        self.log_dir = log_dir
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup file handler
        file_handler = logging.FileHandler(
            self.log_dir / f"therapy_bot_{datetime.now():%Y%m%d}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Setup formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # Setup root logger
        logging.root.setLevel(logging.INFO)
        logging.root.addHandler(file_handler)
        logging.root.addHandler(console_handler)
    
    def log_interaction(
        self,
        interaction_type: str,
        data: Dict[str, Any],
        level: int = logging.INFO
    ) -> None:
        """Log an interaction with structured data"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "data": data
        }
        
        logging.log(level, json.dumps(log_entry))