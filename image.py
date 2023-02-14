"""Holds the class for Nasa image manipulation."""

import io


class NasaImage:
    """Class for manipulation NASA's APOD."""

    def __init__(self, url: str, media_type: str, title: str, date: str) -> None:
        """Initialize method for NASA's APOD object.

        Args:
            url (str): URL of the resource
            media_type (str): Expected media type.
            title (str): Title of the picture.
            date (str): Date of the picture.
        """
        self.url = url
        self.media_type = media_type
        self.title = title
        self.date = date
        self.bytes: io.BytesIO | None = None

    def __repr__(self) -> str:
        """Build the string representation for NASA's APOD object.

        Returns:
            String representation.
        """
        return f"{self.title} - {self.url}"

    def __eq__(self, other: object) -> bool:
        """Check equity of NASA's APOD objects.

        Args:
            other (NasaImage): The image to compare against.

        Returns:
            True if both objects are equal otherwise False.
        """
        if not isinstance(other, NasaImage):
            return NotImplemented

        return (
            self.url == other.url
            and self.media_type == other.media_type
            and self.title == other.title
            and self.date == other.date
        )
