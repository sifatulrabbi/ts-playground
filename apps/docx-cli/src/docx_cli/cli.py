"""Main CLI application using Typer."""

import typer

from docx_cli.commands import new, update, export, list_projects, info

app = typer.Typer(
    name="docx-cli",
    help="Edit DOCX files via JSON-based update commands, with HTML preview.",
    add_completion=False,
)

# Register commands
app.command(name="new")(new.new_project)
app.command(name="update")(update.update_project)
app.command(name="export")(export.export_project)
app.command(name="list")(list_projects.list_projects)
app.command(name="info")(info.project_info)


if __name__ == "__main__":
    app()
