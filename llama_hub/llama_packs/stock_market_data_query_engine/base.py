from typing import List, Dict, Any, Optional

from llama_index.llama_pack.base import BaseLlamaPack
from llama_index.schema import IndexNode
from llama_index import VectorStoreIndex
from llama_index.query_engine import PandasQueryEngine
from llama_index.retrievers import RecursiveRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.response_synthesizers import get_response_synthesizer
from llama_index.llms.llm import LLM
from llama_index.llms import OpenAI
from llama_index.service_context import ServiceContext


class StockMarketDataQueryEnginePack(BaseLlamaPack):
    """Historical stock market data query engine pack."""

    def __init__(
        self,
        tickers: List[str],
        llm: Optional[LLM] = None,
        **kwargs: Any,
    ):
        self.tickers = tickers

        try:
            import yfinance as yf
        except ImportError:
            raise ImportError("Dependencies missing, run `pip install yfinance`")

        stocks_market_data = []
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(**kwargs)

            year = [i.year for i in hist.index]
            hist.insert(0, "year", year)
            month = [i.month for i in hist.index]
            hist.insert(1, "month", month)
            day = [i.day for i in hist.index]
            hist.insert(2, "day", day)
            hist.reset_index(drop=True, inplace=True)
            stocks_market_data.append(hist)
        self.stocks_market_data = stocks_market_data

        service_context = ServiceContext.from_defaults(llm=llm or OpenAI(model="gpt-4"))

        df_price_query_engines = [
            PandasQueryEngine(stock, service_context=service_context)
            for stock in stocks_market_data
        ]

        summaries = [f"{ticker} historical market data" for ticker in tickers]

        df_price_nodes = [
            IndexNode(text=summary, index_id=f"pandas{idx}")
            for idx, summary in enumerate(summaries)
        ]

        df_price_id_query_engine_mapping = {
            f"pandas{idx}": df_engine
            for idx, df_engine in enumerate(df_price_query_engines)
        }

        stock_price_vector_index = VectorStoreIndex(
            df_price_nodes, service_context=service_context
        )
        stock_price_vector_retriever = stock_price_vector_index.as_retriever(
            similarity_top_k=1
        )

        stock_price_recursive_retriever = RecursiveRetriever(
            "vector",
            retriever_dict={"vector": stock_price_vector_retriever},
            query_engine_dict=df_price_id_query_engine_mapping,
            verbose=True,
        )

        stock_price_response_synthesizer = get_response_synthesizer(
            # service_context=service_context,
            response_mode="compact",
            service_context=service_context,
        )

        stock_price_query_engine = RetrieverQueryEngine.from_args(
            stock_price_recursive_retriever,
            response_synthesizer=stock_price_response_synthesizer,
        )

        self.stock_price_query_engine = stock_price_query_engine

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "tickers": self.tickers,
            "stocks market data": self.stocks_market_data,
            "query engine": self.stock_price_query_engine,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run."""
        return self.stock_price_query_engine.query(*args, **kwargs)
