import json
import faiss
import pickle
import numpy as np
from .db_utils import get_connection
from .project import get_project_dir

_index = None
_metadata = []


def query_index(project_name: str, query_embdedding: list[float], top_k: int = 5):
    index = get_faiss_index(project_name)
    metadata = get_metadata()
    db_conn = get_connection()

    if index.ntotal == 0:
        return []

    D, I = index.search(np.array([query_embdedding]).astype("float32"), top_k)

    cursor = db_conn.cursor()
    results = []
    for doc_id, dist in zip(I[0], D[0]):
        if doc_id == -1:
            continue
        cursor.execute("SELECT text, metadata FROM chunks WHERE id = ?", int(doc_id))
        row = cursor.fetchone()
        if row:
            text, metadata_json = row
            metadata = json.loads(metadata_json)
            results.append(
                {
                    "id": int(doc_id),
                    "text": text,
                    "metadata": metadata,
                    "distance": float(dist),
                }
            )


def get_faiss_index(project_name: str, dim: int = 384):
    global _index, _metadata
    project_dir = get_project_dir(project_name)
    index_path = project_dir / "faiss_index"  # need to find the correct extension here
    metadata_path = (
        project_dir / "metadata.pkl"
    )  # same here to be honest I think it is .pkl

    if _index is not None:
        return _index

    if index_path.exists():
        print("INFO: Loading Faiss index from disk...")
        _index = faiss.read_index(str(index_path))
    else:
        print("INFO: Creating new Faiss index")
        _index = faiss.IndexIDMap2(faiss.IndexFlatL2(dim))

    if metadata_path.exists():
        with open(str(metadata_path), "rb") as f:
            _metadata = pickle.load(f)

    return _index


def get_metadata():
    return _metadata


def add_to_index(
    project_name: str, embeddings: list[list[float]], metadatas: list[dict]
):
    global _metadata

    index = get_faiss_index(project_name)
    vectors = np.array(embeddings).astype("float32")
    number = embeddings.__len__()
    index.add(number, vectors)

    _metadata.extend(metadatas)
    save_index(project_name)


def save_index(project_name: str):
    project_dir = get_project_dir(project_name)
    index_path = project_dir / "faiss_index"
    metadata_path = project_dir / "metadata.pkl"
    faiss.write_index(_index, str(index_path))
    with open(str(metadata_path), "wb") as f:
        pickle.dump(_metadata, f)
    print("INFO: Faiss index saved to disk...")
