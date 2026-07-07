from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document


# Path to the backend directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Path to the knowledge base folder
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base"


def load_documents() -> list[Document]: 
    """
    Load all Markdown documents from the knowledge base.
    """

    loader = DirectoryLoader(
        path=str(KNOWLEDGE_BASE_PATH), #we are converting into string because variable KNOWLEDGE_BASE_PATH is a path object, the functions expects a string
        glob="*.md", #loads all .md files ONLY
        loader_cls=TextLoader, #tells DirectoryLoader that whenever you find a .md file, read its plain text
    )

    documents = loader.load()

    return documents