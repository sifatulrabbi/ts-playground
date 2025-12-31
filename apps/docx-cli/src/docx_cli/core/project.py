"""Project management utilities."""

import json
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_PROJECT_DIR = ".docx-projects"


@dataclass
class Project:
    """Project metadata."""

    id: str
    original_path: str
    created_at: str
    updated_at: str
    element_count: int


@dataclass
class ProjectPaths:
    """Paths to project files."""

    root: Path
    project_json: Path
    base_docx: Path
    preview_html: Path
    styles_css: Path
    updates_json: Path


def generate_project_id(filename: str) -> str:
    """Generate a project ID from a filename."""
    base = Path(filename).stem
    sanitized = "".join(c if c.isalnum() else "-" for c in base.lower())
    sanitized = "-".join(filter(None, sanitized.split("-")))
    return f"{sanitized}-docx-project"


def get_projects_dir(project_dir: Optional[str] = None) -> Path:
    """Get the projects directory path."""
    if project_dir:
        return Path(project_dir)
    return Path.cwd() / DEFAULT_PROJECT_DIR


def get_project_paths(project_id: str, project_dir: Optional[str] = None) -> ProjectPaths:
    """Get all paths for a project."""
    projects_dir = get_projects_dir(project_dir)
    root = projects_dir / project_id
    return ProjectPaths(
        root=root,
        project_json=root / "project.json",
        base_docx=root / "base.docx",
        preview_html=root / "preview.html",
        styles_css=root / "styles.css",
        updates_json=root / "updates.json",
    )


def project_exists(project_id: str, project_dir: Optional[str] = None) -> bool:
    """Check if a project exists."""
    paths = get_project_paths(project_id, project_dir)
    return paths.project_json.exists()


def load_project(project_id: str, project_dir: Optional[str] = None) -> Project:
    """Load a project by ID."""
    paths = get_project_paths(project_id, project_dir)
    if not paths.project_json.exists():
        raise ValueError(f"Project not found: {project_id}")

    with open(paths.project_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    return Project(**data)


def save_project(project: Project, project_dir: Optional[str] = None) -> None:
    """Save project metadata."""
    paths = get_project_paths(project.id, project_dir)
    paths.root.mkdir(parents=True, exist_ok=True)

    with open(paths.project_json, "w", encoding="utf-8") as f:
        json.dump(asdict(project), f, indent=2)


def create_project(
    input_path: Path,
    project_id: str,
    element_count: int,
    project_dir: Optional[str] = None,
) -> Project:
    """Create a new project."""
    paths = get_project_paths(project_id, project_dir)

    # Check if project.json exists (project files may already be created by docx_parser)
    if paths.project_json.exists():
        raise ValueError(f"Project already exists: {project_id}")

    paths.root.mkdir(parents=True, exist_ok=True)

    now = datetime.utcnow().isoformat() + "Z"
    project = Project(
        id=project_id,
        original_path=str(input_path.absolute()),
        created_at=now,
        updated_at=now,
        element_count=element_count,
    )

    save_project(project, project_dir)

    # Initialize empty updates file
    with open(paths.updates_json, "w", encoding="utf-8") as f:
        json.dump([], f)

    return project


def list_all_projects(project_dir: Optional[str] = None) -> list[Project]:
    """List all projects."""
    projects_dir = get_projects_dir(project_dir)

    if not projects_dir.exists():
        return []

    projects = []
    for item in projects_dir.iterdir():
        if item.is_dir():
            project_json = item / "project.json"
            if project_json.exists():
                try:
                    with open(project_json, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    projects.append(Project(**data))
                except (json.JSONDecodeError, TypeError):
                    pass

    return sorted(projects, key=lambda p: p.updated_at, reverse=True)


def get_updates(project_id: str, project_dir: Optional[str] = None) -> list[dict]:
    """Get all updates for a project."""
    paths = get_project_paths(project_id, project_dir)

    if not paths.updates_json.exists():
        return []

    with open(paths.updates_json, "r", encoding="utf-8") as f:
        return json.load(f)


def append_updates(
    project_id: str,
    updates: list[dict],
    project_dir: Optional[str] = None,
) -> None:
    """Append updates to a project's update history."""
    paths = get_project_paths(project_id, project_dir)

    existing = get_updates(project_id, project_dir)

    # Add timestamp to each update
    now = datetime.utcnow().isoformat() + "Z"
    for update in updates:
        update["applied_at"] = now

    existing.extend(updates)

    with open(paths.updates_json, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    # Update project's updated_at timestamp
    project = load_project(project_id, project_dir)
    project.updated_at = now
    save_project(project, project_dir)


def delete_project(project_id: str, project_dir: Optional[str] = None) -> None:
    """Delete a project."""
    paths = get_project_paths(project_id, project_dir)

    if paths.root.exists():
        shutil.rmtree(paths.root)
