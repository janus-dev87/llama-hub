# Llama Hub 🦙

This is a simple library of all the data loaders / readers that have been created by the community. The goal is to make it extremely easy to connect large language models to a large variety of knowledge sources. These are general-purpose utilities that are meant to be used in [GPT Index](https://github.com/jerryjliu/gpt_index/tree/main/gpt_index) (e.g. when building a index) and [LangChain](https://github.com/hwchase17/langchain) (e.g. when building different tools an agent can use). For example, there are loaders to parse Google Docs, SQL Databases, PDF files, PowerPoints, Notion, Slack, Obsidian, and many more. Note that because different loaders produce the same types of Documents, you can easily use them together in the same index.

Check out our website here: https://llamahub.ai/.

## Usage

These general-purpose loaders are designed to be used as a way to load data into [GPT Index](https://github.com/jerryjliu/gpt_index/tree/main/gpt_index) and/or subsequently used as a Tool in a [LangChain](https://github.com/hwchase17/langchain) Agent. **You can use them with `download_loader` from GPT Index in a single line of code!** For example, see the code snippets below using the Google Docs Loader.

### GPT Index

```python
from gpt_index import GPTSimpleVectorIndex, download_loader

GoogleDocsReader = download_loader('GoogleDocsReader')

gdoc_ids = ['1wf-y2pd9C878Oh-FmLH7Q_BQkljdm6TQal-c1pUfrec']
loader = GoogleDocsReader()
documents = loader.load_data(document_ids=gdoc_ids)
index = GPTSimpleVectorIndex(documents)
index.query('Where did the author go to school?')
```

### LangChain

Note: Make sure you change the description of the `Tool` to match your use-case.

```python
from gpt_index import GPTSimpleVectorIndex, download_loader
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI
from langchain.chains.conversation.memory import ConversationBufferMemory

GoogleDocsReader = download_loader('GoogleDocsReader')

gdoc_ids = ['1wf-y2pd9C878Oh-FmLH7Q_BQkljdm6TQal-c1pUfrec']
loader = GoogleDocsReader()
documents = loader.load_data(document_ids=gdoc_ids)
index = GPTSimpleVectorIndex(documents)

tools = [
    Tool(
        name="Google Doc Index",
        func=lambda q: index.query(q),
        description=f"Useful when you want answer questions about the Google Documents.",
    ),
]
llm = OpenAI(temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history")
agent_chain = initialize_agent(
    tools, llm, agent="zero-shot-react-description", memory=memory
)

output = agent_chain.run(input="Where did the author go to school?")
```

## How to add a loader

Adding a loader simply requires forking this repo and making a Pull Request. The Loader Hub website will update automatically. However, please keep in the mind the following guidelines when making your PR.

### Step 1: Create a new directory

In `loader_hub`, create a new directory for your new loader. It can be nested within another, but name it something unique because the name of the directory will become the identifier for your loader (e.g. `google_docs`). Inside your new directory, create a `__init__.py` file, which can be empty, a `base.py` file which will contain your loader implementation, and, if needed, a `requirements.txt` file to list the package dependencies of your loader. Those packages will automatically be installed when your loader is used, so no need to worry about that anymore!

If you'd like, you can create the new directory and files by running the following script in the `loader_hub` directory. Just remember to put your dependencies into a `requirements.txt` file.

```
./add_loader.sh [NAME_OF_NEW_DIRECTORY]
```

### Step 2: Write your README

Inside your new directory, create a `README.md` that mirrors that of the existing ones. It should have a summary of what your loader does, its inputs, and how its used in the context of GPT Index and LangChain.

### Step 3: Add your loader to the library.json file

Finally, add your loader to the `loader_hub/library.json` file so that it may be used by others. As is exemplified by the current file, add in the class name of your loader, along with its id, author, etc. This file is referenced by the Loader Hub website and the download function within GPT Index.

### Step 4: Make a Pull Request!

Create a PR against the main branch. We typically review the PR within a day. To help expedite the process, it may be helpful to provide screenshots (either in the PR or in
the README directly) showing your data loader in action!

## FAQ

### Should I create a PR against Llama Hub or the GPT Index repo directly?

If you have a data loader PR, by default let's try to create it against Llama Hub! We will make exceptions in certain cases
(for instance, if we think the data loader should be core to the GPT Index repo).

For all other PR's relevant to GPT Index, let's create it directly against the [GPT Index repo](https://github.com/jerryjliu/gpt_index).

### Other questions?

Feel free to hop into the [community Discord](https://discord.gg/dGcwcsnxhU) or tag the official [Twitter account](https://twitter.com/gpt_index)!
