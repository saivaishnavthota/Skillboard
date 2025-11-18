"""Uvicorn configuration to avoid memory issues with file watching."""
import os

# Limit file watching to app directory only to reduce memory usage
reload_dirs = ["/app/app"] if os.path.exists("/app/app") else ["/app"]
reload_includes = ["*.py"]
reload_excludes = [
    "*.pyc",
    "__pycache__",
    ".git",
    "*.log",
    "venv",
    "env",
    ".venv",
]

