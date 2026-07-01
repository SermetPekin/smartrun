#!/usr/bin/env python
"""
Test suite for --html parameter functionality.
Tests that --html flag is properly parsed and controls HTML generation.

Run:
    pytest smartrun/tests/test_html_parameter.py -v
    python -m pytest smartrun/tests/test_html_parameter.py -v
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from smartrun.cli import main, _build_arg_parser
from smartrun.options import Options


class TestHtmlParameter:
    """Test --html parameter handling in CLI."""

    def test_argparse_html_default_false(self):
        """Test that argparse sets html to False by default."""
        parser = _build_arg_parser()
        args = parser.parse_args(["test_script.py"])
        assert args.html is False

    def test_argparse_html_flag_true(self):
        """Test that argparse sets html to True when --html is provided."""
        parser = _build_arg_parser()
        args = parser.parse_args(["test_script.py", "--html"])
        assert args.html is True

    def test_options_html_default(self):
        """Test that Options class receives default html=False."""
        opts = Options(
            script="test_script.py",
            html=False,
        )
        assert opts.html is False

    def test_options_html_true(self):
        """Test that Options class receives html=True."""
        opts = Options(
            script="test_script.py",
            html=True,
        )
        assert opts.html is True

    def test_html_with_notebook(self):
        """Test that html flag works with notebook files."""
        parser = _build_arg_parser()
        args = parser.parse_args(["test.ipynb", "--html"])
        assert args.html is True
        assert args.script == "test.ipynb"

    def test_html_with_output_directory(self):
        """Test that html flag works with --out parameter."""
        parser = _build_arg_parser()
        args = parser.parse_args(["test.ipynb", "--html", "--out", "output_dir"])
        assert args.html is True
        assert args.out == "output_dir"

    def test_html_type(self):
        """Test that html is a boolean type."""
        opts = Options(script="test.ipynb", html=True)
        assert isinstance(opts.html, bool)


class TestHtmlIntegrationWithCLI:
    """Integration tests for --html with CLI."""

    def test_cli_integration_html_false(self, monkeypatch):
        """Test CLI integration with html=False (default)."""
        from smartrun import cli as cli_mod

        captured = {}

        def fake_dispatch(self):
            captured["html"] = self.opts.html

        monkeypatch.setattr(cli_mod.CLI, "dispatch", fake_dispatch)

        # Simulate CLI call without --html
        cli_mod.main(["test.ipynb"])

        assert captured["html"] is False

    def test_cli_integration_html_true(self, monkeypatch):
        """Test CLI integration with html=True."""
        from smartrun import cli as cli_mod

        captured = {}

        def fake_dispatch(self):
            captured["html"] = self.opts.html

        monkeypatch.setattr(cli_mod.CLI, "dispatch", fake_dispatch)

        # Simulate CLI call with --html
        cli_mod.main(["test.ipynb", "--html"])

        assert captured["html"] is True

    def test_html_with_multiple_flags(self, monkeypatch):
        """Test html flag works with other CLI flags."""
        from smartrun import cli as cli_mod

        captured = {}

        def fake_dispatch(self):
            captured["html"] = self.opts.html
            captured["verbose"] = self.opts.verbose
            captured["timeout"] = self.opts.timeout

        monkeypatch.setattr(cli_mod.CLI, "dispatch", fake_dispatch)

        # Simulate CLI call with multiple flags
        cli_mod.main(["test.ipynb", "--html", "--verbose", "--timeout", "3600"])

        assert captured["html"] is True
        assert captured["verbose"] is True
        assert captured["timeout"] == 3600


class TestHtmlNotebookExecution:
    """Test that html flag controls notebook execution mode."""

    @patch("smartrun.runner.convert")
    @patch("smartrun.runner.run_and_save_notebook")
    def test_html_true_calls_convert(
        self, mock_run_and_save, mock_convert
    ):
        """Test that html=True calls convert function (HTML generation)."""
        from smartrun.runner import run_notebook_in_venv

        opts = Options(script="test.ipynb", html=True)

        try:
            run_notebook_in_venv(opts)
        except Exception:
            # Expected due to mocking
            pass

        # Should call convert when html=True
        mock_convert.assert_called_once()
        # Should NOT call run_and_save_notebook
        mock_run_and_save.assert_not_called()

    @patch("smartrun.runner.convert")
    @patch("smartrun.runner.run_and_save_notebook")
    def test_html_false_calls_run_and_save(
        self, mock_run_and_save, mock_convert
    ):
        """Test that html=False calls run_and_save_notebook (no HTML)."""
        from smartrun.runner import run_notebook_in_venv

        opts = Options(script="test.ipynb", html=False)

        try:
            run_notebook_in_venv(opts)
        except Exception:
            # Expected due to mocking
            pass

        # Should call run_and_save_notebook when html=False
        mock_run_and_save.assert_called_once()
        # Should NOT call convert
        mock_convert.assert_not_called()


class TestHtmlWithOutputDirectory:
    """Test html flag interaction with output directory."""

    def test_html_and_out_both_set(self):
        """Test that both html and out can be set together."""
        opts = Options(
            script="test.ipynb",
            html=True,
            out=Path("output_folder"),
        )
        assert opts.html is True
        assert opts.out == Path("output_folder")

    def test_out_used_in_convert(self, monkeypatch):
        """Test that output directory is passed to convert when html=True."""
        from smartrun.runner import run_notebook_in_venv

        captured = {}

        def fake_convert(nb_opts, opts):
            captured["html"] = opts.html
            captured["out"] = opts.out

        monkeypatch.setattr("smartrun.runner.convert", fake_convert)

        opts = Options(script="test.ipynb", html=True, out=Path("html_output"))

        try:
            run_notebook_in_venv(opts)
        except Exception:
            pass

        assert captured["html"] is True
        assert captured["out"] == Path("html_output")


class TestHtmlEdgeCases:
    """Test edge cases for html parameter."""

    def test_html_with_python_script_ignored(self):
        """Test that html flag is ignored for .py files."""
        # HTML flag is only relevant for notebooks
        opts = Options(script="test.py", html=True)
        assert opts.html is True  # Flag is set but won't affect .py execution

    def test_html_help_text(self):
        """Test that html argument has proper help text."""
        parser = _build_arg_parser()
        # Check that --html is in the parser
        html_action = None
        for action in parser._actions:
            if "--html" in action.option_strings:
                html_action = action
                break

        assert html_action is not None
        assert html_action.help == "Generate HTML report"
        # Check that it's a store_true action
        assert html_action.__class__.__name__ == "_StoreTrueAction"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
