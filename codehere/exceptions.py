class CodehereError(Exception):
    """Base exception for codehere."""

    def __init__(self, message: str | None = None):
        self.message = message
        super().__init__(message)


class TagError(CodehereError):
    """Error related to tag processing."""

    def __init__(self, message: str | None = None, *, line: int | None = None, cell: int | None = None):
        self.line = line
        self.cell = cell
        super().__init__(message)


class UnclosedTagError(TagError):
    """A codehere/comment tag was opened but never closed."""


class NoOpenTagError(TagError):
    """A closing tag was found without a matching opening tag."""


class UnsupportedExtensionError(CodehereError):
    """File extension is not supported by codehere."""
