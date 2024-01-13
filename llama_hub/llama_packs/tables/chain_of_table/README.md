# Chain-of-table Pack

This LlamaPack implements the [Chain-of-Table paper by Wang et al.](https://arxiv.org/pdf/2401.04398v1.pdf).

Chain-of-Table proposes the following: given a user query over tabular data, plan out a sequence of tabular operations over the table to retrieve the right information in order to satisfy the user query. The updated table is explicitly used/modified throughout the intermediate chain (unlike chain-of-thought/ReAct which uses generic thoughts). 

There is a fixed set of tabular operations that are defined in the paper:
- `f_add_column`
- `f_select_row`
- `f_select_column`
- `f_group_by`
- `f_sort_by`

We implemented the paper based on the prompts described in the paper, and adapted it to get it working. That said, this is marked as beta, so there may still be kinks to work through. Do you have suggestions / contributions on how to improve the robustness? Let us know! 

A full notebook guide can be found [here](https://github.com/run-llama/llama-hub/blob/main/llama_hub/llama_packs/tables/chain_of_table/chain_of_table.ipynb).

## CLI Usage

You can download llamapacks directly using `llamaindex-cli`, which comes installed with the `llama-index` python package:

```bash
llamaindex-cli download-llamapack ChainOfTablePack --download-dir ./chain_of_table_pack
```

You can then inspect the files at `./chain_of_table_pack` and use them as a template for your own project!

## Code Usage

We will show you how to import the agent from these files!

```python
from llama_index.llama_pack import download_llama_pack

# download and install dependencies
ChainOfTablePack = download_llama_pack(
  "ChainOfTablePack", "./chain_of_table_pack"
)

```

From here, you can use the pack. You can import the relevant modules from the download folder (in the example below we assume it's a relative import or the directory 
has been added to your system path).

```python
from chain_of_table_pack.base import ChainOfTableQueryEngine, serialize_table

query_engine = ChainOfTableQueryEngine(df, llm=llm, verbose=True)
response = query_engine.query("Who won best Director in the 1972 Academy Awards?")
```

You can also use/initialize the pack directly.

```python
from llm_compiler_agent_pack.base import ChainOfTablePack

agent_pack = ChainOfTablePack(df, llm=llm, verbose=True)
```

The `run()` function is a light wrapper around `agent.chat()`.

```python
response = pack.run("Who won best Director in the 1972 Academy Awards?")
```
