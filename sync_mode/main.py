import io
from typing import List, Set, Dict

import requests
from PIL import Image

from image import NasaImage


def get_metadata(api_url: str):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return []


def process_metadata(data: List[Dict]):
    return [
        NasaImage(
            url=p.get("url"),
            media_type=p.get("media_type"),
            title=p.get("title"),
            date=p.get("date"),
        )
        for p in data
    ]


def get_content(image: NasaImage):
    print(f"Getting data for: {image}")
    response = requests.get(image.url)
    if response.status_code == 200:
        image.bytes = io.BytesIO(response.content)
        return
    print(f"Cannot get the content for image: {image}")


def get_images(images: List[NasaImage]):
    for image in images:
        get_content(image)


def process_image(image: NasaImage):
    if image.media_type != "image":
        print(f"Invalid media type for {image}")
        return

    print(f"Processing image: {image}")
    img = Image.open(image.bytes)
    return get_color_count(set(img.getdata()))


def get_color_count(unique_pixels: Set):
    return len(unique_pixels)


def process_images(images: List[NasaImage]):
    for image in images:
        print(process_image(image))


def main(api_url: str, start_date, end_date):
    url = f"{api_url}&start_date={start_date}&end_date={end_date}"
    data = get_metadata(url)
    if not data:
        print("An error ocurred retrieving the pictures metadata.")
        return

    images = process_metadata(data)
    get_images(images)
    process_images(images)
