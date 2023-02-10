"""S3 file and directory reader.

A loader that fetches a file or iterates through a directory on AWS S3.

"""
import tempfile
from typing import Any, Dict, List, Optional, Union

from gpt_index import download_loader
from gpt_index.readers.base import BaseReader
from gpt_index.readers.schema.base import Document


class S3Reader(BaseReader):
    """General reader for any S3 file or directory."""

    def __init__(
        self,
        *args: Any,
        bucket: str,
        key: Optional[str] = None,
        prefix: Optional[str] = "",
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
        aws_access_id: Optional[str] = None,
        aws_access_secret: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize S3 bucket and key, along with credentials if needed.

        If key is not set, the entire bucket (filtered by prefix) is parsed.

        Args:
        bucket (str): the name of your S3 bucket
        key (Optional[str]): the name of the specific file. If none is provided,
            this loader will iterate through the entire bucket.
        prefix (Optional[str]): the prefix to filter by in the case that the loader
            iterates through the entire bucket. Defaults to empty string.
        file_extractor (Optional[Dict[str, BaseParser]]): A mapping of file
            extension to a BaseParser class that specifies how to convert that file
            to text. See `SimpleDirectoryReader` for more details.
        aws_access_id (Optional[str]): provide AWS access key directly.
        aws_access_secret (Optional[str]): provide AWS access key directly.
        """
        super().__init__(*args, **kwargs)

        self.bucket = bucket
        self.key = key
        self.prefix = prefix

        self.file_extractor = file_extractor

        self.aws_access_id = aws_access_id
        self.aws_access_secret = aws_access_secret

    def load_data(self) -> List[Document]:
        """Load file(s) from S3."""
        import boto3

        s3 = boto3.resource("s3")
        s3_client = boto3.client("s3")
        if self.aws_access_id:
            session = boto3.Session(
                aws_access_key_id=self.aws_access_id,
                aws_secret_access_key=self.aws_access_secret,
            )
            s3 = session.resource("s3")
            s3_client = session.client("s3")

        with tempfile.TemporaryDirectory() as temp_dir:
            if self.key:
                filepath = f"{temp_dir}/{self.key}"
                s3_client.download_file(self.bucket, self.key, filepath)
            else:
                bucket = s3.Bucket(self.bucket)
                for obj in bucket.objects.filter(Prefix=self.prefix):
                    filepath = f"{temp_dir}/{obj.key}"
                    s3_client.download_file(self.bucket, obj.key, filepath)

            SimpleDirectoryReader = download_loader("SimpleDirectoryReader")
            loader = SimpleDirectoryReader(temp_dir, file_extractor=self.file_extractor)

            return loader.load_data()
