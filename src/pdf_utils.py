from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import shutil
from .project import get_project_dir


def copy_pdf(pdf_path: str, project_name: str):
    source = Path(pdf_path).resolve()

    if not source.exists():
        raise FileNotFoundError(f"file not found: {pdf_path}")

    if source.suffix.lower() != ".pdf":
        raise ValueError(f"file must be a pdf: {pdf_path}")

    project_dir = get_project_dir(project_name)
    target = project_dir / "documents" / source.name

    if target.exists():
        raise FileExistsError(f"file already exists: {target}")

    shutil.copy2(source, target)
    return target

def load_and_split_pdf(file_path: str, chunk_size=200, chunk_overlap=20):
    loader = PyMuPDFLoader(file_path)
    raw_docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " "]
            )

    split_docs = splitter.split_documents(raw_docs)

    output = []
    for doc in split_docs:
        text = doc.page_content
        metadata = doc.metadata
        output.append((text, metadata))

    return output
