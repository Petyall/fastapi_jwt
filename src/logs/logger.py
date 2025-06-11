import logging

from pathlib import Path


Path("src/logs").mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("project_logger")
logger.setLevel(logging.ERROR)

formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")

file_handler = logging.FileHandler("src/logs/errors.log", encoding="UTF-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
