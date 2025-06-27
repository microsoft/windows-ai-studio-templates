#!/usr/bin/env python3
"""
Sanitize script - new modular version
This script maintains compatibility with the original sanitize.py while using the new modular structure.
"""

import sys
import os
from pathlib import Path

# Get the absolute path to the project root (parent of scripts)
project_root = Path(__file__).parent.parent
scripts_dir = Path(__file__).parent

# Add both the project root and scripts directory to Python path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(scripts_dir))

# Import the main function from the new sanitize.main module
from sanitize.main import main

if __name__ == "__main__":
    main()
