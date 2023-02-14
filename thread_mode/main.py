"""Includes the functions for getting and processing Nasa images in threading mode."""

import io
from threading import Thread
from typing import Dict, List, Set

import requests
from PIL import Image

from image import NasaImage


class MetadataThread(Thread):
    """Class for spawning a thread to retrieve images metadata."""

    def __init__(self, url: str):
        """Initialize the thread object with the required data.

        Args:
            url (str): URL of the metadata endpoint.
        """
        Thread.__init__(self)
        self.value: List[Dict] = []
        self.url = url

    def run(self):
        """Request the url of the metadata endpoint and sets the json response."""
        response = requests.get(self.url)
        if response.status_code == 200:
            self.value = response.json()


def process_metadata(data: List[Dict[str, str]]) -> List[NasaImage]:
    """Process the metadata and build an object from it.

    Args:
        data (List[Dict]): List of images data.

    Returns:
        List[NasaImage]: Returns a list of NASA images objects.
    """
    return [
        NasaImage(url=p["url"], media_type=p["media_type"], title=p["title"], date=p["date"])
        for p in data
    ]


def get_image_binary(image: NasaImage):
    """Get the binary content of a set of images using their URL.

    The binary content is loaded using an in-memory buffer and set to the image bytes attribute.

    Args:
        image (NasaImage): A NASA image object.
    """
    response = requests.get(image.url)
    if response.status_code == 200:
        image.bytes = io.BytesIO(response.content)
        return
    print(f"Cannot get the content for image: {image}")


def get_content(images: List[NasaImage]):
    """Span a set of threads for getting the binary contet of a list of images.

    Args:
        images (List[NasaImage]): A list of NASA images objects.
    """
    threads = []
    for image in images:
        t = Thread(target=get_image_binary, args=(image,))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()


def process_image(image: NasaImage) -> int | None:
    """Process a given image.

    This function takes an image, checks for the valid media type and count the unique colors.

    Args:
        image (NasaImage): An image object.

    Returns:
        The number of unique colors of the image.
    """
    if image.media_type != "image":
        print(f"Invalid media type for {image}")
        return  # type: ignore

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


def main(api_url: str, start_date: str, end_date: str):
    """Run the process for processing images in a date range.

    Args:
        api_url (str): URL of the image metadata API endpoint.
        start_date (str): Start date of the date range.
        end_date (str): End date of the date range.
    """
    url = f"{api_url}&start_date={start_date}&end_date={end_date}"
    t = MetadataThread(url=url)
    t.start()
    t.join()
    data = t.value

    if not data:
        print("An error ocurred retrieving the pictures metadata.")
        return

    images = process_metadata(data)
    get_content(images)
    process_images(images)
