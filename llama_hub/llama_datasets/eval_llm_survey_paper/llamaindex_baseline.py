from llama_index.llama_dataset import download_llama_dataset
from llama_index.llama_pack import download_llama_pack
from llama_index import VectorStoreIndex


def main():
    # DOWNLOAD LLAMADATASET
    rag_dataset, documents = download_llama_dataset(
        "EvaluatingLlmSurveyPaperDataset", "./data"
    )

    # BUILD BASIC RAG PIPELINE
    index = VectorStoreIndex.from_documents(documents=documents)
    query_engine = index.as_query_engine()

    # EVALUATE WITH PACK
    RagEvaluatorPack = download_llama_pack("RagEvaluatorPack", "./pack")
    rag_evaluator = RagEvaluatorPack(query_engine=query_engine, rag_dataset=rag_dataset)
    benchmark_df = rag_evaluator.run()
    print(benchmark_df)


if __name__ == "__main__":
    main()
