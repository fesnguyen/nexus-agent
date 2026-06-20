from pathlib import Path

from app.tools.base import BaseTool
from app.tools.schemas.tool_schemas import FileReaderInput


class FileReaderTool(BaseTool):
    """
    Purpose:
        Read files from the Nexus workspace.

    Why:
        Provides a controlled mechanism for accessing local files.

    Security:
        Prevents path traversal attacks by restricting access
        to files inside the project workspace.
    """

    name = "file_reader"

    description = (
        "Read the contents of a file from the workspace."
    )

    input_schema = FileReaderInput

    def __init__(self, workspace_root: Path | None = None):
        """
        Args:
            workspace_root:
                Base directory the tool is allowed to read from.
                Defaults to current project root.
        """

        self.workspace_root = (
            workspace_root.resolve()
            if workspace_root
            else Path.cwd()
            .resolve() # absolute canonical path
        )

    def run(self, tool_input: FileReaderInput) -> str:
        """
        Read a file from the workspace.

        Args:
            tool_input:
                FileReaderInput schema.

        Returns:
            File contents as a string.

        Raises:
            ValueError:
                Invalid path.

            FileNotFoundError:
                File does not exist.
        """

        requested_path = (
            self.workspace_root / tool_input.path
        ).resolve()

        # Prevent:
        # ../../../etc/passwd
        # ../../.env
        if not str(requested_path).startswith(
            str(self.workspace_root)
        ):
            raise ValueError(
                "Access outside workspace is not allowed."
            )

        if not requested_path.exists():
            raise FileNotFoundError(
                f"File not found: {tool_input.path}"
            )

        if not requested_path.is_file():
            raise ValueError(
                f"Not a file: {tool_input.path}"
            )

        return requested_path.read_text(
            encoding="utf-8"
        )