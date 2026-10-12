import logfire
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """Chunk text using langchain's recursive character text splitter."""
    with logfire.span("Text Chunking", text_length=len(text)):
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap
            )
            chunked_text_list = text_splitter.split_text(text)
            logfire.info(f"Generated {len(chunked_text_list)} chunks")
            return chunked_text_list
        except Exception as e:
            logfire.error(f"Chunking Failed, for text size: {len(text)}")