"""Read and write YAML frontmatter in markdown files."""

import os

import frontmatter


def read_frontmatter(filepath: str) -> tuple[dict, str]:
    """Read a markdown file and return (metadata_dict, body_string).

    Returns ({}, "") if the file doesn't exist.
    """
    if not os.path.isfile(filepath):
        return {}, ""

    post = frontmatter.load(filepath)
    return dict(post.metadata), post.content


def write_frontmatter(filepath: str, metadata: dict, body: str) -> None:
    """Write a markdown file with YAML frontmatter and body content.

    Creates parent directories if they don't exist.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    post = frontmatter.Post(body, **metadata)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))
        f.write("\n")


def update_frontmatter(filepath: str, updates: dict) -> None:
    """Read existing file, merge updates into frontmatter, write back."""
    metadata, body = read_frontmatter(filepath)
    metadata.update(updates)
    write_frontmatter(filepath, metadata, body)
