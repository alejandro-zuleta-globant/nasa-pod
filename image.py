import io


class NasaImage:
    def __init__(self, url: str, media_type: str, title: str, date: str) -> None:
        self.url = url
        self.media_type = media_type
        self.title = title
        self.date = date
        self.bytes: io.BytesIO | None = None

    def __repr__(self) -> str:
        return f"{self.title} - {self.url}"
