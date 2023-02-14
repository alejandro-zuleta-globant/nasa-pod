"""Includes reusable fixtures for unit tests."""

from typing import Dict, Generator, List, Literal
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from image import NasaImage


@pytest.fixture()
def valid_response() -> List[Dict[str, str]]:
    """Build a fake metadata API response.

    Returns:
        A list of the metadata for each NASA's picture.
    """
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
        },
    ]


@pytest.fixture()
def invalid_response() -> List:
    """Build an invalid metadata API response.

    Returns:
        List: An empty list.
    """
    return []


@pytest.fixture()
def binary_response() -> Literal[b"\x00\x0f"]:
    """Build a binary content for an image.

    Returns:
        Binary content.
    """
    return b"\x00\x0F"


@pytest.fixture(autouse=True)
def mocked_get_request(mocker: MockerFixture) -> Generator[MagicMock, None, None]:
    """Create a mock object for HTTP get requests using `requests` package.

    Args:
        mocker: Mocking fixture.

    Yields:
        A mock of requests.get function.
    """
    yield mocker.patch("requests.get")


@pytest.fixture()
def ok_get_request(
    mocked_get_request: MagicMock, valid_response: List[Dict[str, str]]
) -> Generator[MagicMock, None, None]:
    """Build a mock object with a valid response and valid HTTP status code.

    Args:
        mocked_get_request: A mock of requests.get function.
        valid_response: A list of the metadata for each NASA's picture.

    Yields:
        A mock of requests.get function.
    """
    mocked_get_request.return_value.status_code = 200
    mocked_get_request.return_value.json.return_value = valid_response
    yield mocked_get_request


@pytest.fixture()
def error_get_request(
    mocked_get_request: MagicMock, invalid_response: List
) -> Generator[MagicMock, None, None]:
    """Build a mock object with an invalid response and invalid HTTP status code.

    Args:
        mocked_get_request: A mock of requests.get function.
        invalid_response: An empty list.

    Yields:
        A mock of requests.get function.
    """
    mocked_get_request.return_value.status_code = 400
    mocked_get_request.return_value.json.return_value = invalid_response
    yield mocked_get_request


@pytest.fixture()
def ok_image_content_request(
    mocked_get_request: MagicMock, binary_response: Literal[b"\x00\x0f"]
) -> Generator[MagicMock, None, None]:
    """Build a mock object of a response with the binary content of an image.

    Args:
        mocked_get_request (MagicMock): A mock of requests.get function.
        binary_response: A binary literal.

    Yields:
        A mock of requests.get function.
    """
    mocked_get_request.return_value.status_code = 200
    mocked_get_request.return_value.content = binary_response
    yield mocked_get_request


@pytest.fixture()
def error_image_content_request(mocked_get_request: MagicMock) -> Generator[MagicMock, None, None]:
    """Build a mock object of a invalid binary content response.

    Args:
        mocked_get_request: A mock of requests.get function.

    Yields:
        A mock of requests.get function.
    """
    mocked_get_request.return_value.status_code = 400
    yield mocked_get_request


@pytest.fixture()
def images_data(valid_response: List[Dict[str, str]]) -> List[NasaImage]:
    """_summary_

    Args:
        valid_response: A list images metadata.

    Returns:
        List[NasaImage]: List of NASA's image objects
    """
    return [
        NasaImage(url=p["url"], media_type=p["media_type"], title=p["title"], date=p["date"])
        for p in valid_response
    ]
