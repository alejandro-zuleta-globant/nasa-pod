import io
from typing import List, Dict, Set

from aiohttp import ClientSession
import asyncio
from PIL import Image

from image import NasaImage


async def get_metadata(api_url: str) -> List[Dict]:
    async with ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                return await response.json()
            return []


async def process_metadata(data: List[Dict]):
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
    async with session.get(image.url) as response:
        if response.status == 200:
            image.bytes = io.BytesIO(await response.read())


def process_image(image: NasaImage):
    if image.media_type != "image":
        print(f"Invalid media type for {image}")
        return

    if not image.bytes:
        print(f"Corrupted bytes for image: {image}")

    print(f"Processing image: {image}")
    img = Image.open(image.bytes)
    return get_color_count(set(img.getdata()))


def get_color_count(unique_pixels: Set):
    return len(unique_pixels)


async def main(api_url: str, start_date: str, end_date: str):
    url = f"{api_url}&start_date={start_date}&end_date={end_date}"
    data = await get_metadata(url)

    if not data:
        print("An error ocurred retrieving the pictures metadata.")
        return

    images = await process_metadata(data)
    await get_content(images)
    for image in images:
        print(process_image(image))
