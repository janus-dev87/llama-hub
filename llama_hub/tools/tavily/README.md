# Tavily Tool

[Tavily](https://app.tavily.com/) is a robust search API tailored specifically for LLM Agents. It seamlessly integrates with diverse data sources to ensure a superior, relevant search experience.

To begin, you need to obtain an API key on the [Tavily's developer dashboard](https://app.tavily.com/).

## Usage

This tool has a more extensive example usage documented in a Jupyter notebook [here](https://github.com/emptycrown/llama-hub/tree/main/llama_hub/tools/notebooks/tavily.ipynb)

Here's an example usage of the TavilyToolSpec.

```python
from llama_hub.tools.tavily import TavilyToolSpec
from llama_index.agent import OpenAIAgent

tavily_tool = TavilyToolSpec(
    api_key='your-key',
)
agent = OpenAIAgent.from_tools(tavily_tool.to_tool_list())

agent.chat('What happened in the latest Burning Man festival?')
```

`search`: Search for relevant dynamic data based on a query. Returns a list of urls and their relevant content.


This loader is designed to be used as a way to load data as a Tool in an Agent. See [here](https://github.com/emptycrown/llama-hub/tree/main) for examples.
