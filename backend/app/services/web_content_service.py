import os

os.environ.setdefault("USER_AGENT", "company-knowledge-assistant/1.0")

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document


def load_web_documents(url: str) -> list[Document]:
    loader = WebBaseLoader(web_paths=[url])
    return loader.load()
