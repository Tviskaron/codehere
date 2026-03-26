"""Codehere — prepare annotated code for teaching."""

__version__ = "0.2.1"

from codehere.converter import Converter
from codehere.exceptions import (
    CodehereError,
    NoOpenTagError,
    TagError,
    UnclosedTagError,
    UnsupportedExtensionError,
)
from codehere.processors import process_file
from codehere.utils import get_outfile_path


def _detect_notebook_path() -> str | None:
    """Try to auto-detect the current notebook path (Colab, VS Code, Jupyter)."""
    from pathlib import Path

    # VS Code stores the notebook path in IPython's user namespace
    try:
        ip = __import__("IPython").get_ipython()
        if ip:
            path = ip.user_ns.get("__vsc_ipynb_file__")
            if path and Path(path).exists():
                return str(path)
    except Exception:
        pass

    # Google Colab: fetch notebook content via internal API and save to a temp file
    try:
        from google.colab import _message
        import json as _json
        import tempfile

        response = _message.blocking_request("get_ipynb", timeout_sec=10)
        if response and "ipynb" in response:
            tmp = tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False, mode="w")
            _json.dump(response["ipynb"], tmp)
            tmp.close()
            return tmp.name
    except Exception:
        pass

    # Jupyter: try matching kernel connection file to running server sessions
    try:
        import ipykernel
        import json as _json
        from urllib.request import urlopen

        connection_file = Path(ipykernel.get_connection_file()).stem
        kernel_id = connection_file.split("-", 1)[1].split(".")[0]

        for mod_name in ("jupyter_server.serverapp", "notebook.notebookapp"):
            try:
                mod = __import__(mod_name, fromlist=["list_running_servers"])
                for srv in mod.list_running_servers():
                    url = srv["url"] + "api/sessions"
                    if srv.get("token"):
                        url += "?token=" + srv["token"]
                    sessions = _json.loads(urlopen(url).read())
                    for sess in sessions:
                        if sess["kernel"]["id"] == kernel_id:
                            nb_path = sess.get("notebook", {}).get("path") or sess.get("path")
                            if nb_path:
                                full = Path(srv.get("notebook_dir", srv.get("root_dir", ""))) / nb_path
                                if full.exists():
                                    return str(full)
            except Exception:
                continue
    except Exception:
        pass

    # Fallback: single .ipynb in current directory
    notebooks = list(Path.cwd().glob("*.ipynb"))
    if len(notebooks) == 1:
        return str(notebooks[0])

    return None


def convert(
    file: str | None = None,
    outfile: str | None = None,
    solution: bool = False,
    clear: bool = False,
    replacement: str = " Your code here ",
) -> None:
    """Backward-compatible entry point."""
    if file is None:
        file = _detect_notebook_path()
    if file is None:
        raise FileNotFoundError("Cannot determine input file location. Please specify it directly.")
    if outfile is None:
        outfile = get_outfile_path(file, solution=solution)
    process_file(file, outfile, solution=solution, clear=clear, replacement=replacement)
    print("Saved in:", outfile)


__all__ = [
    "Converter",
    "CodehereError",
    "NoOpenTagError",
    "TagError",
    "UnclosedTagError",
    "UnsupportedExtensionError",
    "convert",
    "get_outfile_path",
    "process_file",
]
