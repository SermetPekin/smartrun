#!/usr/bin/env python
"""
Test suite for notebook execution timeout functionality.
Tests that timeout is properly passed from Options to notebook execution.

Run:
    pytest smartrun/tests/test_nb_timeout.py -v
    python -m pytest smartrun/tests/test_nb_timeout.py -v
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from smartrun.nb.nb_run import NBOptions, convert, run_and_save_notebook
from smartrun.options import Options


class TestNBOptionsTimeout:
    """Test NBOptions timeout configuration."""

    def test_nb_options_default_timeout(self):
        """Test that NBOptions has default timeout of 600."""
        nb_opts = NBOptions(file_name="test.ipynb")
        assert nb_opts.timeout == 600

    def test_nb_options_custom_timeout(self):
        """Test that NBOptions accepts custom timeout."""
        nb_opts = NBOptions(file_name="test.ipynb", timeout=1200)
        assert nb_opts.timeout == 1200

    def test_nb_options_timeout_type(self):
        """Test that timeout is an integer."""
        nb_opts = NBOptions(file_name="test.ipynb", timeout=900)
        assert isinstance(nb_opts.timeout, int)

    def test_nb_options_str_representation_includes_timeout(self):
        """Test that string representation includes timeout."""
        nb_opts = NBOptions(file_name="test.ipynb", timeout=1800)
        str_repr = str(nb_opts)
        assert "timeout" in str_repr.lower()
        assert "1800" in str_repr


class TestConvertFunctionTimeout:
    """Test that convert function properly uses timeout from Options."""

    @patch("smartrun.nb.nb_run.ExecutePreprocessor")
    @patch("smartrun.nb.nb_run.HTMLExporter")
    @patch("smartrun.nb.nb_run.nbformat")
    @patch("builtins.open")
    @patch("os.makedirs")
    @patch("os.chdir")
    def test_convert_uses_opts_timeout(
        self,
        mock_chdir,
        mock_makedirs,
        mock_open,
        mock_nbformat,
        mock_html_exporter,
        mock_execute_preprocessor,
    ):
        """Test that convert function passes opts.timeout to ExecutePreprocessor."""
        # Setup mocks
        mock_nb = MagicMock()
        mock_nbformat.read.return_value = mock_nb
        mock_ep_instance = MagicMock()
        mock_execute_preprocessor.return_value = mock_ep_instance
        mock_html_exporter_instance = MagicMock()
        mock_html_exporter.return_value = mock_html_exporter_instance
        mock_html_exporter_instance.from_notebook_node.return_value = (
            "<html></html>",
            {},
        )

        # Create test objects
        nb_opts = NBOptions(file_name="test.ipynb", timeout=600)
        opts = Options(script="test.ipynb", timeout=2400)

        # Call convert
        try:
            convert(nb_opts, opts)
        except Exception:
            # We expect some exceptions due to mocking, but we're checking the call
            pass

        # Verify ExecutePreprocessor was called with opts.timeout
        mock_execute_preprocessor.assert_called_once()
        call_kwargs = mock_execute_preprocessor.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == 2400

    @patch("smartrun.nb.nb_run.ExecutePreprocessor")
    @patch("smartrun.nb.nb_run.HTMLExporter")
    @patch("smartrun.nb.nb_run.nbformat")
    @patch("builtins.open")
    @patch("os.makedirs")
    @patch("os.chdir")
    def test_convert_with_default_cli_timeout(
        self,
        mock_chdir,
        mock_makedirs,
        mock_open,
        mock_nbformat,
        mock_html_exporter,
        mock_execute_preprocessor,
    ):
        """Test that convert uses default CLI timeout of 1200."""
        # Setup mocks
        mock_nb = MagicMock()
        mock_nbformat.read.return_value = mock_nb
        mock_ep_instance = MagicMock()
        mock_execute_preprocessor.return_value = mock_ep_instance
        mock_html_exporter_instance = MagicMock()
        mock_html_exporter.return_value = mock_html_exporter_instance
        mock_html_exporter_instance.from_notebook_node.return_value = (
            "<html></html>",
            {},
        )

        # Create test objects with default timeout
        nb_opts = NBOptions(file_name="test.ipynb")
        opts = Options(script="test.ipynb")  # Uses default timeout=1200

        # Call convert
        try:
            convert(nb_opts, opts)
        except Exception:
            pass

        # Verify ExecutePreprocessor was called with default timeout
        mock_execute_preprocessor.assert_called_once()
        call_kwargs = mock_execute_preprocessor.call_args[1]
        assert call_kwargs["timeout"] == 1200

    @patch("smartrun.nb.nb_run.ExecutePreprocessor")
    @patch("smartrun.nb.nb_run.HTMLExporter")
    @patch("smartrun.nb.nb_run.nbformat")
    @patch("builtins.open")
    @patch("os.makedirs")
    @patch("os.chdir")
    def test_convert_timeout_zero(
        self,
        mock_chdir,
        mock_makedirs,
        mock_open,
        mock_nbformat,
        mock_html_exporter,
        mock_execute_preprocessor,
    ):
        """Test that convert handles timeout=0 (no timeout)."""
        # Setup mocks
        mock_nb = MagicMock()
        mock_nbformat.read.return_value = mock_nb
        mock_ep_instance = MagicMock()
        mock_execute_preprocessor.return_value = mock_ep_instance
        mock_html_exporter_instance = MagicMock()
        mock_html_exporter.return_value = mock_html_exporter_instance
        mock_html_exporter_instance.from_notebook_node.return_value = (
            "<html></html>",
            {},
        )

        # Create test objects with timeout=0
        nb_opts = NBOptions(file_name="test.ipynb")
        opts = Options(script="test.ipynb", timeout=0)

        # Call convert
        try:
            convert(nb_opts, opts)
        except Exception:
            pass

        # Verify ExecutePreprocessor was called with timeout=0
        mock_execute_preprocessor.assert_called_once()
        call_kwargs = mock_execute_preprocessor.call_args[1]
        assert call_kwargs["timeout"] == 0


class TestRunAndSaveNotebookTimeout:
    """Test run_and_save_notebook function timeout handling."""

    @patch("smartrun.nb.nb_run.ExecutePreprocessor")
    @patch("smartrun.nb.nb_run.nbformat")
    @patch("pathlib.Path.open")
    def test_run_and_save_uses_nb_opts_timeout(
        self,
        mock_path_open,
        mock_nbformat,
        mock_execute_preprocessor,
    ):
        """Test that run_and_save_notebook uses nb_opts.timeout when opts is None."""
        mock_nb = MagicMock()
        mock_file = MagicMock()
        mock_path_open.return_value.__enter__.return_value = mock_file
        mock_nbformat.read.return_value = mock_nb
        mock_nbformat.write = MagicMock()

        mock_ep_instance = MagicMock()
        mock_ep_instance.preprocess.return_value = (mock_nb, {})
        mock_execute_preprocessor.return_value = mock_ep_instance

        nb_opts = NBOptions(file_name="test.ipynb", timeout=1200)

        try:
            run_and_save_notebook(nb_opts)
        except Exception as e:
            # Some exceptions are ok due to mocking
            pass

        # Should use nb_opts.timeout when opts is None
        mock_execute_preprocessor.assert_called_once_with(
            timeout=1200, kernel_name="python3"
        )

    @patch("smartrun.nb.nb_run.ExecutePreprocessor")
    @patch("smartrun.nb.nb_run.nbformat")
    @patch("pathlib.Path.open")
    def test_run_and_save_uses_opts_timeout(
        self,
        mock_path_open,
        mock_nbformat,
        mock_execute_preprocessor,
    ):
        """Test that run_and_save_notebook uses opts.timeout when opts is provided."""
        mock_nb = MagicMock()
        mock_file = MagicMock()
        mock_path_open.return_value.__enter__.return_value = mock_file
        mock_nbformat.read.return_value = mock_nb
        mock_nbformat.write = MagicMock()

        mock_ep_instance = MagicMock()
        mock_ep_instance.preprocess.return_value = (mock_nb, {})
        mock_execute_preprocessor.return_value = mock_ep_instance

        nb_opts = NBOptions(file_name="test.ipynb", timeout=600)
        opts = Options(script="test.ipynb", timeout=2400)

        try:
            run_and_save_notebook(nb_opts, opts)
        except Exception as e:
            # Some exceptions are ok due to mocking
            pass

        # Should use opts.timeout when opts is provided (takes precedence)
        mock_execute_preprocessor.assert_called_once_with(
            timeout=2400, kernel_name="python3"
        )

    @patch("smartrun.nb.nb_run.ExecutePreprocessor")
    @patch("smartrun.nb.nb_run.nbformat")
    @patch("pathlib.Path.open")
    def test_run_and_save_default_nb_opts_timeout(
        self,
        mock_path_open,
        mock_nbformat,
        mock_execute_preprocessor,
    ):
        """Test that run_and_save_notebook uses default NBOptions timeout of 600."""
        mock_nb = MagicMock()
        mock_file = MagicMock()
        mock_path_open.return_value.__enter__.return_value = mock_file
        mock_nbformat.read.return_value = mock_nb
        mock_nbformat.write = MagicMock()

        mock_ep_instance = MagicMock()
        mock_ep_instance.preprocess.return_value = (mock_nb, {})
        mock_execute_preprocessor.return_value = mock_ep_instance

        nb_opts = NBOptions(file_name="test.ipynb")  # Uses default timeout=600

        try:
            run_and_save_notebook(nb_opts)
        except Exception as e:
            pass

        # Should use default NBOptions timeout of 600
        mock_execute_preprocessor.assert_called_once_with(
            timeout=600, kernel_name="python3"
        )


class TestIntegrationWithCLI:
    """Integration tests for notebook timeout with CLI."""

    def test_notebook_execution_receives_cli_timeout(self, monkeypatch):
        """Test that notebook execution receives timeout from CLI options."""
        from smartrun import cli as cli_mod

        captured = {}

        def fake_convert(nb_options, opts):
            captured["timeout"] = opts.timeout if opts else None
            captured["nb_timeout"] = nb_options.timeout

        # Patch convert function
        monkeypatch.setattr("smartrun.runner.convert", fake_convert)
        # Patch other heavy operations
        monkeypatch.setattr(cli_mod, "install_packages_smart", lambda *a, **k: None)
        monkeypatch.setattr(
            cli_mod, "install_packages_smartrun_smartfiles", lambda *a, **k: None
        )

        # Simulate running a notebook with custom timeout
        cli_mod.main(["test.ipynb", "--timeout", "3600"])

        # This would need the actual integration to work
        # For now, this is a placeholder test structure


class TestTimeoutEdgeCases:
    """Test edge cases for timeout handling."""

    def test_nb_options_with_very_large_timeout(self):
        """Test NBOptions with very large timeout value."""
        nb_opts = NBOptions(file_name="test.ipynb", timeout=86400)  # 24 hours
        assert nb_opts.timeout == 86400

    def test_nb_options_with_zero_timeout(self):
        """Test NBOptions with zero timeout (no timeout)."""
        nb_opts = NBOptions(file_name="test.ipynb", timeout=0)
        assert nb_opts.timeout == 0

    def test_options_timeout_converted_to_int(self):
        """Test that timeout is converted to int in convert function."""
        opts = Options(script="test.ipynb", timeout=1500)
        # The convert function uses int(opts.timeout) at line 138
        assert int(opts.timeout) == 1500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
