"""Export command - Generate output DOCX with all updates applied."""

from pathlib import Path
from typing import Optional

import typer

from docx_cli.core.project import (
    get_project_paths,
    get_updates,
    load_project,
    project_exists,
)
from docx_cli.core.docx_writer import apply_updates_to_docx


def export_project(
    project_id: str = typer.Argument(..., help="Project ID"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output DOCX path"),
    project_dir: Optional[str] = typer.Option(
        None, "--project-dir", "-d", help="Projects directory"
    ),
) -> None:
    """Export project to DOCX with all updates applied."""
    # Check project exists
    if not project_exists(project_id, project_dir):
        typer.echo(f"Error: Project not found: {project_id}", err=True)
        raise typer.Exit(1)

    # Get project info
    project = load_project(project_id, project_dir)
    paths = get_project_paths(project_id, project_dir)

    # Determine output path
    if output is None:
        output = Path.cwd() / f"{project_id}-output.docx"

    # Get updates
    updates = get_updates(project_id, project_dir)

    typer.echo(f"Exporting '{project_id}'...")
    typer.echo(f"  Updates to apply: {len(updates)}")

    try:
        # Apply updates to DOCX
        apply_updates_to_docx(
            base_docx_path=paths.base_docx,
            output_path=output,
            updates=updates,
        )

        typer.echo(f"Exported to: {output}")

    except Exception as e:
        typer.echo(f"Error exporting: {e}", err=True)
        raise typer.Exit(1)
