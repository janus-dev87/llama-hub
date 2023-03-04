"""Simple Reader that loads highlights from readwise.io"""
import requests
import json
from typing import List

from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document

def _get_readwise_data(api_key, updated_after=None):
  """
  Uses Readwise's export API to export all highlights, optionally after a specified date.

  See https://readwise.io/api_deets for details.

  Args:
      updated_after (datetime.datetime): The datetime to load highlights after. Useful for updating indexes over time.
  """
  next_page = None
  while True:
    response = requests.get(
      url="https://readwise.io/api/v2/export/",
      params={"pageCursor": next_page, "updatedAfter": updated_after},
      headers={"Authorization": f"Token {api_key}"})
    response.raise_for_status()
    yield from response.json()["results"]
    next_page = response.json().get("nextPageCursor")
    if not next_page: break

class ReadwiseReader(BaseReader):
    """
    Reader for Readwise highlights.
    """
    def __init__(self, api_key):
        self._api_key = api_key

    def load_data(
        self,
        updated_after = None,
    ) -> List[Document]:
        """
        Load your Readwise.io highlights.

        Args:
            updated_after (datetime.datetime): The datetime to load highlights after. Useful for updating indexes over time.
        """
        docs = [*_get_readwise_data(api_key=self._api_key, updated_after=updated_after)]
        print(docs[0].keys())
        result = [Document(json.dumps(d)) for d in docs]
        for x in result:
          print(x.get_text())
        return result
