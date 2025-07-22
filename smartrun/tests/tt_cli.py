from typer.testing import CliRunner
from smartrun.cli import main as app

runner = CliRunner()


def test_app1(capsys):
    with capsys.disabled():
        result = runner.invoke(app, ["somefile.py"])
        print(result)


def tt_app2(capsys):
    with capsys.disabled():
        result = runner.invoke(
            app,
            [
                "somefile.py",
                "--html",
            ],
        )
        print(result)
        # assert result.exit_code == 0
        # assert "Hello Camila" in result.output
        # assert "Let's have a coffee in Berlin" in result.output
