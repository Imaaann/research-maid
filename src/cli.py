import json
import numpy as np
import click
from click.types import Path

from .vectordb import embed_query, embed_texts, get_faiss_index, query_index, save_index
from .db_utils import init_sqlite_db
from .pdf_utils import copy_pdf, load_and_split_pdf
from .project import create_project


@click.group()
def cli():
    """research-maid: auto-cite tool for research PDFs."""
    pass


@cli.command()
@click.argument("project_name")
def create(project_name: str):
    """Create a new project."""
    create_project(project_name)


@cli.command()
@click.argument("project_name")
@click.argument("pdf_path")
def add(project_name: str, pdf_path: str):
    copy_path = copy_pdf(pdf_path, project_name)
    db_conn = init_sqlite_db(project_name)
    try:
        index = get_faiss_index(project_name)

        chunks = load_and_split_pdf(str(copy_path))
        texts = [c[0] for c in chunks]
        metadatas = [c[1] for c in chunks]

        embeddings = embed_texts(texts)

        cursor = db_conn.cursor()
        vectors = np.array(embeddings, dtype="float32")

        for idx, (text, meta, vec) in enumerate(zip(texts, metadatas, vectors)):
            meta_json = json.dumps(meta)
            cursor.execute(
                "INSERT INTO chunks (text, metadata) VALUES (?, ?)", (text, meta_json)
            )
            chunk_id = cursor.lastrowid

            vec_np = np.array([vec], dtype="float32")
            id_np = np.array([chunk_id], dtype=np.int64)
            index.add_with_ids(vec_np, id_np)

        db_conn.commit()
        save_index(project_name)

    except Exception as e:
        db_conn.rollback()
        print(f"ERROR: Adding document failed: {e}")


@cli.command()
@click.argument("project_name")
@click.argument("target_pdf")
def cite(project_name: str, target_pdf: str):
    """Cite a target PDF using project sources."""
    init_sqlite_db(project_name)
    chunks = load_and_split_pdf(target_pdf)
    texts = [c[0] for c in chunks]
    for text in texts:
        emb = embed_query(text)
        hits = query_index(project_name, emb)
        print("========== NEW TEXT CHUNK ============")
        print("\n\n\nHITS: ")
        __import__("pprint").pprint(hits)

        # print("\n\n\nTEXT CHUNK: ")
        # __import__("pprint").pprint(text)


if __name__ == "__main__":
    cli()
