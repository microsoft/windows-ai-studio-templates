#!/usr/bin/env python3
"""
Sanitize script - new modular version
This script maintains compatibility with the original sanitize.py while using the new modular structure.
Auto-formats all Python scripts in the scripts directory on every run.
"""

import sys
import os
import subprocess
from pathlib import Path

# Get the absolute path to the project root (parent of scripts)
project_root = Path(__file__).parent.parent
scripts_dir = Path(__file__).parent

# Add both the project root and scripts directory to Python path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(scripts_dir))


def auto_format_scripts():
    """
    Auto-format all Python scripts in the scripts directory using black with 120 character line length.
    """
    print("Auto-formatting Python scripts in scripts directory...")

    # Find all Python files in the scripts directory
    python_files = []
    for py_file in scripts_dir.rglob("*.py"):
        if py_file.is_file():
            python_files.append(str(py_file))

    if not python_files:
        print("No Python files found to format.")
        return

    try:
        # Check if black is installed
        subprocess.run(["black", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing black formatter...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "black"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install black: {e}")
            return

    # Format all Python files with black
    try:
        cmd = ["black", "--line-length", "120"] + python_files
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Successfully formatted {len(python_files)} Python files with 120 character line length.")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"Black formatting failed: {result.stderr}")
    except Exception as e:
        print(f"Error during formatting: {e}")


# Import the main function from the new sanitize.main module
from sanitize.main import main

if __name__ == "__main__":
    # Auto-format scripts before running sanitize
    auto_format_scripts()
    main()
