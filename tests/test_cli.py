"""Tests for SuperOptiX CLI."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from superoptix.cli.utils import is_superoptix_project, validate_superoptix_project


def test_is_superoptix_project_with_super_file():
    """Test is_superoptix_project returns True when .super file exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .super file
        super_file = Path(temp_dir) / ".super"
        super_file.write_text("project: test\nversion: 0.1.0\n")

        # Change to the temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            assert is_superoptix_project() is True
        finally:
            os.chdir(original_cwd)


def test_is_superoptix_project_without_super_file():
    """Test is_superoptix_project returns False when .super file doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to the temp directory (no .super file)
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            assert is_superoptix_project() is False
        finally:
            os.chdir(original_cwd)


def test_validate_superoptix_project_with_super_file():
    """Test validate_superoptix_project doesn't raise when .super file exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .super file
        super_file = Path(temp_dir) / ".super"
        super_file.write_text("project: test\nversion: 0.1.0\n")

        # Change to the temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            # Should not raise an exception
            validate_superoptix_project()
        finally:
            os.chdir(original_cwd)


def test_validate_superoptix_project_without_super_file():
    """Test validate_superoptix_project raises SystemExit when .super file doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to the temp directory (no .super file)
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            with pytest.raises(SystemExit) as exc_info:
                validate_superoptix_project()
            assert exc_info.value.code == 1
        finally:
            os.chdir(original_cwd)


@patch("superoptix.cli.utils.console.print")
def test_validate_superoptix_project_error_message(mock_print):
    """Test that validate_superoptix_project shows appropriate error message."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to the temp directory (no .super file)
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            with pytest.raises(SystemExit):
                validate_superoptix_project()

            # Check that error message was printed
            mock_print.assert_called()
            # Get all calls and check if any contains the error message
            all_calls = [str(call) for call in mock_print.call_args_list]
            # Rich formatting includes tags, so check for the text content in any call
            assert any(
                "❌ Not in a SuperOptiX project directory" in str(call)
                for call in all_calls
            )
        finally:
            os.chdir(original_cwd)
