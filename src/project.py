from datetime import datetime
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"


def create_project(project_name: str):
    """
    Create a new research-maid projects

    Structure:
        <project-name>/
            documents/    -- source PDFs
            citation.json -- citation mapping
            manifest.json -- metadata
    """

    PROJECTS_DIR.mkdir(exist_ok=True)

    project_dir = PROJECTS_DIR / project_name
    if project_dir.exists():
        raise FileExistsError(f"Project '{project_name}' already exists!")

    documents_dir = project_dir / "documents"
    project_dir.mkdir()
    documents_dir.mkdir()

    citations_file = project_dir / "citation.json"
    citations_file.write_text(json.dumps({}, indent=2, ensure_ascii=False))

    manifest_file = project_dir / "manifest.json"
    manifest = {
        "project_name": project_name,
        "documents_dir": str(documents_dir),
        "num_documents": 0,
        "created_at": datetime.now().isoformat() + "Z",
        "version": "0.1.0",
    }

    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print(
        f"[research-maid]: Successfully created project {project_name} at {project_dir}"
    )
