#!/usr/bin/env python3
"""
Simple test runner for smartrun CLI tests.
This version mocks the imports to avoid dependency issues during testing.
"""
import sys
import os
from pathlib import Path
from dataclasses import dataclass
import tempfile

# Add the smartrun directory to the path
sys.path.insert(0, str(Path(__file__).parent / "smartrun"))


# Mock the rich print to avoid import issues
def mock_print(*args, **kwargs):
    """Mock rich print function."""
    print(*args, **kwargs)


# Patch rich.print
sys.modules["rich"] = type(sys)("rich")
sys.modules["rich"].print = mock_print

try:
    from smartrun.options import Options
    from smartrun.cli import CLI

    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Could not import smartrun modules: {e}")
    IMPORTS_AVAILABLE = False


@dataclass
class MockArgs:
    """Mock arguments for testing CLI functionality."""

    script: str
    second: str = None
    venv: bool = False
    verbose: bool = False
    no_uv: bool = False
    html: bool = False
    exc: str | None = None
    inc: str | None = None
    out: str | None = None


def test_options_creation():
    """Test basic Options object creation."""
    if not IMPORTS_AVAILABLE:
        print("❌ Cannot test - imports not available")
        return False

    try:
        opts = Options(script="test.py")
        print("✅ Options creation test passed")
        return True
    except Exception as e:
        print(f"❌ Options creation test failed: {e}")
        return False


def test_options_with_all_params():
    """Test Options with all parameters."""
    if not IMPORTS_AVAILABLE:
        print("❌ Cannot test - imports not available")
        return False

    try:
        opts = Options(
            script="test.py",
            second="arg2",
            venv=Path("./test_env"),
            verbose=True,
            no_uv=True,
            html=True,
            exc="pkg1,pkg2",
            inc="matplotlib,numpy",
            out=Path("./output"),
        )

        # Verify all attributes are set correctly
        assert opts.script == "test.py"
        assert opts.second == "arg2"
        assert opts.venv == Path("./test_env")
        assert opts.verbose is True
        assert opts.no_uv is True
        assert opts.html is True
        assert opts.exc == "pkg1,pkg2"
        assert opts.inc == "matplotlib,numpy"
        assert opts.out == Path("./output")

        print("✅ Options with all parameters test passed")
        return True
    except Exception as e:
        print(f"❌ Options with all parameters test failed: {e}")
        return False


def test_notebook_html_args():
    """Test creating arguments for notebook with HTML output."""
    print("\n🧪 Testing notebook HTML arguments...")

    try:
        # Test HTML enabled
        args_html = MockArgs(
            script="titanic.ipynb", html=True, out="html_outputs", verbose=True
        )

        if IMPORTS_AVAILABLE:
            opts = Options(
                script=args_html.script,
                second=args_html.second,
                venv=args_html.venv,
                verbose=args_html.verbose,
                no_uv=args_html.no_uv,
                html=args_html.html,
                exc=args_html.exc,
                inc=args_html.inc,
                out=args_html.out,
            )

            assert opts.html is True
            assert opts.out == "html_outputs"
            assert opts.script == "titanic.ipynb"
            assert opts.verbose is True

        print("✅ Notebook HTML arguments test passed")
        return True
    except Exception as e:
        print(f"❌ Notebook HTML arguments test failed: {e}")
        return False


def test_notebook_no_html_args():
    """Test creating arguments for notebook without HTML output."""
    print("\n🧪 Testing notebook no-HTML arguments...")

    try:
        # Test HTML disabled
        args_no_html = MockArgs(script="titanic.ipynb", html=False, verbose=True)

        if IMPORTS_AVAILABLE:
            opts = Options(
                script=args_no_html.script,
                second=args_no_html.second,
                venv=args_no_html.venv,
                verbose=args_no_html.verbose,
                no_uv=args_no_html.no_uv,
                html=args_no_html.html,
                exc=args_no_html.exc,
                inc=args_no_html.inc,
                out=args_no_html.out,
            )

            assert opts.html is False
            assert opts.out is None
            assert opts.script == "titanic.ipynb"
            assert opts.verbose is True

        print("✅ Notebook no-HTML arguments test passed")
        return True
    except Exception as e:
        print(f"❌ Notebook no-HTML arguments test failed: {e}")
        return False


def test_cli_commands():
    """Test various CLI command scenarios."""
    print("\n🧪 Testing CLI command scenarios...")

    test_scenarios = [
        ("venv", "test_env"),
        ("install", "pandas,numpy"),
        ("add", "matplotlib"),
        ("list", None),
        ("titanic.ipynb", None),
        ("iris.ipynb", None),
    ]

    passed = 0
    for script, second in test_scenarios:
        try:
            args = MockArgs(script=script, second=second, verbose=True)

            if IMPORTS_AVAILABLE:
                opts = Options(
                    script=args.script,
                    second=args.second,
                    venv=args.venv,
                    verbose=args.verbose,
                    no_uv=args.no_uv,
                    html=args.html,
                    exc=args.exc,
                    inc=args.inc,
                    out=args.out,
                )

                # Basic validation
                assert opts.script == script
                assert opts.second == second
                assert opts.verbose is True

            print(f"  ✅ {script} command test passed")
            passed += 1
        except Exception as e:
            print(f"  ❌ {script} command test failed: {e}")

    print(f"✅ CLI commands test: {passed}/{len(test_scenarios)} passed")
    return passed == len(test_scenarios)


def test_options_properties():
    """Test Options class properties and methods."""
    if not IMPORTS_AVAILABLE:
        print("❌ Cannot test properties - imports not available")
        return False

    try:
        # Test use_uv property
        opts = Options(script="test.py", no_uv=False)

        # Clear environment variable for clean test
        old_env = os.environ.get("SMARTRUN_NO_UV")
        if "SMARTRUN_NO_UV" in os.environ:
            del os.environ["SMARTRUN_NO_UV"]

        # Test default behavior (should use uv)
        assert opts.use_uv is True

        # Test with no_uv=True
        opts_no_uv = Options(script="test.py", no_uv=True)
        assert opts_no_uv.use_uv is False

        # Test with environment variable
        os.environ["SMARTRUN_NO_UV"] = "1"
        opts_env = Options(script="test.py", no_uv=False)
        assert opts_env.use_uv is False

        # Restore environment
        if old_env is not None:
            os.environ["SMARTRUN_NO_UV"] = old_env
        elif "SMARTRUN_NO_UV" in os.environ:
            del os.environ["SMARTRUN_NO_UV"]

        print("✅ Options properties test passed")
        return True
    except Exception as e:
        print(f"❌ Options properties test failed: {e}")
        return False


def run_comprehensive_tests():
    """Run all available tests."""
    print("🚀 Starting comprehensive smartrun test suite...")
    print("=" * 60)

    tests = [
        ("Options Creation", test_options_creation),
        ("Options All Parameters", test_options_with_all_params),
        ("Notebook HTML Args", test_notebook_html_args),
        ("Notebook No-HTML Args", test_notebook_no_html_args),
        ("CLI Commands", test_cli_commands),
        ("Options Properties", test_options_properties),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} - FAILED with exception: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"🏁 Test Results: {passed} passed, {failed} failed")

    if IMPORTS_AVAILABLE:
        print("✅ All smartrun modules imported successfully")
    else:
        print("⚠️  Some tests skipped due to import issues")

    return failed == 0


def quick_jupyter_tests():
    """Run quick Jupyter-specific tests."""
    print("🚀 Quick Jupyter notebook tests...")
    print("-" * 40)

    # Test 1: HTML output
    print("\n1️⃣  Testing Jupyter with HTML output:")
    test_notebook_html_args()

    # Test 2: No HTML output
    print("\n2️⃣  Testing Jupyter without HTML output:")
    test_notebook_no_html_args()

    print("\n✅ Jupyter tests completed!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "--html" or command == "html":
            print("🧪 Testing HTML functionality...")
            test_notebook_html_args()
        elif command == "--no-html" or command == "no-html":
            print("🧪 Testing no-HTML functionality...")
            test_notebook_no_html_args()
        elif command == "--jupyter" or command == "jupyter":
            quick_jupyter_tests()
        elif command == "--all" or command == "all":
            run_comprehensive_tests()
        elif command == "--quick" or command == "quick":
            run_comprehensive_tests()  # Add quick option
        else:
            print(
                "Usage: python test_runner.py [--html|--no-html|--jupyter|--all|--quick]"
            )
            print("  --html     - Test HTML output functionality")
            print("  --no-html  - Test without HTML output")
            print("  --jupyter  - Run Jupyter-specific tests")
            print("  --all      - Run comprehensive test suite")
            print("  --quick    - Run comprehensive test suite")
            print(
                "\nNote: Commands also work without -- prefix (e.g., 'html' instead of '--html')"
            )
    else:
        # Default: run Jupyter tests
        quick_jupyter_tests()
