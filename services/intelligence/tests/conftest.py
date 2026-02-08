import sys
from unittest.mock import MagicMock

# Mock asyncpg to avoid installation requirements (compilation on Windows)
sys.modules["asyncpg"] = MagicMock()
