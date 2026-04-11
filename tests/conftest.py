#! python
"""
tests/conftest.py (pytest-prefer-nested-dup-tests)
"""

################################################################################
#region Imports

#===============================================================================
#region stdlib

from collections.abc import (
    Sequence,
)

#endregion stdlib
#===============================================================================

#endregion Imports
################################################################################

pytest_plugins: str | Sequence[str] = ["pytester"]
