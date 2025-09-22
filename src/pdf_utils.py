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

    counter = 1
    while target.exists():
        target = project_dir / f"{source.stem}_{counter}{source.suffix}"
        counter += 1

    shutil.copy2(source, target)
