"""HTML manipulation using BeautifulSoup."""

import secrets
from pathlib import Path
from typing import Literal

from bs4 import BeautifulSoup, Tag


UpdateType = Literal["replace", "insert_before", "insert_after", "delete"]


def generate_element_id(tag_name: str) -> str:
    """Generate a unique element ID."""
    suffix = secrets.token_hex(4).upper()
    return f"{tag_name}-{suffix}"


def load_html(html_path: Path) -> BeautifulSoup:
    """Load HTML file into BeautifulSoup."""
    content = html_path.read_text(encoding="utf-8")
    return BeautifulSoup(content, "html.parser")


def save_html(soup: BeautifulSoup, html_path: Path) -> None:
    """Save BeautifulSoup to HTML file."""
    html_path.write_text(str(soup), encoding="utf-8")


def find_element_by_id(soup: BeautifulSoup, element_id: str) -> Tag:
    """Find element by ID, raise error if not found."""
    element = soup.find(id=element_id)
    if element is None:
        raise ValueError(f"Element not found: {element_id}")
    if not isinstance(element, Tag):
        raise ValueError(f"Element is not a tag: {element_id}")
    return element


def assign_ids_to_fragment(soup: BeautifulSoup, fragment: BeautifulSoup) -> None:
    """Assign unique IDs to all elements in a fragment that lack IDs."""
    for tag in fragment.find_all(True):  # Find all tags
        if isinstance(tag, Tag) and not tag.get("id"):
            tag_name = tag.name
            if tag_name in ("p", "h1", "h2", "h3", "h4", "h5", "h6"):
                tag["id"] = generate_element_id("p")
            elif tag_name == "li":
                tag["id"] = generate_element_id("li")
            elif tag_name == "table":
                tag["id"] = generate_element_id("tbl")
            elif tag_name == "tr":
                tag["id"] = generate_element_id("tr")
            elif tag_name in ("td", "th"):
                tag["id"] = generate_element_id("td")
            elif tag_name in ("ul", "ol"):
                tag["id"] = generate_element_id("list")


def parse_content(content: str) -> BeautifulSoup:
    """Parse HTML content string into BeautifulSoup fragment."""
    return BeautifulSoup(content, "html.parser")


def apply_replace(soup: BeautifulSoup, target_id: str, content: str) -> None:
    """Replace an element's content."""
    target = find_element_by_id(soup, target_id)

    # Parse new content
    fragment = parse_content(content)

    # Assign IDs to new elements
    assign_ids_to_fragment(soup, fragment)

    # Replace the target's content
    target.clear()
    for child in list(fragment.children):
        if isinstance(child, str):
            target.append(child)
        else:
            target.append(child.extract())


def apply_insert_before(soup: BeautifulSoup, target_id: str, content: str) -> None:
    """Insert content before an element."""
    target = find_element_by_id(soup, target_id)

    # Parse new content
    fragment = parse_content(content)

    # Assign IDs to new elements
    assign_ids_to_fragment(soup, fragment)

    # Insert each element before target
    for child in reversed(list(fragment.children)):
        if isinstance(child, Tag):
            target.insert_before(child.extract())
        elif isinstance(child, str) and child.strip():
            target.insert_before(child)


def apply_insert_after(soup: BeautifulSoup, target_id: str, content: str) -> None:
    """Insert content after an element."""
    target = find_element_by_id(soup, target_id)

    # Parse new content
    fragment = parse_content(content)

    # Assign IDs to new elements
    assign_ids_to_fragment(soup, fragment)

    # Insert each element after target
    for child in list(fragment.children):
        if isinstance(child, Tag):
            target.insert_after(child.extract())
        elif isinstance(child, str) and child.strip():
            target.insert_after(child)


def apply_delete(soup: BeautifulSoup, target_id: str) -> None:
    """Delete an element."""
    target = find_element_by_id(soup, target_id)
    target.decompose()


def apply_update(soup: BeautifulSoup, update: dict) -> None:
    """Apply a single update to the HTML."""
    update_type: UpdateType = update["type"]
    target_id: str = update["target_element"]
    content: str = update.get("content", "")

    if update_type == "replace":
        apply_replace(soup, target_id, content)
    elif update_type == "insert_before":
        apply_insert_before(soup, target_id, content)
    elif update_type == "insert_after":
        apply_insert_after(soup, target_id, content)
    elif update_type == "delete":
        apply_delete(soup, target_id)
    else:
        raise ValueError(f"Unknown update type: {update_type}")


def apply_updates(html_path: Path, updates: list[dict]) -> None:
    """Apply multiple updates to an HTML file."""
    soup = load_html(html_path)

    for update in updates:
        apply_update(soup, update)

    save_html(soup, html_path)


def validate_update(update: dict) -> None:
    """Validate an update command structure."""
    if not isinstance(update, dict):
        raise ValueError(f"Update must be a dict, got {type(update)}")

    if "type" not in update:
        raise ValueError("Update missing 'type' field")

    if "target_element" not in update:
        raise ValueError("Update missing 'target_element' field")

    update_type = update["type"]
    valid_types = ("replace", "insert_before", "insert_after", "delete")

    if update_type not in valid_types:
        raise ValueError(f"Invalid update type: {update_type}. Must be one of {valid_types}")

    if update_type != "delete" and "content" not in update:
        raise ValueError(f"Update type '{update_type}' requires 'content' field")


def validate_updates(updates: list[dict]) -> None:
    """Validate a list of update commands."""
    if not isinstance(updates, list):
        raise ValueError(f"Updates must be a list, got {type(updates)}")

    for i, update in enumerate(updates):
        try:
            validate_update(update)
        except ValueError as e:
            raise ValueError(f"Invalid update at index {i}: {e}")
