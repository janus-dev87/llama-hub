"""Remote file reader.

A loader that fetches an arbitrary remote page or file by URL and parses its contents.

"""
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from llama_index import download_loader
from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document


class RemoteReader(BaseReader):
    """General reader for any remote page or file."""

    def __init__(
        self,
        *args: Any,
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)

        self.file_extractor = file_extractor

    @staticmethod
    def _is_youtube_video(url: str) -> bool:
        # TODO create more global method for detecting all types
        """
        Returns True if the given URL is a video on YouTube, False otherwise.
        """
        # Regular expression pattern to match YouTube video URLs
        youtube_pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([^\s&]+)"

        # Match the pattern against the URL
        match = re.match(youtube_pattern, url)

        # If there's a match, it's a YouTube video URL
        if match:
            return True

        # Otherwise, it's not a YouTube video URL
        return False

    def load_data(self, url: str) -> List[Document]:
        """Parse whatever is at the URL."""
        import tempfile
        from urllib.parse import urlparse
        from urllib.request import urlopen

        extra_info = {"Source": url}

        result = urlopen(url)
        url_type = result.info().get_content_type()
        documents = []
        if url_type == "text/html" or url_type == "text/plain":
            text = "\n\n".join([str(el.decode("utf-8-sig")) for el in result])
            documents = [Document(text, extra_info=extra_info)]
        elif self._is_youtube_video(url):
            YoutubeTranscriptReader = download_loader("YoutubeTranscriptReader")
            youtube_reader = YoutubeTranscriptReader()
            # TODO should we have another langauge, like english / french?
            documents = youtube_reader.load_data([url])
        else:
            suffix = Path(urlparse(url).path).suffix
            with tempfile.TemporaryDirectory() as temp_dir:
                filepath = f"{temp_dir}/temp{suffix}"
                with open(filepath, "wb") as output:
                    output.write(result.read())

                SimpleDirectoryReader = download_loader("SimpleDirectoryReader")
                loader = SimpleDirectoryReader(
                    temp_dir,
                    file_metadata=(lambda _: extra_info),
                    file_extractor=self.file_extractor,
                )
                documents = loader.load_data()
        return documents
