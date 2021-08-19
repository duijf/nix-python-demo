import os
import pathlib
import sys

import pytest

PROJECT_ROOT = pathlib.Path(os.environ["PROJECT_ROOT"])
sys.path.append(str(PROJECT_ROOT / "backend"))

pytest.main()
