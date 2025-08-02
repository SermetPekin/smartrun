import os
import datetime
import warnings
from typing import Optional, Any
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# Optional Jupyter dependencies
nbformat: Optional[Any] = None
HTMLExporter: Optional[Any] = None
ExecutePreprocessor: Optional[Any] = None
try:
    import nbformat
    from nbconvert import HTMLExporter
    from nbconvert.preprocessors import ExecutePreprocessor

    JUPYTER_AVAILABLE = True
except ImportError:
    JUPYTER_AVAILABLE = False
    warnings.warn(
        "nbconvert or nbformat package is missing. "
        "Install with 'pip install nbconvert nbformat' to enable Jupyter notebook functionality.",
        ImportWarning,
        stacklevel=2,
    )


def is_jupyter_available() -> bool:
    """Check if Jupyter dependencies are available."""
    return JUPYTER_AVAILABLE


def require_jupyter():
    """Raise ImportError if Jupyter dependencies are not available."""
    if not JUPYTER_AVAILABLE:
        raise ImportError(
            "Jupyter dependencies (nbconvert, nbformat) are required for this operation. "
            "Install with: pip install nbconvert nbformat"
        )


def default_name_format(options) -> str:
    """
    default name format for output files
    """
    day = datetime.date.today().isoformat()
    outfile = os.path.join(options.output_dir, f"{options.out_name}_{day}.html")
    return outfile


@dataclass
class NBOptions:
    """
    NBOptions
    """

    file_name: Path | str = "daily_report.ipynb"
    workspace: Path | str = "."
    output_dir: Path | str = "html_outputs"
    out_name: str = "daily_report"
    renderer: str = "notebook"
    kernel: str = "python"
    timeout: int = 600
    out_name_func: Callable = None

    def __post_init__(self):
        if ".ipynb" not in str(self.file_name):
            self.file_name = str(self.file_name) + ".ipynb"
        self.file_name = Path(self.file_name)
        if self.out_name_func is None:
            self.out_name_func = default_name_format

    def __str__(self):
        t = f"""    
    NBOptions 
   ................
    file_name : {self.file_name }   
    output_dir    : {self.output_dir }   
    renderer : {self.renderer}
    kernel : {self.kernel }  
    timeout : {self.timeout}
     
"""
        return t


def run_and_save_notebook(nb_opts: NBOptions, output_suffix="_executed"):
    notebook_path = Path(nb_opts.file_name)
    nb = nbformat.read(notebook_path.open(encoding="utf-8"), as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    ep.preprocess(nb, {"metadata": {"path": notebook_path.parent}})
    output_path = notebook_path.with_name(notebook_path.stem + output_suffix + ".ipynb")
    nbformat.write(nb, output_path.open("w", encoding="utf-8"))
    return output_path


def change_ws(ws: str | Path) -> None:
    if str(ws) == ".":
        return
    project_root = os.path.abspath(os.path.join(os.getcwd(), ws))
    os.chdir(project_root)


def convert(options: NBOptions) -> None:
    """convert"""
    DEFAULT_RENDERER = (
        options.renderer
    )  #  "notebook"  #   "plotly_mimetype"  # "iframe"  #  "plotly_mimetype" #
    # pio.renderers.default = DEFAULT_RENDERER  #
    os.environ["PLOTLY_RENDERER"] = DEFAULT_RENDERER
    change_ws(options.workspace)
    # --- paths -------------------------------------------------
    NOTEBOOK = options.file_name
    OUTPUT_DIR = options.output_dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # --- read notebook ----------------------------------------
    with open(NOTEBOOK, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    # --- run notebook -----------------------------------------
    # Change kernel_name if you use a different kernel
    ep = ExecutePreprocessor(timeout=options.timeout, kernel_name=options.kernel)
    ep.preprocess(nb, {"metadata": {"path": os.path.dirname(NOTEBOOK) or "."}})
    # --- export to HTML ---------------------------------------
    html_exporter = HTMLExporter(template_name="lab")
    body, _ = html_exporter.from_notebook_node(nb)
    outfile = options.out_name_func(options)
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"✅ Saved executed notebook as {outfile}")
