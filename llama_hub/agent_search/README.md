# AgentSearch Loader

This framework facilitates seamless integration with the AgentSearch dataset or hosted search APIs (e.g. Search Engines) and with RAG-specialized LLM's (e.g. Search Agents).

During query-time, the user passes in the query string, search provider (`bing`, `agent-search`), and RAG provider model (`SciPhi/Sensei-7B-V1`). 

To learn more, please refer to the documentation [here](https://agent-search.readthedocs.io/en/latest/).

## Usage

Here's an example usage of the AgentSearchReader.

```python
# Optionally set the API key in the env
# import os
# os.environ["SCIPHI_API_KEY"] = "..."

from llama_index import download_loader

AgentSearch = download_loader("AgentSearchReader")

reader = AgentSearch()

document = reader.load_data(
    query="latest news",
)[0]
# text = "The latest news encompasses ... and its consequences [2]."
# metadata = {'related_queries': ['Details on the...', ...], 'search_results' : [...]}
```

This loader is designed to be used as a way to load data into [LlamaIndex](https://github.com/run-llama/llama_index/tree/main/llama_index) and/or subsequently used as a Tool in a [LangChain](https://github.com/hwchase17/langchain) Agent. See [here](https://github.com/emptycrown/llama-hub/tree/main) for examples.
