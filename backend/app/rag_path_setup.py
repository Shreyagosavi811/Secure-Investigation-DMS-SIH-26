"""
rag_path_setup.py

Adds the investigation_dataset_engine directory to sys.path so that
backend/app services can import from the rag.* package.

This MUST be imported before any rag.* imports.
"""

import sys
import os

def setup_rag_path() -> str:
    """
    Adds investigation_dataset_engine to sys.path.
    Safe to call multiple times (idempotent).
    Returns the resolved path.
    """
    # Resolve from this file's location: backend/app/ -> project root
    this_file = os.path.abspath(__file__)
    # backend/app/rag_path_setup.py -> backend/app -> backend -> project_root
    project_root = os.path.abspath(os.path.join(this_file, "../../../"))
    engine_path = os.path.join(project_root, "investigation_dataset_engine")

    if not os.path.isdir(engine_path):
        raise RuntimeError(
            f"investigation_dataset_engine not found at {engine_path}. "
            "Ensure you are running from the correct project root."
        )

    if engine_path not in sys.path:
        sys.path.insert(0, engine_path)

    return engine_path


# Auto-setup on import
_RAG_ENGINE_PATH = setup_rag_path()
