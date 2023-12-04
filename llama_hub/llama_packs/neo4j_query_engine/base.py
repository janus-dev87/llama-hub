"""Neo4j Query Engine Pack."""


from typing import Any, Dict, List, Optional
from enum import Enum

from llama_index.llama_pack.base import BaseLlamaPack
from llama_index.schema import Document
from llama_index.graph_stores import Neo4jGraphStore
from llama_index.llms import OpenAI
from llama_index import (
    StorageContext,
    ServiceContext,
    KnowledgeGraphIndex,
)
from llama_index import get_response_synthesizer, VectorStoreIndex
from llama_index.text_splitter import SentenceSplitter
from llama_index.retrievers import VectorIndexRetriever, KGTableRetriever


class Neo4jQueryEngineType(str, Enum):
    """Neo4j query engine type"""

    KG_KEYWORD = "keyword"
    KG_HYBRID = "hybrid"
    RAW_VECTOR = "vector"
    RAW_VECTOR_KG_COMBO = "vector_kg"
    KG_QE = "KnowledgeGraphQueryEngine"
    KG_RAG_RETRIEVER = "KnowledgeGraphRAGRetriever"


class Neo4jQueryEnginePack(BaseLlamaPack):
    """Neo4j Query Engine pack."""

    def __init__(
        self,
        username: str,
        password: str,
        url: str,
        database: str,
        docs: List[Document],
        query_engine_type: Optional[Neo4jQueryEngineType] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""

        neo4j_graph_store = Neo4jGraphStore(
            username=username,
            password=password,
            url=url,
            database=database,
        )

        neo4j_storage_context = StorageContext.from_defaults(
            graph_store=neo4j_graph_store
        )

        # define LLM
        self.llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")
        self.service_context = ServiceContext.from_defaults(llm=self.llm)

        neo4j_index = KnowledgeGraphIndex.from_documents(
            documents=docs,
            storage_context=neo4j_storage_context,
            max_triplets_per_chunk=10,
            service_context=self.service_context,
            include_embeddings=True,
        )

        # create node parser to parse nodes from document
        node_parser = SentenceSplitter(chunk_size=512)

        # use transforms directly
        nodes = node_parser(docs)
        print(f"loaded nodes with {len(nodes)} nodes")

        # based on the nodes and service_context, create index
        vector_index = VectorStoreIndex(
            nodes=nodes, service_context=self.service_context
        )

        if query_engine_type == Neo4jQueryEngineType.KG_KEYWORD:
            # KG keyword-based entity retrieval
            self.query_engine = neo4j_index.as_query_engine(
                # setting to false uses the raw triplets instead of adding the text from the corresponding nodes
                include_text=False,
                retriever_mode="keyword",
                response_mode="tree_summarize",
            )

        elif query_engine_type == Neo4jQueryEngineType.KG_HYBRID:
            # KG hybrid entity retrieval
            self.query_engine = neo4j_index.as_query_engine(
                include_text=True,
                response_mode="tree_summarize",
                embedding_mode="hybrid",
                similarity_top_k=3,
                explore_global_knowledge=True,
            )

        elif query_engine_type == Neo4jQueryEngineType.RAW_VECTOR:
            # Raw vector index retrieval
            self.query_engine = vector_index.as_query_engine()

        elif query_engine_type == Neo4jQueryEngineType.RAW_VECTOR_KG_COMBO:
            from llama_index.query_engine import RetrieverQueryEngine

            # create neo4j custom retriever
            neo4j_vector_retriever = VectorIndexRetriever(index=vector_index)
            neo4j_kg_retriever = KGTableRetriever(
                index=neo4j_index, retriever_mode="keyword", include_text=False
            )
            neo4j_custom_retriever = CustomRetriever(
                neo4j_vector_retriever, neo4j_kg_retriever
            )

            # create neo4j response synthesizer
            neo4j_response_synthesizer = get_response_synthesizer(
                service_context=self.service_context,
                response_mode="tree_summarize",
            )

            # Custom combo query engine
            self.query_engine = RetrieverQueryEngine(
                retriever=neo4j_custom_retriever,
                response_synthesizer=neo4j_response_synthesizer,
            )

        elif query_engine_type == Neo4jQueryEngineType.KG_QE:
            # using KnowledgeGraphQueryEngine
            from llama_index.query_engine import KnowledgeGraphQueryEngine

            self.query_engine = KnowledgeGraphQueryEngine(
                storage_context=neo4j_storage_context,
                service_context=self.service_context,
                llm=self.llm,
                verbose=True,
            )

        elif query_engine_type == Neo4jQueryEngineType.KG_RAG_RETRIEVER:
            # using KnowledgeGraphRAGRetriever
            from llama_index.query_engine import RetrieverQueryEngine
            from llama_index.retrievers import KnowledgeGraphRAGRetriever

            neo4j_graph_rag_retriever = KnowledgeGraphRAGRetriever(
                storage_context=neo4j_storage_context,
                service_context=self.service_context,
                llm=self.llm,
                verbose=True,
            )

            self.query_engine = RetrieverQueryEngine.from_args(
                neo4j_graph_rag_retriever, service_context=self.service_context
            )

        else:
            # KG vector-based entity retrieval
            self.query_engine = neo4j_index.as_query_engine()

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "llm": self.llm,
            "service_context": self.service_context,
            "query_engine": self.query_engine,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return self.query_engine.query(*args, **kwargs)


from llama_index import QueryBundle
from llama_index.schema import NodeWithScore
from llama_index.retrievers import BaseRetriever, VectorIndexRetriever, KGTableRetriever
from typing import List


class CustomRetriever(BaseRetriever):
    """Custom retriever that performs both Vector search and Knowledge Graph search"""

    def __init__(
        self,
        vector_retriever: VectorIndexRetriever,
        kg_retriever: KGTableRetriever,
        mode: str = "OR",
    ) -> None:
        """Init params."""

        self._vector_retriever = vector_retriever
        self._kg_retriever = kg_retriever
        if mode not in ("AND", "OR"):
            raise ValueError("Invalid mode.")
        self._mode = mode

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes given query."""

        vector_nodes = self._vector_retriever.retrieve(query_bundle)
        kg_nodes = self._kg_retriever.retrieve(query_bundle)

        vector_ids = {n.node.node_id for n in vector_nodes}
        kg_ids = {n.node.node_id for n in kg_nodes}

        combined_dict = {n.node.node_id: n for n in vector_nodes}
        combined_dict.update({n.node.node_id: n for n in kg_nodes})

        if self._mode == "AND":
            retrieve_ids = vector_ids.intersection(kg_ids)
        else:
            retrieve_ids = vector_ids.union(kg_ids)

        retrieve_nodes = [combined_dict[rid] for rid in retrieve_ids]
        return retrieve_nodes
