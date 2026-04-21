from typing import List
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
from llama_searcher.utils.logger import logger

encoding = tiktoken.get_encoding("cl100k_base")
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", ". ", "\n", " "],
    length_function=lambda x: len(encoding.encode(x)),
)


def fly_search(query: str, res: List[str], top_k: int = 4) -> str:
    """Implement RAG (Retrieval-Augmented Generation) to find the most similar content."""
    try:
        vector_store = InMemoryVectorStore(embeddings)

        valid_results = [str(item) for item in res if item]

        if not valid_results:
            return "No valid content found for similarity search"

        results_split = splitter.split_documents(
            [Document(page_content=item) for item in valid_results]
        )

        if not results_split:
            return "No content chunks created for similarity search"

        vector_store.add_documents(documents=results_split)

        results = vector_store.similarity_search(
            query=query, k=min(top_k, len(results_split))
        )

        formatted_results = [
            f"--- Relevant Content {i + 1} ---\n{result.page_content}\n"
            for i, result in enumerate(results)
        ]

        return "\n".join(formatted_results)

    except Exception as e:
        logger.error(f"Error in fly_search: {str(e)}")
        return f"Error performing similarity search: {str(e)}"
