import click
from click.types import Path

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
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))
def add(project_name: str, pdf_path: Path):
    """Add a source PDF to a project."""
    print(f"Added to project {project_name}: file:{pdf_path}")


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
