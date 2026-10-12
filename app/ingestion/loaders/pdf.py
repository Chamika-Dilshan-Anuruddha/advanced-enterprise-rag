import logfire
from langchain_community.document_loaders import PyPDFLoader


def parse_pdf(file_path: str) -> str:
    """Parse pdf files in to texst using langchain and pypdf."""

    with logfire.span("PyPDF Parsing", filename=file_path):
        try:
            loader = PyPDFLoader(file_path = file_path)
            pages = loader.load()

            final_text = []
            for page in pages:
                final_text.append(page.page_content.strip())

            final_text = "\n\n".join(final_text)

            if not final_text.strip():
                logfire.warning(f"PyPDF returned empty text for: {file_path}")
            else:
                logfire.info(f"PyPDf successfully parsed {len(final_text)} characters")

            return final_text

        except Exception as e:
            logfire.error(f"PyPDF Parse Failed: {e}")
            raise e