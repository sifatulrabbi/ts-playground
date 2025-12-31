# DOCX-CLI Implementation Plan

A CLI for editing DOCX files via JSON-based update commands, with HTML preview. **All Python.**

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
│       ├── cli.py              # Typer app
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

## CLI Commands

```bash
# Create project from DOCX
python -m docx_cli new --input ./myproposal.docx

# Apply updates
python -m docx_cli update myproposal-docx-project --file updates.json
python -m docx_cli update myproposal-docx-project --code '{"type":"replace",...}'

# Export to DOCX
python -m docx_cli export myproposal-docx-project

# List projects
python -m docx_cli list

# Project info
python -m docx_cli info myproposal-docx-project
```

## Project Storage

```
.docx-projects/
└── myproposal-docx-project/
    ├── project.json      # Metadata
    ├── base.docx         # Original with IDs
    ├── preview.html      # HTML preview
    ├── styles.css
    └── updates.json      # Update history
```

## Implementation Steps

### Phase 1: Project Setup

- [ ] Create pyproject.toml with dependencies (typer, python-docx, lxml, beautifulsoup4)
- [ ] Create package structure (src/docx_cli/)
- [ ] Create **main**.py and cli.py entry points

### Phase 2: Core Utilities

- [ ] Create core/project.py (load, save, list projects)
- [ ] Create styles.py (CSS class mappings)

### Phase 3: New Command

- [ ] Create core/docx_parser.py (extract IDs, inject if missing, generate HTML)
- [ ] Create commands/new.py

### Phase 4: Update Command

- [ ] Create core/html_updater.py (BeautifulSoup operations)
- [ ] Create commands/update.py

### Phase 5: Export Command

- [ ] Create core/docx_writer.py (apply updates to DOCX)
- [ ] Create commands/export.py

### Phase 6: Query Commands

- [ ] Create commands/list.py
- [ ] Create commands/info.py

## ID Mapping

| Element    | DOCX Source  | HTML ID                          |
| ---------- | ------------ | -------------------------------- |
| Paragraph  | `w14:paraId` | `p-{paraId}`                     |
| Table      | Position     | `tbl-{index}`                    |
| Table Row  | Position     | `tr-{tblIdx}-{rowIdx}`           |
| Table Cell | Position     | `td-{tblIdx}-{rowIdx}-{cellIdx}` |
| List Item  | `w14:paraId` | `li-{paraId}`                    |

## Update Types

```json
{"type": "replace", "target_element": "p-12345678", "content": "New text"}
{"type": "insert_before", "target_element": "p-12345678", "content": "New paragraph"}
{"type": "insert_after", "target_element": "p-12345678", "content": "New paragraph"}
{"type": "delete", "target_element": "p-12345678"}
```

## Dependencies

```toml
[project.dependencies]
typer = ">=0.9.0"
python-docx = ">=1.1.0"
lxml = ">=5.0.0"
beautifulsoup4 = ">=4.12.0"
```

## Migration Notes

This replaces the previous hybrid Bun/TypeScript + Python approach with an all-Python solution. The existing TypeScript files in `src/` can be removed.
