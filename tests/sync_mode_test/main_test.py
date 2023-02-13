import io

from sync_mode.main import (
    get_metadata,
    process_metadata,
    get_content,
    get_images,
    get_color_count,
    process_images,
    process_image,
    main,
)


def test_get_metadata_ok(ok_get_request, valid_response):
    # Arrange
    expected_url = "http://test.com/test"

    result = get_metadata(expected_url)

    ok_get_request.assert_called_with(expected_url)
    assert result == valid_response


def test_get_metadata_error(error_get_request, invalid_response):
    # Arrange
    expected_url = "http://test.com/test"

    result = get_metadata(expected_url)

    error_get_request.assert_called_with(expected_url)
    assert result == invalid_response


def test_process_metadata(valid_response, images_data):
    result = process_metadata(valid_response)
    assert result == images_data


def test_get_content_ok(images_data, ok_image_content_request, binary_response):
    image = images_data[0]
    get_content(image)
    ok_image_content_request.assert_called_with(image.url)
    assert image.bytes.getvalue() == io.BytesIO(binary_response).getvalue()


def test_get_content_error(images_data, error_image_content_request, capfd):
    image = images_data[0]
    get_content(image)
    error_image_content_request.assert_called_with(image.url)
    out, _ = capfd.readouterr()
    # Assert the second calling to print checking the value written to stdout
    assert out.split("\n")[1] == f"Cannot get the content for image: {image}"


def test_get_images(images_data, mocker):
    get_content_mock = mocker.patch("sync_mode.main.get_content")
    calls = [mocker.call(image) for image in images_data]

    get_images(images_data)
    assert get_content_mock.call_count == len(images_data)
    get_content_mock.assert_has_calls(calls)


def test_get_color_count(mocker):
    colors = {(255, 255, 255), (0, 0, 0)}
    expected = 2
    len_mock = mocker.patch("sync_mode.main.len", return_value=expected)
    result = get_color_count(colors)
    len_mock.assert_called_once_with(colors)
    assert expected == result


def test_process_images(mocker, images_data, capfd):
    num_of_colors = 6
    process_image_mock = mocker.patch("sync_mode.main.process_image", return_value=num_of_colors)
    calls = [mocker.call(image) for image in images_data]

    process_images(images_data)

    process_image_mock.assert_has_calls(calls)
    out, _ = capfd.readouterr()
    assert all([bool(str(num_of_colors) == line) for line in out.strip().split("\n")])


def test_process_image_invalid_media_type(images_data, capfd):
    image = images_data[2]
    expected_message = f"Invalid media type for {image}\n"

    process_image(image)

    out, _ = capfd.readouterr()
    assert expected_message == out


def test_process_image_valid_media_type(mocker, images_data, capfd, binary_response):
    image = images_data[0]
    image.bytes = io.BytesIO(binary_response)
    expected_message = f"Processing image: {image}\n"

    img_mock = mocker.Mock()
    expected_img_data = ((255, 255, 255), (0, 0, 0))
    img_mock.getdata.return_value = expected_img_data
    color_count = len(expected_img_data)

    image_open_mock = mocker.patch("PIL.Image.open", return_value=img_mock)
    color_counter_mock = mocker.patch(
        "sync_mode.main.get_color_count",
        return_value=color_count
    )

    result = process_image(image)

    out, _ = capfd.readouterr()
    assert expected_message == out
    assert result == color_count
    image_open_mock.assert_called_once_with(image.bytes)
    color_counter_mock.assert_called_once_with(set(expected_img_data))


def test_main_no_data(mocker, capfd):
    expected_url = "http://test.com/&start_date=2022-02-10&end_date=2022-02-13"
    get_data_mock = mocker.patch("sync_mode.main.get_metadata", return_value=None)
    expected_message = "An error ocurred retrieving the pictures metadata.\n"
    
    main(api_url=expected_url, start_date="2022-02-10", end_date="2022-02-13")
    get_data_mock.called_once_with(expected_url)
    out, _ = capfd.readouterr()
    assert out == expected_message


def test_main(mocker, images_data, valid_response):
    expected_url = "http://test.com/&start_date=2022-02-10&end_date=2022-02-13"
    get_data_mock = mocker.patch(
        "sync_mode.main.get_metadata",
        return_value=valid_response
    )

    process_metadata_mock = mocker.patch(
        "sync_mode.main.process_metadata",
        return_value=images_data
    )

    get_images_mock = mocker.patch(
        "sync_mode.main.get_images"
    )

    process_images_mock = mocker.patch(
        "sync_mode.main.process_images"
    )
    
    main(api_url=expected_url, start_date="2022-02-10", end_date="2022-02-13")
    get_data_mock.called_once_with(expected_url)
    process_metadata_mock.called_once_with(valid_response)
    get_images_mock.called_once_with(images_data)
    process_images_mock.called_once_with(images_data)
