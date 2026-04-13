import logging
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

class TheryBotLogger:
    _initialized = False

    def __init__(self, log_dir: Path = Path("logs")):
        self.log_dir = log_dir
        if not TheryBotLogger._initialized:
            self._setup_logging()
            TheryBotLogger._initialized = True

    def _setup_logging(self) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Only add handlers if the root logger has none yet
        root = logging.getLogger()
        if root.handlers:
            return

        file_handler = logging.FileHandler(
            self.log_dir / f"thery_bot_{datetime.now():%Y%m%d}.log"
        )
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

        root.setLevel(logging.INFO)
        root.addHandler(file_handler)
        root.addHandler(console_handler)

    def log_interaction(
        self,
        interaction_type: str,
        data: Dict[str, Any],
        level: int = logging.INFO,
    ) -> None:
        """Log an interaction with structured data."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "data": data,
        }
        logging.log(level, json.dumps(log_entry))