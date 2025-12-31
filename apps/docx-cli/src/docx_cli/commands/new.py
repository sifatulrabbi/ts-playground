"""New command - Create a project from a DOCX file."""

from pathlib import Path
from typing import Optional

import typer

from docx_cli.core.project import (
    create_project,
    generate_project_id,
    get_project_paths,
    project_exists,
)
from docx_cli.core.docx_parser import parse_docx_to_project


def new_project(
    input: Path = typer.Option(..., "--input", "-i", help="Path to the DOCX file"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Custom project name"),
    project_dir: Optional[str] = typer.Option(
        None, "--project-dir", "-d", help="Projects directory"
    ),
) -> None:
    """Create a new project from a DOCX file."""
    # Validate input file
    if not input.exists():
        typer.echo(f"Error: File not found: {input}", err=True)
        raise typer.Exit(1)

    if not input.suffix.lower() == ".docx":
        typer.echo(f"Error: File must be a .docx file: {input}", err=True)
        raise typer.Exit(1)

    # Generate project ID
    project_id = name if name else generate_project_id(input.name)

    # Check if project already exists
    if project_exists(project_id, project_dir):
        typer.echo(f"Error: Project already exists: {project_id}", err=True)
        typer.echo("Use --name to specify a different project name.")
        raise typer.Exit(1)

    # Get project paths
    paths = get_project_paths(project_id, project_dir)

    typer.echo(f"Creating project '{project_id}'...")

    try:
        # Parse DOCX and create project files
        element_count = parse_docx_to_project(
            input_path=input,
            base_docx_path=paths.base_docx,
            preview_html_path=paths.preview_html,
            styles_css_path=paths.styles_css,
        )

        # Create project metadata
        project = create_project(
            input_path=input,
            project_id=project_id,
            element_count=element_count,
            project_dir=project_dir,
        )

        typer.echo(f"Created project: {project.id}")
        typer.echo(f"  Elements: {element_count}")
        typer.echo(f"  Location: {paths.root}")
        typer.echo(f"  Preview: {paths.preview_html}")

    except Exception as e:
        typer.echo(f"Error creating project: {e}", err=True)
        raise typer.Exit(1)
