# Snowflake Loader

This loader connects to Snowflake (using SQLAlchemy under the hood). The user specifies a query and extracts Document objects corresponding to the results. You can use this loader to easily connect to a database on Snowflake and pass the documents into a `GPTSQLStructStoreIndex` from LlamaIndex.

## Usage

### Option 1: Pass your own SQLAlchemy Engine object of the database connection
Here's an example usage of the SnowflakeReader.

```python
from llama_index import download_loader

SnowflakeReader = download_loader('SnowflakeReader')

reader = SnowflakeReader(
    engine= your_sqlalchemy_engine,
)

query = "SELECT * FROM your_table"

documents = reader.load_data(query=query)
```


### Option 2: Pass the required parameters to esstablish Snowflake connection
Here's an example usage of the SnowflakeReader.

```python
from llama_index import download_loader

SnowflakeReader = download_loader('SnowflakeReader')

reader = SnowflakeReader(
    account='your_account',
    user='your_user',
    password='your_password',
    database='your_database',
    schema='your_schema',
    warehouse='your_warehouse',
    role='your_role',  # Optional role setting
    proxy='http://proxusername:proxypassword@myproxy:port'  # Optional proxy setting
)

query = "SELECT * FROM your_table"

documents = reader.load_data(query=query)
```

#### Author
[Godwin Paul Vincent](https://github.com/godwin3737)

This loader is designed to be used as a way to load data into [LlamaIndex](https://github.com/run-llama/llama_index/tree/main/llama_index) and/or subsequently used as a Tool in a [LangChain](https://github.com/hwchase17/langchain) Agent. See [here](https://github.com/emptycrown/llama-hub/tree/main) for examples.


