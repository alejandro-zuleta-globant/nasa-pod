import io
from threading import Thread
from typing import List, Dict, Set

from PIL import Image
import requests

from image import NasaImage


class MetadataThread(Thread):
    # constructor
    def __init__(self, url: str):
        # execute the base constructor
        Thread.__init__(self)
        # set a default value
        self.value: List[Dict] = []
        self.url = url

    # function executed in a new thread
    def run(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            self.value = response.json()


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


def get_image_binary(image: NasaImage):
    response = requests.get(image.url)
    if response.status_code == 200:
        image.bytes = io.BytesIO(response.content)
        return
    print(f"Cannot get the content for image: {image}")


def get_content(images: List[NasaImage]):
    threads = []
    for image in images:
        t = Thread(target=get_image_binary, args=(image,))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()


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


def main(api_url: str, start_date: str, end_date: str):
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
