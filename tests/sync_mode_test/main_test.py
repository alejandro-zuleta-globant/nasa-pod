"""Unit tests for the sync mode implementation"""

import io
from typing import Dict, List, Literal
from unittest.mock import MagicMock

from pytest import CaptureFixture
from pytest_mock import MockerFixture

from image import NasaImage
from sync_mode.main import (
    get_color_count,
    get_content,
    get_images,
    get_metadata,
    main,
    process_image,
    process_images,
    process_metadata,
)


def test_get_metadata_ok(ok_get_request: MagicMock, valid_response: List[Dict[str, str]]):
    """Test the metadata retrieval from the API.

    Args:
        ok_get_request (_type_): A mock of a get request.
        valid_response (_type_): A list of image metadata.
    """
    # Arrange
    expected_url = "http://test.com/test"

    result = get_metadata(expected_url)

    ok_get_request.assert_called_with(expected_url)
    assert result == valid_response


def test_get_metadata_error(error_get_request: MagicMock, invalid_response: List):
    """Test the metadata retrieval when the API does not responds successfully.

    Args:
        error_get_request (MagicMock): A mock of a get request.
        invalid_response (List): An empty list
    """
    # Arrange
    expected_url = "http://test.com/test"

    result = get_metadata(expected_url)

    error_get_request.assert_called_with(expected_url)
    assert result == invalid_response


def test_process_metadata(valid_response: List[Dict[str, str]], images_data: List[NasaImage]):
    """Test the processing of retrieved metadata.

    Args:
        valid_response (List[Dict[str, str]]): A list of images metadata.
        images_data (List[NasaImage]): A list of NASA image objects.
    """
    result = process_metadata(valid_response)
    assert result == images_data


def test_get_content_ok(
    images_data: List[NasaImage],
    ok_image_content_request: MagicMock,
    binary_response: Literal[b"\x00\x0f"],
):
    """_summary_

    Args:
        images_data: A list of NASA image objects.
        ok_image_content_request: A mock of a get request.
        binary_response: A binary literal.
    """
    image = images_data[0]
    get_content(image)
    ok_image_content_request.assert_called_with(image.url)
    assert image.bytes.getvalue() == io.BytesIO(binary_response).getvalue()  # type: ignore


def test_get_content_error(
    images_data: List[NasaImage], error_image_content_request: MagicMock, capfd: CaptureFixture[str]
):
    """Test the error handling when binary content retrieval for a NASA image fails.

    Args:
        images_data (List[NasaImage]): A list of NASA image objects.
        error_image_content_request (MagicMock): A mock of a get request.
        capfd (CaptureFixture[str]): Capture fixture for getting stdout string
    """
    image = images_data[0]
    get_content(image)
    error_image_content_request.assert_called_with(image.url)
    out, _ = capfd.readouterr()
    # Assert the second calling to print checking the value written to stdout
    assert out.split("\n")[1] == f"Cannot get the content for image: {image}"


def test_get_images(images_data: List[NasaImage], mocker: MockerFixture):
    """Test the get the image binary content for a list of NASA image objects.

    Args:
        images_data: A list of NASA image objects.
        mocker: Mocking fixture.
    """
    get_content_mock = mocker.patch("sync_mode.main.get_content")
    calls = [mocker.call(image) for image in images_data]

    get_images(images_data)
    assert get_content_mock.call_count == len(images_data)
    get_content_mock.assert_has_calls(calls)


def test_get_color_count(mocker: MockerFixture):
    """Test the counting of colors

    Args:
        mocker: Mocking fixture.
    """
    colors = {(255, 255, 255), (0, 0, 0)}
    expected = 2
    len_mock = mocker.patch("sync_mode.main.len", return_value=expected)
    result = get_color_count(colors)
    len_mock.assert_called_once_with(colors)
    assert expected == result


def test_process_images(
    mocker: MockerFixture, images_data: List[NasaImage], capfd: CaptureFixture[str]
):
    """_summary_

    Args:
        mocker (MockerFixture): Mocking fixture.
        images_data (List[NasaImage]): A list of NASA image objects.
        capfd (CaptureFixture[str]): Capture fixture for getting stdout string
    """
    num_of_colors = 6
    process_image_mock = mocker.patch("sync_mode.main.process_image", return_value=num_of_colors)
    calls = [mocker.call(image) for image in images_data]

    process_images(images_data)

    process_image_mock.assert_has_calls(calls)
    out, _ = capfd.readouterr()
    assert all([bool(str(num_of_colors) == line) for line in out.strip().split("\n")])


def test_process_image_invalid_media_type(images_data: List[NasaImage], capfd: CaptureFixture[str]):
    """Test the processing of a image with an invalid media type.

    Args:
        images_data (List[NasaImage]): A list of NASA image objects.
        capfd (CaptureFixture[str]): Capture fixture for getting stdout string
    """
    image = images_data[2]
    expected_message = f"Invalid media type for {image}\n"

    process_image(image)

    out, _ = capfd.readouterr()
    assert expected_message == out


def test_process_image_valid_media_type(
    mocker: MockerFixture,
    images_data: List[NasaImage],
    capfd: CaptureFixture[str],
    binary_response: Literal[b"\x00\x0f"],
):
    """Test the processing of a image with a valid media type.

    Args:
        mocker (MockerFixture): Mocking fixture.
        images_data (List[NasaImage]): A list of NASA image objects.
        capfd (CaptureFixture[str]): Capture fixture for getting stdout string
        binary_response: A binary literal.
    """
    image = images_data[0]
    image.bytes = io.BytesIO(binary_response)
    expected_message = f"Processing image: {image}\n"

    img_mock = mocker.Mock()
    expected_img_data = ((255, 255, 255), (0, 0, 0))
    img_mock.getdata.return_value = expected_img_data
    color_count = len(expected_img_data)

    image_open_mock = mocker.patch("PIL.Image.open", return_value=img_mock)
    color_counter_mock = mocker.patch("sync_mode.main.get_color_count", return_value=color_count)

    result = process_image(image)

    out, _ = capfd.readouterr()
    assert expected_message == out
    assert result == color_count
    image_open_mock.assert_called_once_with(image.bytes)
    color_counter_mock.assert_called_once_with(set(expected_img_data))


def test_main_no_data(mocker: MockerFixture, capfd: CaptureFixture[str]):
    """Test the main calling for processing the NASA's APOD when no data is retrieved.

    Args:
        mocker: Mocking fixture.
        capfd: Capture fixture for getting stdout string
    """
    expected_url = "http://test.com/&start_date=2022-02-10&end_date=2022-02-13"
    get_data_mock = mocker.patch("sync_mode.main.get_metadata", return_value=None)
    expected_message = "An error ocurred retrieving the pictures metadata.\n"

    main(api_url=expected_url, start_date="2022-02-10", end_date="2022-02-13")
    get_data_mock.called_once_with(expected_url)
    out, _ = capfd.readouterr()
    assert out == expected_message


def test_main(
    mocker: MockerFixture, images_data: List[NasaImage], valid_response: List[Dict[str, str]]
):
    """Test the main calling for processing the NASA's APOD when data is retrieved for a date range.

    Args:
        mocker (MockerFixture): Mocking fixture.
        images_data (List[NasaImage]): A list of NASA image objects.
        valid_response (List[Dict[str, str]]): A list of image metadata.
    """
    expected_url = "http://test.com/&start_date=2022-02-10&end_date=2022-02-13"
    get_data_mock = mocker.patch("sync_mode.main.get_metadata", return_value=valid_response)

    process_metadata_mock = mocker.patch(
        "sync_mode.main.process_metadata", return_value=images_data
    )

    get_images_mock = mocker.patch("sync_mode.main.get_images")

    process_images_mock = mocker.patch("sync_mode.main.process_images")

    main(api_url=expected_url, start_date="2022-02-10", end_date="2022-02-13")
    get_data_mock.called_once_with(expected_url)
    process_metadata_mock.called_once_with(valid_response)
    get_images_mock.called_once_with(images_data)
    process_images_mock.called_once_with(images_data)
