# Opensearch Loader

The Opensearch Loader returns a set of texts corresponding to documents retrieved from an Opensearch index.
The user initializes the loader with an Opensearch index. They then pass in a field, and optionally a JSON query DSL object to fetch the fields they want.

## Usage

Here's an example usage of the OpensearchReader to load 100 documents.

```python
from llama_index import download_loader

OpensearchReader = download_loader("OpensearchReader")

reader = OpensearchReader(
    host="localhost", 
    port=9200, 
    index="<index_name>", 
    basic_auth=('<user_name>', '<password>')
)

query = {
    'size': 100,
    'query': {
        'match_all': {}
    }
}
documents = reader.load_data(
    "<field_name>", 
    query=query, 
    embedding_field="field_name"
)
```

This loader is designed to be used as a way to load data into [LlamaIndex](https://github.com/run-llama/llama_index/tree/main/llama_index) and/or subsequently used as a Tool in a [LangChain](https://github.com/hwchase17/langchain) Agent. See [here](https://github.com/emptycrown/llama-hub/tree/main) for examples.
