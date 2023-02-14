"""Includes the functions for get and process Nasa images in sync mode."""

import asyncio
import io
from typing import Dict, List, Set

from aiohttp import ClientSession
from PIL import Image

from image import NasaImage


async def get_metadata(api_url: str) -> List[Dict]:
    """Get the metadata from the given URL.

    Args:
        api_url (str): NASA's api URL

    Returns
    -------
        List[Dict]: List of decoded data containing images metadata.
    """
    async with ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                return await response.json()
            return []


async def process_metadata(data: List[Dict]) -> List[NasaImage] :
    """Process the metadata and build an object from it.

    Args:
        data (List[Dict]): List of images data.

    Returns:
        Returns a list of NASA images objects.
    """
    return [
        NasaImage(
            url=p.get("url"),
            media_type=p.get("media_type"),
            title=p.get("title"),
            date=p.get("date"),
        )
        for p in data
    ]


async def get_content(images: List[NasaImage]):
    """Get the binary content of a set of images using their URL.

    Args:
        images (List[NasaImage]): List of NASA images objects.
    """
    tasks = []
    async with ClientSession() as session:
        for image in images:
            if image.media_type != "image":
                print(f"Invalid media type for {image}")
                continue
            task = asyncio.ensure_future(get_image_bytes(image, session))
            tasks.append(task)
        await asyncio.gather(*tasks)


async def get_image_bytes(image: NasaImage, session: ClientSession):
    """Get the binary content of an image using its URL.

    The binary content is loaded using an in-memory buffer and set to
    the image bytes attribute.

    Args:
    ----
        image (NasaImage): An image.
        session (ClientSession): An iohttp client session object.
    """
    async with session.get(image.url) as response:
        if response.status == 200:
            image.bytes = io.BytesIO(await response.read())


def process_image(image: NasaImage) -> int | None:
    """Process a given image.

    Args:
        image (NasaImage): An image object.

    Returns:
        The number of unique colors of the image.
    """
    if image.media_type != "image":
        print(f"Invalid media type for {image}")
        return # type: ignore

    if not image.bytes:
        print(f"Corrupted bytes for image: {image}")

    print(f"Processing image: {image}")
    img = Image.open(image.bytes)
    return get_color_count(set(img.getdata()))


def get_color_count(unique_pixels: Set):
    """Get the total number of colors.

    Args:
        unique_pixels (Set): A set of pixels

    Returns
    -------
        The number of colors.
    """
    return len(unique_pixels)


async def main(api_url: str, start_date: str, end_date: str):
    """Process the images in the given date range.

    Args:
    ----
        api_url (str): URL of the NASA's image metadata endpoint.
        start_date (str): Start date in format "YYYY-MM-DD"
        end_date (str): End date in format "YYYY-MM-DD"
    """
    url = f"{api_url}&start_date={start_date}&end_date={end_date}"
    data = await get_metadata(url)

    if not data:
        print("An error ocurred retrieving the pictures metadata.")
        return

    images = await process_metadata(data)
    await get_content(images)
    for image in images:
        print(process_image(image))
