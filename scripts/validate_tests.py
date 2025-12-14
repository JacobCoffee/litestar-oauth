#!/usr/bin/env python3
"""Validate the litestar-oauth test suite structure and completeness.

This script checks that all required test files exist and provides
statistics about the test suite.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def count_test_functions(file_path: Path) -> dict[str, int]:
    """Count test functions in a Python file.

    Args:
        file_path: Path to Python test file

    Returns:
        Dict with counts of sync/async tests
    """
    try:
        with file_path.open() as f:
            tree = ast.parse(f.read())
    except Exception:
        return {"sync": 0, "async": 0, "total": 0}

    sync_tests = 0
    async_tests = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith("test_"):
                if any(isinstance(d, ast.Name) and d.id == "async" for d in node.decorator_list):
                    async_tests += 1
                else:
                    sync_tests += 1
        elif isinstance(node, ast.AsyncFunctionDef):
            if node.name.startswith("test_"):
                async_tests += 1

    return {
        "sync": sync_tests,
        "async": async_tests,
        "total": sync_tests + async_tests,
    }


def count_test_classes(file_path: Path) -> int:
    """Count test classes in a Python file.

    Args:
        file_path: Path to Python test file

    Returns:
        Number of test classes
    """
    try:
        with file_path.open() as f:
            tree = ast.parse(f.read())
    except Exception:
        return 0

    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            count += 1

    return count


def validate_test_structure() -> dict[str, Any]:
    """Validate the test suite structure.

    Returns:
        Dict with validation results
    """
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"
    testing_dir = project_root / "src" / "litestar_oauth" / "testing"

    results: dict[str, Any] = {
        "required_files": {},
        "test_counts": {},
        "class_counts": {},
        "total_tests": 0,
        "total_classes": 0,
        "missing_files": [],
    }

    # Required test files
    required_files = {
        "Testing utilities": {
            testing_dir / "__init__.py": "Testing module exports",
            testing_dir / "mocks.py": "Mock implementations",
            testing_dir / "fixtures.py": "Pytest fixtures",
        },
        "Test configuration": {
            tests_dir / "conftest.py": "Shared fixtures and config",
        },
        "Unit tests": {
            tests_dir / "unit" / "test_types.py": "Type tests",
            tests_dir / "unit" / "test_exceptions.py": "Exception tests",
            tests_dir / "unit" / "test_base.py": "Base provider tests",
            tests_dir / "unit" / "test_service.py": "Service tests",
        },
        "Provider tests": {
            tests_dir / "unit" / "providers" / "test_github.py": "GitHub provider tests",
            tests_dir / "unit" / "providers" / "test_google.py": "Google provider tests",
            tests_dir / "unit" / "providers" / "test_discord.py": "Discord provider tests",
        },
        "Integration tests": {
            tests_dir / "integration" / "test_litestar_plugin.py": "Litestar plugin tests",
        },
    }

    # Check each file
    for category, files in required_files.items():
        results["required_files"][category] = {}
        for file_path, description in files.items():
            exists = file_path.exists()
            results["required_files"][category][str(file_path)] = {
                "exists": exists,
                "description": description,
            }

            if not exists:
                results["missing_files"].append(str(file_path))
            elif file_path.suffix == ".py" and "test_" in file_path.name:
                # Count tests in test files
                counts = count_test_functions(file_path)
                classes = count_test_classes(file_path)

                results["test_counts"][str(file_path)] = counts
                results["class_counts"][str(file_path)] = classes
                results["total_tests"] += counts["total"]
                results["total_classes"] += classes

    return results


def print_validation_results(results: dict[str, Any]) -> None:
    """Print validation results in a readable format.

    Args:
        results: Validation results dictionary
    """
    print("\n" + "=" * 80)
    print("LITESTAR-OAUTH TEST SUITE VALIDATION")
    print("=" * 80 + "\n")

    # File existence check
    print("FILE STRUCTURE:")
    print("-" * 80)
    for category, files in results["required_files"].items():
        print(f"\n{category}:")
        for file_path, info in files.items():
            status = "✓" if info["exists"] else "✗"
            print(f"  {status} {Path(file_path).name:<40} - {info['description']}")

    # Missing files
    if results["missing_files"]:
        print("\n\nMISSING FILES:")
        print("-" * 80)
        for file_path in results["missing_files"]:
            print(f"  ✗ {file_path}")
    else:
        print("\n\n✓ All required files present")

    # Test statistics
    print("\n\nTEST STATISTICS:")
    print("-" * 80)
    print(f"Total Test Functions: {results['total_tests']}")
    print(f"Total Test Classes:   {results['total_classes']}")

    if results["test_counts"]:
        print("\n\nDetailed Test Counts:")
        for file_path, counts in results["test_counts"].items():
            file_name = Path(file_path).name
            print(
                f"  {file_name:<40} "
                f"Tests: {counts['total']:>3} "
                f"(Sync: {counts['sync']:>3}, Async: {counts['async']:>3})"
            )

        # Calculate totals
        total_sync = sum(c["sync"] for c in results["test_counts"].values())
        total_async = sum(c["async"] for c in results["test_counts"].values())

        print(f"\n  {'TOTAL':<40} Tests: {results['total_tests']:>3} "
              f"(Sync: {total_sync:>3}, Async: {total_async:>3})")

    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    all_present = len(results["missing_files"]) == 0
    status = "PASS" if all_present else "FAIL"
    print(f"\nValidation Status: {status}")
    print(f"Test Functions:    {results['total_tests']}")
    print(f"Test Classes:      {results['total_classes']}")
    print(f"Missing Files:     {len(results['missing_files'])}")

    if results['total_tests'] >= 200:
        print("\n✓ Test count meets target (200+)")
    else:
        print(f"\n✗ Test count below target (need {200 - results['total_tests']} more)")

    print("\n" + "=" * 80 + "\n")


def main() -> None:
    """Run test suite validation."""
    results = validate_test_structure()
    print_validation_results(results)

    # Exit with error code if validation failed
    if results["missing_files"]:
        exit(1)


if __name__ == "__main__":
    main()
