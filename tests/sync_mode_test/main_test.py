from sync_mode.main import get_metadata

def test_get_metadata_ok(mocker):
    # Arrange
    expected_url = "http://test.com/test"

    expected_data = {
        "ABC": 1,
        "DEF": 2,
    }

    get_mock = mocker.patch("requests.get")
    get_mock.return_value.status_code = 200
    get_mock.return_value.json.return_value = expected_data

    result = get_metadata(expected_url)

    get_mock.assert_called_with(expected_url)
    assert result == expected_data

def test_get_metadata_error(mocker):
    # Arrange
    expected_url = "http://test.com/test"

    expected_data = {}

    get_mock = mocker.patch("requests.get")
    get_mock.return_value.status_code = 400
    get_mock.return_value.json.return_value = expected_data

    result = get_metadata(expected_url)

    get_mock.assert_called_with(expected_url)
    assert result == expected_data
