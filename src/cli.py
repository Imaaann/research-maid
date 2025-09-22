import click
from click.types import Path

from .vectordb import get_faiss_index
from .db_utils import init_sqlite_db
from .pdf_utils import copy_pdf
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
       faiss_index = get_faiss_index(project_name)
    except Exception as e:
        db_conn.rollback()
        print(f"ERROR: FAISS Indexing failed: {e}")
        

   

@cli.command()
@click.argument("project_name")
@click.argument("target_pdf", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--threshold", "-t", default=0.6, help="Similarity threshold (default: 0.6)"
)
def cite(project_name: str, target_pdf: Path, threshold: float):
    """Cite a target PDF using project sources."""
    print(f"project {project_name}, file: {target_pdf.name}, threshold: {threshold}")


if __name__ == "__main__":
    cli()
