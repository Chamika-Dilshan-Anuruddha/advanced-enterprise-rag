import logfire
from bs4 import BeautifulSoup
from pathlib import Path

def parse_html(file_path: str) -> str:
    """Parses HTML content using BeautifulSoup into clean text."""

    with logfire.span("HTML Parsing", filename=file_path):
        try:
            with open(Path(file_path), 'r', encoding='utf-8') as file:
                html_cont = file.read()

            soup = BeautifulSoup(html_cont, 'html.parser')

            # kill all script and style elements
            for script in soup(["script", "style", "meta", "noscript"]):
                script.extract()    # rip it out

            text = soup.get_text()

            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            logfire.error(f"HTML Parse Failed: {e}")
            raise e

    
