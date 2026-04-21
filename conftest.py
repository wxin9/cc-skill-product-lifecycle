"""
Pytest conftest.py — adds project root to sys.path so that
`from scripts.core.xxx import Xxx` works without needing PYTHONPATH.
"""
import sys
from pathlib import Path

# Add the project root (the directory containing this conftest.py) to sys.path
sys.path.insert(0, str(Path(__file__).parent))
