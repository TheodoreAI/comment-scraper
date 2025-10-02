#!/usr/bin/env python3
"""
YouTube Comment Scraper - Main Entry Point

This launcher script handles the import paths correctly and runs the main application.
"""

import sys
import os
from pathlib import Path

# Add the project root and src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# Set the PYTHONPATH environment variable
os.environ['PYTHONPATH'] = f"{project_root}:{src_path}:{os.environ.get('PYTHONPATH', '')}"

# Now import and run the main module
if __name__ == "__main__":
    from src.main import main
    sys.exit(main())
