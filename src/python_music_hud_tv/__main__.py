#!/usr/bin/env python
"""
TODO
"""
################################################################################
#region __main__.py Preamble

# insert our repo base dir into the sys.path so that we can import our library
# we know that the repo path is ./../.. b/c we should be in ./src/<project name>/
import sys
import os
import os.path as os_path
MY_DIR_FULLPATH = os_path.dirname(__file__)
MY_REPO_FULLPATH = os_path.dirname(os_path.dirname(MY_DIR_FULLPATH))
sys.path.insert(0, MY_REPO_FULLPATH)
MY_LIB_FULLPATH = os_path.join(MY_REPO_FULLPATH, "src")
sys.path.insert(0, MY_LIB_FULLPATH)

MY_PROGRAM_NAME = os.environ.get("BFI_ORIGINAL_EXEC_NAME", os_path.basename(sys.argv[0]))
if (  # pragma: no cover
    "." not in os_path.basename(MY_PROGRAM_NAME) or
    ".py" in os_path.basename(MY_PROGRAM_NAME)
):
    MY_PROGRAM_NAME = os_path.basename(MY_PROGRAM_NAME)  # type: ignore[reportConstantRedefinition]  # noqa: E501,B950  # pragma: no cover
del os
del os_path

#endregion __main__.py Preamble
################################################################################

################################################################################
#region Imports

#===============================================================================
#region ours (internal)

from python_music_hud_tv import (
    MusicHudServer                  as python_music_hud_tv_MusicHudServer,
)

#endregion ours (internal)
#===============================================================================

#endregion Imports
################################################################################

################################################################################
#region Private Functions

#-------------------------------------------------------------------------------
def __main(argv: list[str]) -> int:
    """
    TODO
    """

    # ignore unused args
    argv = argv  # pylint: disable=self-assigning-variable

    # TODO: remove dorky logging hack, take real args to config logging
    # pylint: disable=import-outside-toplevel
    from logging import (
        basicConfig                     as logging_basicConfig,
    )
    logging_basicConfig(level=1)

    server = python_music_hud_tv_MusicHudServer()
    server.runServer()

    return 0

#endregion Private Functions
################################################################################

################################################################################
#region Script Entry Point

#-------------------------------------------------------------------------------
def scriptEntryPoint() -> None:  # pragma: no cover
    """
    Script entry point. Used by tool.poetry.scripts.

    Returns:
        int: return code
    """
    ret = __main(sys.argv[1:])
    sys.exit(ret)

#endregion Script Entry Point
################################################################################

################################################################################
#region Immediate

#-------------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    scriptEntryPoint()

#endregion Immediate
################################################################################
