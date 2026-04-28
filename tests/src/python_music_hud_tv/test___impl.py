#! python
"""
tests/test___impl.py (pytest-prefer-nested-dup-tests)
"""

################################################################################
#region Imports

#===============================================================================
#region stdlib

# import sys
from typing import (
    Any,
)

#endregion stdlib
#===============================================================================

#endregion Imports
################################################################################

################################################################################
#region Types

PytestFixture = Any

#endregion Types
################################################################################

################################################################################
#region Tests


def test___main(testdir: PytestFixture) -> None:
    """
    test___main: simple test to confirm this subpackage of tests loads

    Args:
        testdir (PytestFixture):
    """

    testdir = testdir  # ignore unused arg in sig  ## pylint: disable=self-assigning-variable ## noqa: E501

    print("asdf")

    assert True


#endregion Tests
################################################################################
