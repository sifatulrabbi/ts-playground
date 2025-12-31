# DOCX-CLI All-Python Design

## Overview

A CLI for editing DOCX files via JSON-based update commands, with HTML preview. Built entirely in Python.

## Technology Stack

- **Typer** - CLI framework
- **python-docx** - DOCX read/write
- **lxml** - XML parsing for ID extraction/injection
- **BeautifulSoup** - HTML manipulation

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   docx-cli (Typer)                      │
├─────────────────────────────────────────────────────────┤
│  new         │  update       │  export      │  list/info│
│  (init proj) │  (track edits)│  (apply)     │  (query)  │
└──────┬───────┴───────┬───────┴──────┬───────┴───────────┘
       │               │              │
       ▼               ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ python-docx │ │BeautifulSoup│ │ python-docx │
│ + lxml      │ │ (HTML DOM)  │ │ (apply ops) │
└─────────────┘ └─────────────┘ └─────────────┘
```

## Package Structure

```
apps/docx-cli/
├── pyproject.toml
├── src/
│   └── docx_cli/
│       ├── __init__.py
│       ├── __main__.py         # Entry: python -m docx_cli
│       ├── cli.py              # Typer app with all commands
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── new.py
│       │   ├── update.py
│       │   ├── export.py
│       │   ├── list.py
│       │   └── info.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── project.py      # Project management
│       │   ├── docx_parser.py  # DOCX → HTML with ID extraction
│       │   ├── html_updater.py # BeautifulSoup operations
│       │   └── docx_writer.py  # Apply updates to DOCX
│       └── styles.py
└── scripts/
    └── setup.sh
```

## Project Storage

Location: `.docx-projects/<project-id>/`

```
.docx-projects/
└── myproposal-docx-project/
    ├── project.json      # Metadata
    ├── base.docx         # Original DOCX with IDs injected
    ├── preview.html      # HTML preview
    ├── styles.css        # CSS
    └── updates.json      # Update history
```

### project.json

```json
{
  "id": "myproposal-docx-project",
  "original_path": "/absolute/path/to/myproposal.docx",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:20:00Z",
  "element_count": 47
}
```

### updates.json

```json
[
  {"type": "replace", "target_element": "p-12345678", "content": "New text", "applied_at": "..."},
  {"type": "insert_after", "target_element": "p-12345678", "content": "Added paragraph", "applied_at": "..."}
]
```

## CLI Commands

### new

```bash
python -m docx_cli new --input ./myproposal.docx [--name custom-name]
```

Creates project, extracts/injects IDs, generates HTML preview.

### update

```bash
python -m docx_cli update <project-id> --file updates.json
python -m docx_cli update <project-id> --code '{"type":"replace",...}'
```

Applies updates to HTML preview, tracks in updates.json.

### export

```bash
python -m docx_cli export <project-id> [--output ./output.docx]
```

Applies all tracked updates to DOCX copy, outputs new file.

### list

```bash
python -m docx_cli list
```

Lists all projects in `.docx-projects/`.

### info

```bash
python -m docx_cli info <project-id>
```

Shows project details and update history.

## ID Mapping

| Element | DOCX Source | HTML ID |
|---------|-------------|---------|
| Paragraph | `w14:paraId` | `p-{paraId}` |
| Table | Position index | `tbl-{index}` |
| Table Row | Position | `tr-{tblIdx}-{rowIdx}` |
| Table Cell | Position | `td-{tblIdx}-{rowIdx}-{cellIdx}` |
| List Item | Paragraph's `paraId` | `li-{paraId}` |

If DOCX lacks `w14:paraId` attributes, they are generated and injected.

## Update Types

```python
UpdateCommand = {
    "type": "replace" | "insert_before" | "insert_after" | "delete",
    "target_element": str,  # Element ID
    "content": str,         # New content (not for delete)
}
```

## Dependencies

```toml
[project]
dependencies = [
    "typer>=0.9.0",
    "python-docx>=1.1.0",
    "lxml>=5.0.0",
    "beautifulsoup4>=4.12.0",
]
```
