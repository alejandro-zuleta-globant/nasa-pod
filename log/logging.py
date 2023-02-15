"""Includes the functions and objects for setting up a logger"""

import logging


def setup_logger():
    """Set up the logging facility."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
