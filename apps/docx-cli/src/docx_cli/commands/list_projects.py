"""List command - Show all projects."""

from typing import Optional

import typer

from docx_cli.core.project import get_updates, list_all_projects


def list_projects(
    project_dir: Optional[str] = typer.Option(
        None, "--project-dir", "-d", help="Projects directory"
    ),
) -> None:
    """List all projects."""
    projects = list_all_projects(project_dir)

    if not projects:
        typer.echo("No projects found.")
        return

    typer.echo(f"Found {len(projects)} project(s):\n")

    for project in projects:
        updates = get_updates(project.id, project_dir)
        update_count = len(updates)

        # Format date
        created = project.created_at[:10]

        typer.echo(f"  {project.id}")
        typer.echo(f"    Elements: {project.element_count}")
        typer.echo(f"    Updates: {update_count}")
        typer.echo(f"    Created: {created}")
        typer.echo("")
