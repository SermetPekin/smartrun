import nbformat as nbf
from smartrun.options import Options
from smartrun.cli import CLI
from dataclasses import dataclass


@dataclass
class Args:
    script: str
    second: str = None
    venv: bool = False
    no_uv: bool = False
    html: bool = False
    exc: str | None = None
    inc: str | None = None


def helper(args):
    opts = Options(
        script=args.script,
        second=args.second,
        venv=args.venv,
        no_uv=args.no_uv,
        html=args.html,
        exc=args.exc,
        inc=args.inc,
    )
    CLI(opts).router()


def test_generate_notebook(tmp_path):
    import nbformat

    nb = nbformat.v4.new_notebook()
    nb.cells.append(
        nbformat.v4.new_code_cell(
            "import nbformat;from rich import print;print('Hello from notebook')"
        )
    )
    notebook_file = tmp_path / "test.ipynb"
    with open(notebook_file, "w") as f:
        nbformat.write(nb, f)  # ✅ use top-level nbformat.write
    assert notebook_file.exists()
    args = Args(str(notebook_file))
    return helper(args)
