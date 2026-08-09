import sys
from pathlib import Path

from backend.bootstrap import ensure_project_root_on_path


def test_ensure_project_root_on_path_adds_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path[:] = [entry for entry in sys.path if entry not in {"", str(repo_root)}]

    ensure_project_root_on_path()

    assert str(repo_root) in sys.path
