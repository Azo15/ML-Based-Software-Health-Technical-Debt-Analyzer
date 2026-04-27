"""
Logging utility for ML-Based Software Health & Technical Debt Analyzer.
Provides a rich-based logger for beautiful terminal outputs.
"""
import logging
from rich.logging import RichHandler

def setup_logger(name: str = "debt_analyzer", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger with RichHandler for terminal formatting.
    
    Args:
        name (str): Name of the logger.
        level (int): Logging level.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, don't add more to avoid duplicate logs.
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)
    
    # Create RichHandler
    rich_handler = RichHandler(rich_tracebacks=True, markup=True)
    rich_handler.setLevel(level)
    
    # Create a simple formatter (Rich handles the heavy lifting)
    formatter = logging.Formatter("%(message)s", datefmt="[%X]")
    rich_handler.setFormatter(formatter)
    
    logger.addHandler(rich_handler)
    
    # Avoid propagating to the root logger
    logger.propagate = False
    
    return logger

# Default instance to be used across the project
logger = setup_logger()
