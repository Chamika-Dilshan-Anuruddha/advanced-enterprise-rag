import logfire

def parse_text(file_path: str) -> str:
    """Parses plain text files."""
    
    with logfire.span("Text Parsing", filename=file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            return file_content
        except Exception as e:
            logfire.error(f"Text Parse Failed: {e}")
            raise e