from pathlib import Path
import os
import pytest


def ensure_path_exists(path, required=True):
    """Validate that `path` exists on disk.

    - path: str or Path
    - required: if True, missing path raises pytest.fail (if TEST_PATH_STRICT=1) or pytest.skip otherwise.

    This helper centralizes clear messaging when tests reference files that are not
    present on the current developer's filesystem. It is intentionally conservative
    (defaults to skipping) to avoid breaking forks or CI where files may be
    intentionally absent.
    """
    p = Path(path)
    if p.exists():
        return True

    strict = os.getenv("TEST_PATH_STRICT", "0") in ("1", "true", "True")
    msg = f"Required test path does not exist: {p}"
    if required and strict:
        pytest.fail(msg)
    else:
        # Non-strict mode: skip the test so local differences don't cause hard failures
        pytest.skip(msg, allow_module_level=True)
