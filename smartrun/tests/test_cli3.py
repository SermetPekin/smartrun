#!/usr/bin/env python
"""
Enhanced test suite for smartrun CLI and Options functionality.
Tests include Jupyter notebook execution with and without HTML output,
various CLI commands, and comprehensive Options class validation.

Usage:
    python test_cli3.py              # Run default test (no-HTML)
    python test_cli3.py --html       # Test HTML output
    python test_cli3.py --no-html    # Test without HTML
    py            print("Default (no args): Run html_no() test")
    else:
        # Default behavior: run the no-HTML test
        html_no() test_cli3.py --all        # Run all tests
    python test_cli3.py --quick      # Run quick validation tests
"""
from smartrun.options import Options
from smartrun.cli import CLI
from dataclasses import dataclass
from pathlib import Path
import sys
import os
import tempfile


@dataclass
class MockArgs:
    """Enhanced mock arguments for testing CLI functionality."""

    script: str
    second: str = None
    venv: bool = False
    verbose: bool = False
    no_uv: bool = False
    html: bool = False
    exc: str | None = None
    inc: str | None = None
    out: str | None = None
    version: bool = False
    help: bool = False
    lock: bool = False
    unlock: bool = False
    extra_args: tuple = ()


def create_options_from_args(args: MockArgs) -> Options:
    """Helper to create Options from MockArgs with all parameters."""
    return Options(
        script=args.script,
        second=args.second,
        venv=args.venv,
        verbose=args.verbose,
        no_uv=args.no_uv,
        html=args.html,
        exc=args.exc,
        inc=args.inc,
        out=args.out,
        version=args.version,
        help=args.help,
        lock=args.lock,
        unlock=args.unlock,
        extra_args=args.extra_args,
    )


def execute_cli_test(args: MockArgs, description: str = ""):
    """Enhanced helper to execute CLI with given arguments and logging."""
    if description:
        print(f"  🔧 {description}")

    opts = create_options_from_args(args)
    cli = CLI(opts)

    try:
        cli.router()
        print(f"  ✅ Success: {args.script}")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {args.script} - {e}")
        return False


# ════════════════════════════════════════════════════════════════════════════════
#                           ORIGINAL TEST FUNCTIONS (Enhanced)
# ════════════════════════════════════════════════════════════════════════════════


def t1():
    """Enhanced version of original t1 - Virtual environment creation."""
    print("\n🧪 t1() - Creating virtual environment...")
    args = MockArgs("venv", "v6", verbose=True)
    return execute_cli_test(args, "Creating venv 'v6'")


def t2():
    """Enhanced version of original t2 - Package installation."""
    print("\n🧪 t2() - Installing packages...")
    args = MockArgs("install", "pandas", verbose=True)
    return execute_cli_test(args, "Installing pandas")


def html():
    """Enhanced version of original html() - Notebook with HTML output."""
    print("\n🧪 html() - Running notebook with HTML output...")
    with tempfile.TemporaryDirectory() as temp_dir:
        args = MockArgs(script="titanic.ipynb", html=True, out=temp_dir, verbose=True)
        return execute_cli_test(
            args, f"Running titanic.ipynb with HTML output to {temp_dir}"
        )


def html_no():
    """Enhanced version of original html_no() - Notebook without HTML."""
    print("\n🧪 html_no() - Running notebook without HTML output...")
    args = MockArgs(
        script="titanic.ipynb", html=False, out="Output_folder", verbose=True
    )
    return execute_cli_test(args, "Running titanic.ipynb without HTML output")


# ════════════════════════════════════════════════════════════════════════════════
#                              ADDITIONAL TESTS
# ════════════════════════════════════════════════════════════════════════════════


def test_iris_notebook():
    """Test iris notebook execution."""
    print("\n🧪 Testing iris notebook...")
    args = MockArgs("iris.ipynb", verbose=True)
    return execute_cli_test(args, "Running iris.ipynb")


def test_iris_notebook_html():
    """Test iris notebook with HTML output."""
    print("\n🧪 Testing iris notebook with HTML...")
    with tempfile.TemporaryDirectory() as temp_dir:
        args = MockArgs("iris.ipynb", html=True, out=temp_dir, verbose=True)
        return execute_cli_test(args, f"Running iris.ipynb with HTML to {temp_dir}")


def test_sample_notebook():
    """Test sample notebook from scripts directory."""
    print("\n🧪 Testing sample notebook...")
    args = MockArgs("scripts/sample.ipynb", verbose=True)
    return execute_cli_test(args, "Running scripts/sample.ipynb")


def test_package_operations():
    """Test various package operations."""
    print("\n🧪 Testing package operations...")

    operations = [
        ("install", "numpy,matplotlib", "Installing multiple packages"),
        ("add", "seaborn", "Adding seaborn package"),
        ("add", "plotly,rich", "Adding multiple packages"),
        ("install", "requests", "Installing single package"),
    ]

    results = []
    for script, second, desc in operations:
        args = MockArgs(script, second, verbose=True)
        results.append(execute_cli_test(args, desc))

    return all(results)


def test_environment_operations():
    """Test environment-related operations."""
    print("\n🧪 Testing environment operations...")

    operations = [
        ("venv", "test_env_1", "Creating test environment 1"),
        ("venv", "test_env_2", "Creating test environment 2"),
        ("list", None, "Listing environments"),
    ]

    results = []
    for script, second, desc in operations:
        args = MockArgs(script, second, verbose=True)
        results.append(execute_cli_test(args, desc))

    return all(results)


def test_options_validation():
    """Test Options class validation and properties."""
    print("\n🧪 Testing Options class validation...")

    try:
        # Test basic Options creation
        opts1 = Options(script="test.py")
        assert opts1.script == "test.py"
        assert opts1.verbose is False
        assert opts1.html is False
        print("  ✅ Basic Options creation")

        # Test with all parameters
        opts2 = Options(
            script="notebook.ipynb",
            second="arg",
            venv=Path("./env"),
            verbose=True,
            no_uv=True,
            html=True,
            exc="pkg1,pkg2",
            inc="matplotlib",
            out=Path("./output"),
            version=True,
            help=True,
            lock=True,
            unlock=True,
            extra_args=("--extra",),
        )
        assert opts2.script == "notebook.ipynb"
        assert opts2.verbose is True
        assert opts2.html is True
        assert opts2.exc == "pkg1,pkg2"
        print("  ✅ Full Options creation")

        # Test use_uv property
        opts3 = Options(script="test.py", no_uv=False)
        old_env = os.environ.get("SMARTRUN_NO_UV")
        if "SMARTRUN_NO_UV" in os.environ:
            del os.environ["SMARTRUN_NO_UV"]

        assert opts3.use_uv is True
        print("  ✅ use_uv property test")

        # Restore environment
        if old_env:
            os.environ["SMARTRUN_NO_UV"] = old_env

        return True

    except Exception as e:
        print(f"  ❌ Options validation failed: {e}")
        return False


def test_advanced_features():
    """Test advanced CLI features."""
    print("\n🧪 Testing advanced features...")

    features = [
        MockArgs("titanic.ipynb", verbose=True, no_uv=True),
        MockArgs("iris.ipynb", html=True, verbose=True, exc="matplotlib"),
        MockArgs("install", "pandas", inc="numpy,scipy", verbose=True),
    ]

    results = []
    for i, args in enumerate(features, 1):
        result = execute_cli_test(args, f"Advanced feature test {i}")
        results.append(result)

    return all(results)


# ════════════════════════════════════════════════════════════════════════════════
#                              TEST RUNNERS
# ════════════════════════════════════════════════════════════════════════════════


def run_original_tests():
    """Run the original test functions."""
    print("🚀 Running original tests...")
    print("=" * 50)

    tests = [
        ("t1 (venv creation)", t1),
        ("t2 (package install)", t2),
        ("html (notebook with HTML)", html),
        ("html_no (notebook without HTML)", html_no),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print(f"✅ {name} - {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"❌ {name} - FAILED: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)
    print(f"\n🏁 Original tests: {passed}/{total} passed")
    return passed == total


def run_jupyter_tests():
    """Run Jupyter notebook specific tests."""
    print("🚀 Running Jupyter notebook tests...")
    print("=" * 50)

    tests = [
        ("Titanic notebook (no HTML)", html_no),
        ("Titanic notebook (HTML)", html),
        ("Iris notebook", test_iris_notebook),
        ("Iris notebook (HTML)", test_iris_notebook_html),
        ("Sample notebook", test_sample_notebook),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print(f"✅ {name} - {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"❌ {name} - FAILED: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)
    print(f"\n🏁 Jupyter tests: {passed}/{total} passed")
    return passed == total


def run_comprehensive_tests():
    """Run all available tests."""
    print("🚀 Running comprehensive test suite...")
    print("=" * 70)

    test_suites = [
        ("Original Tests", run_original_tests),
        ("Options Validation", test_options_validation),
        ("Package Operations", test_package_operations),
        ("Environment Operations", test_environment_operations),
        ("Advanced Features", test_advanced_features),
    ]

    suite_results = []
    for suite_name, suite_func in test_suites:
        print(f"\n📋 {suite_name}")
        print("-" * len(suite_name))
        try:
            result = suite_func()
            suite_results.append(result)
            print(f"📊 {suite_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"� {suite_name}: FAILED - {e}")
            suite_results.append(False)

    passed_suites = sum(suite_results)
    total_suites = len(suite_results)

    print("\n" + "=" * 70)
    print(f"🏁 Final Results: {passed_suites}/{total_suites} test suites passed")

    if passed_suites == total_suites:
        print("🎉 All tests completed successfully!")
    else:
        print("⚠️  Some tests failed - check output above")

    return passed_suites == total_suites


def run_quick_tests():
    """Run a quick subset of critical tests."""
    print("� Running quick validation tests...")
    print("=" * 40)

    quick_tests = [
        ("Options Creation", test_options_validation),
        ("HTML Notebook", html),
        ("No-HTML Notebook", html_no),
        ("Package Install", t2),
    ]

    results = []
    for name, test_func in quick_tests:
        try:
            result = test_func()
            results.append(result)
            status = "PASSED" if result else "FAILED"
            print(f"⚡ {name}: {status}")
        except Exception as e:
            print(f"⚡ {name}: FAILED - {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)
    print(f"\n🏁 Quick tests: {passed}/{total} passed")
    return passed == total


# ════════════════════════════════════════════════════════════════════════════════
#                                MAIN ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "--html" or command == "html":
            html()
        elif command == "--no-html" or command == "no-html":
            html_no()
        elif command == "--jupyter" or command == "jupyter":
            run_jupyter_tests()
        elif command == "--all" or command == "all":
            run_comprehensive_tests()
        elif command == "--quick" or command == "quick":
            run_quick_tests()
        elif command == "--original" or command == "original":
            run_original_tests()
        elif command == "--t1" or command == "t1":
            t1()
        elif command == "--t2" or command == "t2":
            t2()
        else:
            print("Usage: python test_cli3.py [command]")
            print("\nAvailable commands:")
            print("  --html      - Test notebook with HTML output")
            print("  --no-html   - Test notebook without HTML output")
            print("  --jupyter   - Run all Jupyter notebook tests")
            print("  --all       - Run comprehensive test suite")
            print("  --quick     - Run quick validation tests")
            print("  --original  - Run original test functions")
            print("  --t1        - Run t1() test (venv creation)")
            print("  --t2        - Run t2() test (package install)")
            print("\nNote: Commands also work without -- prefix")
            print("Default (no args): Run html_no() test")
    else:
        # Default behavior: run the no-HTML test
        html_no()
