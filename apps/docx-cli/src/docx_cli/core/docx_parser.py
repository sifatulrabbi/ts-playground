"""DOCX parsing and HTML generation with ID mapping."""

import secrets
import zipfile
from pathlib import Path
from typing import Optional

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from lxml import etree

from docx_cli.styles import get_css_class, get_default_css

# XML namespaces
NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
}


def generate_para_id() -> str:
    """Generate an 8-character hex paragraph ID."""
    return secrets.token_hex(4).upper()


def extract_paragraph_ids(docx_path: Path) -> dict[int, str]:
    """
    Extract existing paragraph IDs from DOCX.
    Returns dict mapping paragraph index to paraId.
    """
    para_ids = {}

    with zipfile.ZipFile(docx_path, "r") as zf:
        if "word/document.xml" not in zf.namelist():
            return para_ids

        xml_content = zf.read("word/document.xml")
        tree = etree.fromstring(xml_content)

        paragraphs = tree.findall(".//w:p", namespaces=NAMESPACES)
        for idx, p in enumerate(paragraphs):
            para_id = p.get(f"{{{NAMESPACES['w14']}}}paraId")
            if para_id:
                para_ids[idx] = para_id

    return para_ids


def inject_paragraph_ids(input_path: Path, output_path: Path) -> dict[int, str]:
    """
    Inject paragraph IDs into DOCX where missing.
    Returns dict mapping paragraph index to paraId.
    """
    para_ids = {}

    # Read and modify document.xml
    with zipfile.ZipFile(input_path, "r") as zin:
        xml_content = zin.read("word/document.xml")
        tree = etree.fromstring(xml_content)

        paragraphs = tree.findall(".//w:p", namespaces=NAMESPACES)
        for idx, p in enumerate(paragraphs):
            para_id = p.get(f"{{{NAMESPACES['w14']}}}paraId")
            if not para_id:
                para_id = generate_para_id()
                p.set(f"{{{NAMESPACES['w14']}}}paraId", para_id)
                # Also add textId for completeness
                text_id = p.get(f"{{{NAMESPACES['w14']}}}textId")
                if not text_id:
                    p.set(f"{{{NAMESPACES['w14']}}}textId", generate_para_id())
            para_ids[idx] = para_id

        modified_xml = etree.tostring(tree, xml_declaration=True, encoding="UTF-8")

        # Write new DOCX with modified XML
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                if item == "word/document.xml":
                    zout.writestr(item, modified_xml)
                else:
                    zout.writestr(item, zin.read(item))

    return para_ids


class DocxToHtmlConverter:
    """Converts DOCX to HTML with ID mapping from DOCX paragraph IDs."""

    def __init__(self, para_ids: dict[int, str]):
        self.para_ids = para_ids
        self.para_index = 0
        self.table_index = 0

    def get_para_id(self) -> str:
        """Get the paragraph ID for current index and increment."""
        para_id = self.para_ids.get(self.para_index, generate_para_id())
        self.para_index += 1
        return para_id

    def convert_run(self, run) -> str:
        """Convert a run (text with formatting) to HTML."""
        text = run.text
        if not text:
            return ""

        # Escape HTML entities
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Apply inline formatting
        if run.bold:
            text = f"<strong>{text}</strong>"
        if run.italic:
            text = f"<em>{text}</em>"
        if run.underline:
            text = f"<u>{text}</u>"

        return text

    def convert_paragraph(self, paragraph: Paragraph) -> tuple[str, str]:
        """
        Convert a paragraph to HTML.
        Returns (html, element_type) where element_type is 'paragraph' or 'list-item'.
        """
        content_parts = [self.convert_run(run) for run in paragraph.runs]
        content = "".join(content_parts)

        if not content.strip():
            # Still consume the para ID for empty paragraphs
            self.get_para_id()
            return "", "paragraph"

        style_name = paragraph.style.name if paragraph.style else None
        css_class = get_css_class(style_name)
        para_id = self.get_para_id()

        # Check for headings
        if style_name and style_name.startswith("Heading"):
            level = style_name.split()[-1]
            try:
                level_num = int(level)
                if 1 <= level_num <= 6:
                    tag = f"h{level_num}"
                    return (
                        f'<{tag} id="p-{para_id}" class="{css_class}">{content}</{tag}>',
                        "paragraph",
                    )
            except ValueError:
                pass

        # Check for list items
        if paragraph._element.pPr is not None:
            numPr = paragraph._element.pPr.numPr
            if numPr is not None:
                return f'<li id="li-{para_id}" class="list-item">{content}</li>', "list-item"

        # Regular paragraph
        return f'<p id="p-{para_id}" class="{css_class}">{content}</p>', "paragraph"

    def convert_table(self, table: Table) -> str:
        """Convert a table to HTML."""
        rows_html = []
        table_idx = self.table_index

        for row_idx, row in enumerate(table.rows):
            cells_html = []
            for cell_idx, cell in enumerate(row.cells):
                cell_content = []
                for para in cell.paragraphs:
                    para_text = "".join(run.text for run in para.runs)
                    if para_text.strip():
                        # Escape HTML
                        para_text = (
                            para_text.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;")
                        )
                        cell_content.append(para_text)
                content = "<br>".join(cell_content)

                tag = "th" if row_idx == 0 else "td"
                cell_id = f"td-{table_idx}-{row_idx}-{cell_idx}"
                cells_html.append(f'<{tag} id="{cell_id}">{content}</{tag}>')

            row_id = f"tr-{table_idx}-{row_idx}"
            rows_html.append(f'<tr id="{row_id}">{"".join(cells_html)}</tr>')

        table_id = f"tbl-{table_idx}"
        self.table_index += 1
        return f'<table id="{table_id}" class="table">{"".join(rows_html)}</table>'

    def convert(self, docx_path: Path) -> tuple[str, str, int]:
        """
        Convert a DOCX file to HTML.
        Returns (html_content, css_content, element_count).
        """
        doc = Document(str(docx_path))

        body_content = []
        list_items: list[str] = []
        list_type: Optional[str] = None
        element_count = 0

        def flush_list():
            nonlocal list_items, list_type, element_count
            if list_items:
                tag = "ul" if list_type == "bullet" else "ol"
                css_class = "bullet-list" if list_type == "bullet" else "numbered-list"
                list_id = f"list-{element_count}"
                content = "".join(list_items)
                body_content.append(f'<{tag} id="{list_id}" class="{css_class}">{content}</{tag}>')
                element_count += 1
                list_items = []
                list_type = None

        for element in doc.element.body:
            if element.tag.endswith("}p"):
                para = Paragraph(element, doc)
                html, elem_type = self.convert_paragraph(para)

                if html.startswith("<li"):
                    if list_type is None:
                        list_type = "bullet"
                    list_items.append(html)
                    element_count += 1
                else:
                    flush_list()
                    if html:
                        body_content.append(html)
                        element_count += 1

            elif element.tag.endswith("}tbl"):
                flush_list()
                table = Table(element, doc)
                body_content.append(self.convert_table(table))
                element_count += 1

        flush_list()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="styles.css">
    <title>Document Preview</title>
</head>
<body>
{chr(10).join(body_content)}
</body>
</html>"""

        return html, get_default_css(), element_count


def parse_docx_to_project(
    input_path: Path,
    base_docx_path: Path,
    preview_html_path: Path,
    styles_css_path: Path,
) -> int:
    """
    Parse DOCX, inject IDs if needed, generate HTML preview.
    Returns element count.
    """
    # Ensure output directory exists
    base_docx_path.parent.mkdir(parents=True, exist_ok=True)

    # Check for existing IDs
    existing_ids = extract_paragraph_ids(input_path)

    # Inject IDs where missing and create base.docx
    para_ids = inject_paragraph_ids(input_path, base_docx_path)

    # Convert to HTML using the IDs
    converter = DocxToHtmlConverter(para_ids)
    html, css, element_count = converter.convert(base_docx_path)

    # Write output files
    preview_html_path.write_text(html, encoding="utf-8")
    styles_css_path.write_text(css, encoding="utf-8")

    return element_count
