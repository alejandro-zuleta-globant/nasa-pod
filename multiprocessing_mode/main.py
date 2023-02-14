"""Implementation for processing NASA APOD in multiprocessing mode."""

import io
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Set

import requests
from PIL import Image

from image import NasaImage


def get_metadata(url: str) -> List[Dict]:
    """Get the metadata from the given URL.

    Args:
        url (str): URL of the metadata endpoint.

    Returns:
        List[Dict]: List of decoded data containing images metadata.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []


def process_metadata(data: List[Dict]) -> List[NasaImage]:
    """Process the metadata and build an object from it.

    Args:
        data (List[Dict]): List of images data.

    Returns:
        List[NasaImage]: Returns a list of NASA images objects.
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


def get_image_binary(image: NasaImage) -> NasaImage:
    """Get the binary content of an image using its URL.

    The binary content is loaded using an in-memory buffer and set to
    the image bytes attribute.

    Args:
        image (NasaImage): An image.

    Returns:
        The image with binary content set as an attribute.
    """
    response = requests.get(image.url)
    if response.status_code == 200:
        image.bytes = io.BytesIO(response.content)
    print(f"Cannot get the content for image: {image}")
    return image


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

    print(f"Processing image: {image}")
    img = Image.open(image.bytes)
    return get_color_count(set(img.getdata()))


def get_color_count(unique_pixels: Set) -> int:
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


def main(api_url: str, start_date: str, end_date: str):
    """Run the process for processing images in date range.

    Args:
        api_url (str): URL of the image metadata API endpoint.
        start_date (str): Start date of the date range.
        end_date (str): End date of the date range.
    """
    n_cores = (cpu_count() - 1) | 1
    print(f"Number of cores: {n_cores}")

    url = f"{api_url}&start_date={start_date}&end_date={end_date}"

    with Pool(n_cores) as pool:
        result = pool.apply_async(get_metadata, (url,))
        data = result.get(timeout=10)

        if not data:
            print("An error ocurred retrieving the pictures metadata.")
            return

        images = process_metadata(data)
        results = pool.map_async(get_image_binary, images)
        imgs = [image for image in results.get()]
        process_images(imgs)
