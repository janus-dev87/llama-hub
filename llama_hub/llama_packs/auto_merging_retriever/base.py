"""Auto Merging Retriever."""

from llama_index import ServiceContext, VectorStoreIndex
from llama_index.llms import OpenAI
from llama_index.node_parser import (
    HierarchicalNodeParser,
    get_leaf_nodes,
)
from typing import List, Dict, Any
from llama_index.llama_pack.base import BaseLlamaPack
from llama_index.schema import Document
from llama_index.retrievers.auto_merging_retriever import AutoMergingRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.storage import StorageContext


class AutoMergingRetrieverPack(BaseLlamaPack):
    """Auto-merging Retriever pack.

    Build a hiearchical node graph from a set of documents, and
    run our auto-merging retriever.

    """

    def __init__(
        self,
        docs: List[Document] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        # create the sentence window node parser w/ default settings
        self.node_parser = HierarchicalNodeParser.from_defaults()
        nodes = self.node_parser.get_nodes_from_documents(docs)
        leaf_nodes = get_leaf_nodes(nodes)
        docstore = SimpleDocumentStore()

        # insert nodes into docstore
        docstore.add_documents(nodes)

        # define storage context (will include vector store by default too)
        storage_context = StorageContext.from_defaults(docstore=docstore)

        service_context = ServiceContext.from_defaults(
            llm=OpenAI(model="gpt-3.5-turbo")
        )
        self.base_index = VectorStoreIndex(
            leaf_nodes,
            storage_context=storage_context,
            service_context=service_context,
        )
        base_retriever = self.base_index.as_retriever(similarity_top_k=6)
        self.retriever = AutoMergingRetriever(
            base_retriever, storage_context, verbose=True
        )
        self.query_engine = RetrieverQueryEngine.from_args(self.retriever)

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "node_parser": self.node_parser,
            "retriever": self.retriever,
            "query_engine": self.query_engine,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return self.query_engine.query(*args, **kwargs)
