"""Update command - Apply updates to a project."""

import json
from pathlib import Path
from typing import Optional

import typer

from docx_cli.core.project import (
    get_project_paths,
    load_project,
    append_updates,
    project_exists,
)
from docx_cli.core.html_updater import (
    apply_updates,
    validate_updates,
)


def update_project(
    project_id: str = typer.Argument(..., help="Project ID"),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Path to JSON file with updates"
    ),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="Inline JSON update command(s)"),
    project_dir: Optional[str] = typer.Option(
        None, "--project-dir", "-d", help="Projects directory"
    ),
) -> None:
    """Apply updates to a project."""
    # Validate we have input
    if file is None and code is None:
        typer.echo("Error: Must provide either --file or --code", err=True)
        raise typer.Exit(1)

    if file is not None and code is not None:
        typer.echo("Error: Cannot use both --file and --code", err=True)
        raise typer.Exit(1)

    # Check project exists
    if not project_exists(project_id, project_dir):
        typer.echo(f"Error: Project not found: {project_id}", err=True)
        raise typer.Exit(1)

    # Parse updates
    try:
        if file is not None:
            if not file.exists():
                typer.echo(f"Error: File not found: {file}", err=True)
                raise typer.Exit(1)

            with open(file, "r", encoding="utf-8") as f:
                updates_data = json.load(f)
        else:
            updates_data = json.loads(code)

        # Normalize to list
        if isinstance(updates_data, dict):
            updates = [updates_data]
        elif isinstance(updates_data, list):
            updates = updates_data
        else:
            typer.echo("Error: Updates must be a JSON object or array", err=True)
            raise typer.Exit(1)

        # Validate updates
        validate_updates(updates)

    except json.JSONDecodeError as e:
        typer.echo(f"Error: Invalid JSON: {e}", err=True)
        raise typer.Exit(1)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    # Get project paths
    paths = get_project_paths(project_id, project_dir)

    typer.echo(f"Applying {len(updates)} update(s) to '{project_id}'...")

    try:
        # Apply updates to HTML preview
        apply_updates(paths.preview_html, updates)

        # Track updates in history
        append_updates(project_id, updates, project_dir)

        typer.echo(f"Applied {len(updates)} update(s)")
        for i, update in enumerate(updates):
            typer.echo(f"  {i + 1}. {update['type']} -> {update['target_element']}")

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error applying updates: {e}", err=True)
        raise typer.Exit(1)
