"""
Document parser.

Responsibilities
----------------
- Parse supported knowledge files.
- Convert raw files into Document objects.

Supported formats
-----------------
- Markdown (.md)

Future formats
--------------
- PDF (.pdf)
- Plain text (.txt)
- DOCX (.docx)
"""

from __future__ import annotations

from pathlib import Path

from app.retrieval.schema import Document


class Parser:
    """
    Parse knowledge files into Document objects.
    """

    @property
    def supported_extensions(self) -> set[str]:
        return {
            ".md",
        }

    def parse(
        self,
        path: Path,
    ) -> Document:
        """
        Parse a knowledge file.

        Parameters
        ----------
        path:
            Path to the knowledge file.

        Returns
        -------
        Document
        """

        suffix = path.suffix.lower()

        if suffix == ".md":
            return self._parse_markdown(path)

        raise ValueError(
            f"Unsupported file type: {suffix}"
        )

    def _parse_markdown(
        self,
        path: Path,
    ) -> Document:
        """
        Parse a Markdown document.
        """

        text = path.read_text(
            encoding="utf-8"
        )

        return Document(
            source=path,
            text=text,
            metadata={},
        )