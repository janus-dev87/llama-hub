"""Pandas AI loader."""

from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document
from llama_index.readers.download import download_loader
from tempfile import TemporaryDirectory


class PandasAIReader(BaseReader):
    """Pandas AI reader.

    Light wrapper around https://github.com/gventuri/pandas-ai.

    Args:
        llm (Optional[pandas.llm]): LLM to use. Defaults to None.
        concat_rows (bool): whether to concatenate all rows into one document.
            If set to False, a Document will be created for each row.
            True by default.

        col_joiner (str): Separator to use for joining cols per row.
            Set to ", " by default.

        row_joiner (str): Separator to use for joining each row.
            Only used when `concat_rows=True`.
            Set to "\n" by default.

        pandas_config (dict): Options for the `pandas.read_csv` function call.
            Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
            for more information.
            Set to empty dict by default, this means pandas will try to figure
            out the separators, table head, etc. on its own.

    """

    def __init__(
        self,
        llm: Optional[Any] = None,
        concat_rows: bool = True,
        col_joiner: str = ", ",
        row_joiner: str = "\n",
        pandas_config: dict = {},
    ) -> None:
        """Init params."""
        try:
            from pandasai.llm.openai import OpenAI
            from pandasai import PandasAI
        except ImportError:
            raise ImportError("Please install pandasai to use this reader.")

        self._llm = llm or OpenAI()
        self._pandas_ai = PandasAI(llm)

        self._concat_rows = concat_rows
        self._col_joiner = col_joiner
        self._row_joiner = row_joiner
        self._pandas_config = pandas_config

    def run_pandas_ai(
        self,
        initial_df: pd.DataFrame,
        query: str,
        is_conversational_answer: bool = False,
    ) -> Any:
        """Load dataframe."""
        import pandasai

        return self._pandas_ai.run(
            initial_df, prompt=query, is_conversational_answer=is_conversational_answer
        )

    def load_data(
        self,
        initial_df: pd.DataFrame,
        query: str,
        is_conversational_answer: bool = False,
    ) -> List[Document]:
        """Parse file."""

        result = self.run_pandas_ai(
            initial_df, query, is_conversational_answer=is_conversational_answer
        )
        if is_conversational_answer:
            return [Document(text=result)]
        else:
            if isinstance(result, (np.generic)):
                result = pd.Series(result)
            elif isinstance(result, (pd.Series, pd.DataFrame)):
                pass
            else:
                raise ValueError("Unexpected type for result: {}".format(type(result)))
            # if not conversational answer, use Pandas CSV Reader

            try:
                from llama_hub.utils import import_loader
                PandasCSVReader = import_loader("PandasCSVReader")
            except ImportError:
                PandasCSVReader = download_loader("PandasCSVReader")

            reader = PandasCSVReader(
                concat_rows=self._concat_rows,
                col_joiner=self._col_joiner,
                row_joiner=self._row_joiner,
                pandas_config=self._pandas_config,
            )

            with TemporaryDirectory() as tmpdir:
                outpath = Path(tmpdir) / "out.csv"
                with outpath.open("w") as f:
                    # TODO: add option to specify index=False
                    result.to_csv(f, index=False)

                docs = reader.load_data(outpath)
                return docs