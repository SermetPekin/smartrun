#!/usr/bin/env python
"""
Test suite for --timeout parameter functionality.
Tests that timeout is properly parsed from CLI arguments and passed to Options class.

Run:
    pytest smartrun/tests/test_timeout.py -v
    python -m pytest smartrun/tests/test_timeout.py::test_timeout_default -v
"""
import pytest
from smartrun.cli import main, _build_arg_parser
from smartrun.options import Options
from pathlib import Path


class TestTimeoutParameter:
    """Test suite for timeout parameter handling."""

    def test_argparse_timeout_default(self):
        """Test that argparse sets default timeout to 1200."""
        parser = _build_arg_parser()
        args = parser.parse_args(["test_script.py"])
        assert args.timeout == 1200

    def test_argparse_timeout_custom_value(self):
        """Test that argparse accepts custom timeout value."""
        parser = _build_arg_parser()
        args = parser.parse_args(["test_script.py", "--timeout", "600"])
        assert args.timeout == 600
        assert isinstance(args.timeout, int)

    def test_argparse_timeout_type_conversion(self):
        """Test that timeout is converted to integer."""
        parser = _build_arg_parser()
        args = parser.parse_args(["test_script.py", "--timeout", "3600"])
        assert args.timeout == 3600
        assert type(args.timeout) == int

    def test_options_timeout_default(self):
        """Test that Options class receives default timeout value."""
        opts = Options(
            script="test_script.py",
            second=None,
            venv=False,
            verbose=False,
            no_uv=False,
            html=False,
            exc=None,
            inc=None,
            version=False,
            help=False,
            out=None,
            timeout=1200,
        )
        assert opts.timeout == 1200

    def test_options_timeout_custom(self):
        """Test that Options class receives custom timeout value."""
        opts = Options(
            script="test_script.py",
            second=None,
            venv=False,
            verbose=False,
            no_uv=False,
            html=False,
            exc=None,
            inc=None,
            version=False,
            help=False,
            out=None,
            timeout=3000,
        )
        assert opts.timeout == 3000

    def test_options_timeout_type(self):
        """Test that timeout in Options is an integer."""
        opts = Options(
            script="test_script.py",
            timeout=1500,
        )
        assert isinstance(opts.timeout, int)
        assert opts.timeout == 1500

    def test_cli_integration_default_timeout(self, monkeypatch):
        """Test full CLI integration with default timeout."""
        from smartrun import cli as cli_mod

        captured_opts = {}

        def fake_dispatch(self):
            captured_opts["timeout"] = self.opts.timeout

        monkeypatch.setattr(cli_mod.CLI, "dispatch", fake_dispatch)

        # Simulate CLI call without --timeout
        cli_mod.main(["test_script.py"])

        assert captured_opts["timeout"] == 1200

    def test_cli_integration_custom_timeout(self, monkeypatch):
        """Test full CLI integration with custom timeout."""
        from smartrun import cli as cli_mod

        captured_opts = {}

        def fake_dispatch(self):
            captured_opts["timeout"] = self.opts.timeout

        monkeypatch.setattr(cli_mod.CLI, "dispatch", fake_dispatch)

        # Simulate CLI call with --timeout 500
        cli_mod.main(["test_script.py", "--timeout", "500"])

        assert captured_opts["timeout"] == 500

    def test_timeout_with_other_options(self, monkeypatch):
        """Test timeout works correctly with other CLI options."""
        from smartrun import cli as cli_mod

        captured_opts = {}

        def fake_dispatch(self):
            captured_opts["timeout"] = self.opts.timeout
            captured_opts["verbose"] = self.opts.verbose
            captured_opts["html"] = self.opts.html

        monkeypatch.setattr(cli_mod.CLI, "dispatch", fake_dispatch)

        # Simulate CLI call with multiple options
        cli_mod.main(["test_script.py", "--timeout", "800", "--verbose", "--html"])

        assert captured_opts["timeout"] == 800
        assert captured_opts["verbose"] is True
        assert captured_opts["html"] is True

    def test_timeout_zero(self):
        """Test that timeout can be set to 0 (no timeout)."""
        parser = _build_arg_parser()
        args = parser.parse_args(["test_script.py", "--timeout", "0"])
        assert args.timeout == 0

    def test_timeout_large_value(self):
        """Test that timeout accepts large values."""
        parser = _build_arg_parser()
        args = parser.parse_args(["test_script.py", "--timeout", "86400"])
        assert args.timeout == 86400  # 24 hours in seconds

    def test_timeout_invalid_string_raises_error(self):
        """Test that non-integer timeout value raises error."""
        parser = _build_arg_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["test_script.py", "--timeout", "invalid"])

    def test_options_dataclass_default(self):
        """Test Options dataclass has correct default for timeout."""
        opts = Options(script="test.py")
        assert opts.timeout == 1200


class TestTimeoutIntegration:
    """Integration tests for timeout with various CLI commands."""

    def test_timeout_with_install_command(self, monkeypatch):
        """Test timeout parameter works with install command."""
        from smartrun import cli as cli_mod

        captured = {}

        def fake_install(opts, packages, verbose=False):
            captured["timeout"] = opts.timeout
            captured["packages"] = packages

        monkeypatch.setattr(cli_mod.Scan, "resolve", lambda pkgs: pkgs)
        monkeypatch.setattr(cli_mod, "install_packages_smart", fake_install)

        cli_mod.main(["install", "pandas", "--timeout", "2400"])

        assert captured["timeout"] == 2400

    def test_timeout_with_venv_command(self, monkeypatch):
        """Test timeout parameter works with venv command."""
        from smartrun import cli as cli_mod

        captured = {}

        def fake_create_venv(opts):
            captured["timeout"] = opts.timeout
            return "test_venv"

        monkeypatch.setattr(cli_mod, "create_venv_path_pure", fake_create_venv)

        cli_mod.main(["venv", "myenv", "--timeout", "1800"])

        assert captured["timeout"] == 1800


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
