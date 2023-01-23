from datetime import datetime, timedelta
from timeit import default_timer
import os

import asyncio
import click

from sync_mode.main import main as main_sync
from async_mode.main import main as main_async
from thread_mode.main import main as main_thread
from multiprocessing_mode.main import main as main_processing


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
@click.option(
    "--end_date",
    "-e",
    "end_date",
    default=datetime.strftime(datetime.now(), "%Y-%m-%d"),
)
def command(mode: str, start_date, end_date):
    api_url = get_api_url()

    if not api_url:
        print("Invalid API URL.")
        return

    print(
        f"Calculating the number of colors for Nasa's picture of the date from {start_date}"
        f" to {end_date}"
    )

    start_time = default_timer()
    match mode:
        case "sync":
            main_sync(api_url=api_url, start_date=start_date, end_date=end_date)
        case "async":
            asyncio.run(
                main_async(api_url=api_url, start_date=start_date, end_date=end_date)
            )
        case "threading":
            main_thread(api_url=api_url, start_date=start_date, end_date=end_date)
        case "multiprocessing":
            main_processing(api_url=api_url, start_date=start_date, end_date=end_date)
        case _:
            print(f"{mode} is not a valid argument.")
    elapsed = default_timer() - start_time
    print(f"{mode} mode took: {elapsed:.2f} seconds")


if __name__ == "__main__":
    command()
