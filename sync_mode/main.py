"""Includes the functions for get and process Nasa images in sync mode."""

import io
from typing import Dict, List, Set

import requests
from PIL import Image

from image import NasaImage


def get_metadata(api_url: str):
    """Get the metadata from the given URL.

    Args:
        url (str): URL of the metadata endpoint.

    Returns:
        List[Dict]: List of decoded data containing images metadata.
    """
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return []


def process_metadata(data: List[Dict]) -> List[NasaImage]:
    """Process the metadata and build a list of objects from it.

    Args:
        data (List[Dict]): List of images data.

    Returns:
        List[NasaImage]: Returns a list of NASA images objects.
    """
    return [
        NasaImage(url=p["url"], media_type=p["media_type"], title=p["title"], date=p["date"])
        for p in data
    ]


def get_content(image: NasaImage):
    """Get the binary content of an image using its URL.

    The binary content is loaded using an in-memory buffer and set to
    the image bytes attribute.

    Args:
        image (NasaImage): An image.
    """
    print(f"Getting data for: {image}")
    response = requests.get(image.url)
    if response.status_code == 200:
        image.bytes = io.BytesIO(response.content)
        return
    print(f"Cannot get the content for image: {image}")


def get_images(images: List[NasaImage]):
    """Get the binary content for a list of NASA images.

    Args:
        images (List[NasaImage]): List of NASA images.
    """
    for image in images:
        get_content(image)


def process_image(image: NasaImage):
    """Process a given image.

    Args:
        image (NasaImage): An image object.

    Returns:
        The number of unique colors of the image.
    """
    if image.media_type != "image":
        print(f"Invalid media type for {image}")
        return

    print(f"Processing image: {image}")
    img = Image.open(image.bytes)
    return get_color_count(set(img.getdata()))


def get_color_count(unique_pixels: Set):
    """Get the total number of colors.

    Args:
        unique_pixels (Set): A set of pixels

    Returns:
        The number of colors.
    """
    return len(unique_pixels)


def process_images(images: List[NasaImage]):
    """Process a set NASA's APOD images.

    Args:
        images (List[NasaImage]): List of NASA images objects.
    """
    for image in images:
        print(process_image(image))


def main(api_url: str, start_date, end_date):
    """Run the process for processing images in date range.

    Args:
        api_url (str): URL of the image metadata API endpoint.
        start_date (str): Start date of the date range.
        end_date (str): End date of the date range.
    """
    url = f"{api_url}&start_date={start_date}&end_date={end_date}"
    data = get_metadata(url)
    if not data:
        print("An error ocurred retrieving the pictures metadata.")
        return

    images = process_metadata(data)
    get_images(images)
    process_images(images)
