import pytest

from image import NasaImage

@pytest.fixture()
def valid_response():
    return [
        {
            "url": "http://nasa.gov/image.jpg",
            "media_type": "image",
            "title": "An image title",
            "date": "2022-02-10",
        },
        {
            "url": "http://nasa.gov/image2.jpg",
            "media_type": "image",
            "title": "An image 2 title",
            "date": "2022-02-11",
        },
        {
            "url": "http://nasa.gov/video.mp4",
            "media_type": "video",
            "title": "A video title",
            "date": "2022-02-13",
        }
    ]

@pytest.fixture()
def invalid_response():
    return []

@pytest.fixture()
def binary_response():
    return b"\x00\x0F"

@pytest.fixture(autouse=True)
def mocked_get_request(mocker):
    yield mocker.patch("requests.get")

@pytest.fixture()
def ok_get_request(mocked_get_request, valid_response):
    mocked_get_request.return_value.status_code = 200
    mocked_get_request.return_value.json.return_value = valid_response
    yield mocked_get_request

@pytest.fixture()
def error_get_request(mocked_get_request, invalid_response):
    mocked_get_request.return_value.status_code = 400
    mocked_get_request.return_value.json.return_value = invalid_response
    yield mocked_get_request

@pytest.fixture()
def ok_image_content_request(mocked_get_request, binary_response):
    mocked_get_request.return_value.status_code = 200
    mocked_get_request.return_value.content = binary_response
    yield mocked_get_request

@pytest.fixture()
def error_image_content_request(mocked_get_request):
    mocked_get_request.return_value.status_code = 400
    yield mocked_get_request

@pytest.fixture()
def images_data(valid_response):
    return [
        NasaImage(
            url=p.get("url"),
            media_type=p.get("media_type"),
            title=p.get("title"),
            date=p.get("date"),
        )
        for p in valid_response
    ]