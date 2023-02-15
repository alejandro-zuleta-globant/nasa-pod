from datetime import datetime, timedelta
from timeit import default_timer
import os
import logging

import asyncio
import click

from sync_mode.main import main as main_sync
from async_mode.main import main as main_async
from thread_mode.main import main as main_thread
from multiprocessing_mode.main import main as main_processing
from log.logging import setup_logger

logger = logging.getLogger(__name__)


def get_api_url() -> str | None:
    return os.environ.get("API_URL")


@click.command()
@click.argument("mode", default="sync")
@click.option(
    "--start_date",
    "-s",
    "start_date",
    default=datetime.strftime(datetime.now() - timedelta(days=10), "%Y-%m-%d"),
)
@click.option("--end_date", "-e", "end_date", default=datetime.strftime(datetime.now(), "%Y-%m-%d"))
def command(mode: str, start_date: str, end_date: str):
    """Executes a command for processing NASA's APOD.

    Args:
        mode (str): Execution mode used for process the pictures.
        start_date:: Start date
        end_date: End date
    """
    setup_logger()
    api_url = get_api_url()

    if not api_url:
        logger.error("Invalid API URL.")
        return

    logger.info(
        f"Calculating the number of colors for Nasa's picture of the date from {start_date}"
        f" to {end_date}"
    )

    start_time = default_timer()
    match mode:  # noqa: E999
        case "sync":
            main_sync(api_url=api_url, start_date=start_date, end_date=end_date)
        case "async":
            asyncio.run(main_async(api_url=api_url, start_date=start_date, end_date=end_date))
        case "threading":
            main_thread(api_url=api_url, start_date=start_date, end_date=end_date)
        case "multiprocessing":
            main_processing(api_url=api_url, start_date=start_date, end_date=end_date)
        case _:
            logger.warning(f"{mode} is not a valid argument.")
    elapsed = default_timer() - start_time
    logger.info(f"{mode} mode took: {elapsed:.2f} seconds")


if __name__ == "__main__":
    command()
