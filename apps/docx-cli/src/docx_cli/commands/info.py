"""Info command - Show project details."""

from typing import Optional

import typer

from docx_cli.core.project import (
    get_project_paths,
    get_updates,
    load_project,
    project_exists,
)


def project_info(
    project_id: str = typer.Argument(..., help="Project ID"),
    project_dir: Optional[str] = typer.Option(
        None, "--project-dir", "-d", help="Projects directory"
    ),
    show_updates: bool = typer.Option(False, "--updates", "-u", help="Show update history"),
) -> None:
    """Show project details."""
    if not project_exists(project_id, project_dir):
        typer.echo(f"Error: Project not found: {project_id}", err=True)
        raise typer.Exit(1)

    project = load_project(project_id, project_dir)
    paths = get_project_paths(project_id, project_dir)
    updates = get_updates(project_id, project_dir)

    typer.echo(f"Project: {project.id}")
    typer.echo(f"  Original: {project.original_path}")
    typer.echo(f"  Elements: {project.element_count}")
    typer.echo(f"  Created: {project.created_at}")
    typer.echo(f"  Updated: {project.updated_at}")
    typer.echo(f"  Updates: {len(updates)}")
    typer.echo("")
    typer.echo("Files:")
    typer.echo(f"  Project: {paths.project_json}")
    typer.echo(f"  Base DOCX: {paths.base_docx}")
    typer.echo(f"  Preview: {paths.preview_html}")
    typer.echo(f"  Styles: {paths.styles_css}")

    if show_updates and updates:
        typer.echo("")
        typer.echo("Update History:")
        for i, update in enumerate(updates):
            applied_at = update.get("applied_at", "unknown")[:19]
            typer.echo(f"  {i + 1}. [{applied_at}] {update['type']} -> {update['target_element']}")
