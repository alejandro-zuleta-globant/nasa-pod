import io
from multiprocessing import Pool, cpu_count
from typing import List, Dict, Set

from PIL import Image
import requests

from image import NasaImage


def get_metadata(url: str) -> List[Dict]:
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []


def process_metadata(data: List[Dict]) -> List[NasaImage]:
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
        return image
    print(f"Cannot get the content for image: {image}")


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
