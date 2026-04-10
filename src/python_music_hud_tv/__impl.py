"""
python-music-hud-tv
"""
# flake8: noqa=D101
################################################################################
#region Python Library Preamble

# we know that the repo path is ./../../ b/c we should be in ./src/<project name>/
import sys
import os.path as os_path
MY_DIR_FULLPATH = os_path.dirname(__file__)
MY_REPO_FULLPATH = os_path.dirname(os_path.dirname(MY_DIR_FULLPATH))
del os_path

from logging import (  # noqa: F401
    FATAL                           as logging_FATAL,
    getLogger                       as logging_getLogger,
)
logger = logging_getLogger(__name__)
logger_log = logger.log

#endregion Python Library Preamble
################################################################################

# TODO: refactor the globals to remove them
# TODO: re-enable flake8 D101

###############################################################################
#region Imports

#===============================================================================
#region stdlib

from datetime import (
    datetime                        as datetime_datetime,
)
from http.server import (
    HTTPServer                      as http_server_HTTPServer,
    BaseHTTPRequestHandler          as http_server_BaseHTTPRequestHandler,
)
from pathlib import (
    Path                            as pathlib_Path,
)
from threading import (
    Thread                          as threading_Thread,
)
from urllib.parse import (
    urlparse                        as urllib_parse_urlparse,
)
from typing import (
    Any,
    Type,
    TypedDict,
)

#endregion stdlib
#===============================================================================

#===============================================================================
#region third party

from ScriptingBridge import SBApplication  # type: ignore[reportGeneralTypesIssues,import]  # pylint: disable=no-name-in-module,import-error  # noqa: E501,B950

#endregion third party
#===============================================================================

#endregion Imports
################################################################################

################################################################################
#region Types

class Track(TypedDict):
    title: str
    artist: str
    duration_in_seconds: int
    duration_pretty: str
    grouping: str
    comment: str

class _MusicData_Songs(TypedDict):
    current: Track
    next: Track
    next_next: Track

class MusicData(TypedDict):
    current_play_head_time_in_seconds: int
    current_play_head_time_pretty: str
    current_play_head_time_and_length_pretty: str
    current_playlist_name: str
    songs: _MusicData_Songs

class PageData(TypedDict):
    current_dance_style_header: str
    next_divider: str
    next_header: str
    next_dance_style_header: str
    next_next_header: str
    real_time: str

Application = Any
AppleMusicTrack = Any
SpotifyTrack = Any

# pylint: disable=invalid-name
html = str

#endregion Types
################################################################################

################################################################################
#region Constants

STATE_PLAYING = 1800426320
STATE_STOPPED = 1800426352

SERVER_PORT = 8080

BACKGROUND_COLOR = "#6E6856"
FOREGROUND_COLOR = "29,27,22"
EVENT_TITLE_HTML = "Mark<br/>&<br/>Sherry<br/>Wedding"

SECRET_TITLES = [
    "Sherry",
    "Never Gonna Give You Up (7\" Mix)",
]

DISPLAY_SONGS_FOR_PLAYLISTS = [
    "SPOTIFY",
    "9 Pre Dance - 30m (6:30p)",
    "10 Main Dance - 1h (8p)",
    "11 Extra Dance - 1h (?)",
    "12 Last Call - 30m (9p)",
    "13 GTFO - 30m (9:30p)",
    "14 Cleanup - 2h (10:15p)",
    "5a Dance (8:10p, <3h)",
    "5b Last Dances (10:45pm)",
]

GAP_SILENCE_TITLE = "----- 30 Minutes of Silence -----"

LAST_CALL_TITLE = "Last Call (One Bourbon, One Scotch, One Beer)"

LAST_DANCE_TITLE = "(I've Had) The Time of My Life"

#endregion Constants
################################################################################

################################################################################
#region Globals

g_app_apple_music: Any = SBApplication.applicationWithBundleIdentifier_("com.apple.Music")  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long  # noqa: E501,B950
g_app_spotify: Any = SBApplication.applicationWithBundleIdentifier_("com.spotify.client")  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long  # noqa: E501,B950

#endregion Globals
################################################################################


################################################################################
#region Public Functions

def durationInSecondsToPretty(duration_in_seconds: int) -> str:
    minutes = int(duration_in_seconds / 60)
    seconds = int(duration_in_seconds % 60)
    length_pretty = f"{minutes:d}:{seconds:02d}"
    return length_pretty

def getApp(name: str) -> Application:
    return SBApplication.applicationWithBundleIdentifier_(name)  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long  # noqa: E501,B950

def appleMusicTrackToOurTrack(track: AppleMusicTrack) -> Track:
    ret_track: Track = {
        "title": "",
        "artist": "",
        "duration_in_seconds": 0,
        "duration_pretty": "",
        "grouping": "",
        "comment": "",
    }

    if track and track.name():
        length = int(track.finish() - track.start())
        ret_track = {
            "title": str(track.name()),
            "artist": str(track.artist()),
            "duration_in_seconds": length,
            "duration_pretty": durationInSecondsToPretty(length),
            "grouping": str(track.grouping()),
            "comment": str(track.comment()),
        }

    return ret_track

def appleMusicGetPlaylistName() -> str:
    ret_name = ""

    app_apple_music = getApp("com.apple.Music")

    if (
        app_apple_music is not None and
        app_apple_music.isRunning() and
        app_apple_music.playerState() == STATE_PLAYING
    ):
        app_apple_music_playlist = app_apple_music.currentPlaylist()
        if app_apple_music_playlist:
            ret_name = app_apple_music_playlist.name()

    return ret_name

def appleMusicGetCurrentPlayHeadTimeInSeconds() -> int:
    ret_time = 0

    app_apple_music = getApp("com.apple.Music")

    if (
        app_apple_music is not None and
        app_apple_music.isRunning() and
        app_apple_music.playerState() == STATE_PLAYING
    ):
        raw_time = app_apple_music.playerPosition()

        # adjust raw_time by track start time b/c the track can start playing
        # from a time greater than 0, such as if skipping a long silence or intro
        current_track = g_app_apple_music.currentTrack()
        current_start = current_track.start()

        cooked_time = raw_time - current_start
        ret_time = max(cooked_time, 0)

    return ret_time

def appleMusicGetCurrentTrack() -> Track:
    app_apple_music = getApp("com.apple.Music")

    app_apple_music_track: AppleMusicTrack = None
    if (
        app_apple_music is not None and
        app_apple_music.isRunning() and
        app_apple_music.playerState() == STATE_PLAYING
    ):
        app_apple_music_track = app_apple_music.currentTrack()

    ret_track = appleMusicTrackToOurTrack(app_apple_music_track)

    return ret_track

def appleMusicGetNextTrack(offset: int = 1) -> Track:
    app_apple_music = getApp("com.apple.Music")

    app_apple_music_track: AppleMusicTrack = None
    if (
        app_apple_music is not None and
        app_apple_music.isRunning() and
        app_apple_music.playerState() == STATE_PLAYING
    ):
        app_apple_music_playlist = app_apple_music.currentPlaylist()
        if app_apple_music_playlist:
            current_track = g_app_apple_music.currentTrack()
            current_index = current_track.index()
            playlist_tracks = app_apple_music_playlist.tracks()
            next_index = current_index + offset
            app_apple_music_track = playlist_tracks[next_index - 1]  # b/c playlist index is offset, first is index -1  # noqa: E501,B950

    ret_track = appleMusicTrackToOurTrack(app_apple_music_track)

    return ret_track

def spotifyGetCurrentPlayHeadTimeInSeconds() -> int:
    ret_time = 0

    app_spotify = getApp("com.spotify.client")

    if (
        app_spotify is not None and
        app_spotify.isRunning() and
        app_spotify.playerState() == STATE_PLAYING
    ):
        ret_time = int(app_spotify.playerPosition())

    return ret_time

def spotifyGetCurrentTrack() -> Track:
    ret_track: Track = {
        "title": "",
        "artist": "",
        "duration_in_seconds": 0,
        "duration_pretty": "",
        "grouping": "",
        "comment": "",
    }

    app_spotify = getApp("com.spotify.client")

    if (
        app_spotify is not None and
        app_spotify.isRunning() and
        app_spotify.playerState() == STATE_PLAYING
    ):
        track = app_spotify.currentTrack()
        length = track.duration() // 1000
        ret_track = {
            "title": track.name(),
            "artist": track.artist(),
            "duration_in_seconds": length,
            "duration_pretty": durationInSecondsToPretty(length),
            "grouping": "",
            "comment": "",
        }

    return ret_track

def getMusicData() -> MusicData:
    """
    TODO
    """

    music_data: MusicData = {
        "current_play_head_time_in_seconds": 0,
        "current_play_head_time_pretty": "",
        "current_play_head_time_and_length_pretty": "",
        "current_playlist_name": "",
        "songs": {
            "current": {
                "title": "",
                "artist": "",
                "duration_in_seconds": 0,
                "duration_pretty": "",
                "grouping": "",
                "comment": "",
            },
            "next": {
                "title": "",
                "artist": "",
                "duration_in_seconds": 0,
                "duration_pretty": "",
                "grouping": "",
                "comment": "",
            },
            "next_next": {
                "title": "",
                "artist": "",
                "duration_in_seconds": 0,
                "duration_pretty": "",
                "grouping": "",
                "comment": "",
            },
        },
    }

    if (
        g_app_apple_music is not None and
        g_app_apple_music.isRunning() and
        g_app_apple_music.playerState() == STATE_PLAYING
    ):
        logger.debug("getting info from Apple Music App")
        music_data["songs"]["current"] = appleMusicGetCurrentTrack()
        music_data["songs"]["next"] = appleMusicGetNextTrack()
        music_data["songs"]["next_next"] = appleMusicGetNextTrack(offset=2)
        music_data["current_play_head_time_in_seconds"] = \
            appleMusicGetCurrentPlayHeadTimeInSeconds()
        music_data["current_playlist_name"] = appleMusicGetPlaylistName()
    elif (
        g_app_spotify is not None and
        g_app_spotify.isRunning() and
        g_app_spotify.playerState() == STATE_PLAYING
    ):
        logger.debug("getting info from Spotify App")
        music_data["songs"]["current"] = spotifyGetCurrentTrack()
        music_data["current_play_head_time_in_seconds"] = \
            spotifyGetCurrentPlayHeadTimeInSeconds()
    else:
        logger.debug("no music app playing")

    music_data["current_play_head_time_pretty"] = \
        durationInSecondsToPretty(music_data["current_play_head_time_in_seconds"])

    music_data["current_play_head_time_and_length_pretty"] = \
        f'{music_data["current_play_head_time_pretty"]}/{music_data["songs"]["current"]["duration_pretty"]}'

    return music_data


def commentToStyle(comment: str | None) -> str:
    """
    TODO
    """

    if not comment:
        return ""

    comment = comment.split(";")[0]

    comment = (
        comment
        .replace("ECS", "East Coast Swing, Jitterbug")
        .replace("WCS", "West Coast Swing")
    )

    ret = "<li>" + comment.replace(",", "</li><li>") + "</li>" if comment else ""
    ret += "<li>Whatever Feels Right</li>"

    return ret

#endregion Public Functions
################################################################################

################################################################################
#region Public Classes

#===============================================================================
class Server():
    """
    TODO
    """

    keep_running = True
    thread: threading_Thread | None = None
    test_case: Any = None

    # #-------------------------------------------------------------------------
    # def __init__(self):
    #     pass

    #---------------------------------------------------------------------------
    def runServer(self, handler_cls: Type[http_server_BaseHTTPRequestHandler]) -> None:
        """
        TODO
        """

        logger.debug("setting up server")

        self.thread = threading_Thread(
            target=self.serverThread,
            args=[
                handler_cls,
            ],
        )
        self.thread.start()

    #---------------------------------------------------------------------------
    def serverThread(self, handler_cls: Any) -> None:
        """
        TODO
        """

        logger.debug("starting server")

        server = http_server_HTTPServer(("localhost", SERVER_PORT), handler_cls)

        while self.keep_running:
            server.handle_request()
        server.server_close()

        logger.debug("server closed")

    #---------------------------------------------------------------------------
    def stopServer(self) -> None:
        """
        TODO
        """

        self.keep_running = False
        if self.thread is not None:
            self.thread.join()

#===============================================================================
# noinspection PyClassHasNoInit
class GenericHandler(http_server_BaseHTTPRequestHandler):
    """
    TODO
    """

    #---------------------------------------------------------------------------
    def do_GET(self) -> None:  # pylint: disable=invalid-name
        """
        TODO
        """
        # pylint: disable=possibly-unused-variable

        parsed_path = urllib_parse_urlparse(self.path)
        real_path = parsed_path.path
        # headers = self.headers

        if real_path == "/STOP_SERVER":
            return

        music_data = getMusicData()

        page_data : PageData = {  # pyright: ignore[reportUnusedVariable]
            "current_dance_style_header": "",
            "next_divider": "",
            "next_header": "",
            "next_dance_style_header": "",
            "next_next_header": "",
            "real_time": "",
        }

        if music_data["songs"]["next_next"]["title"] in SECRET_TITLES:
            music_data["songs"]["next_next"]["title"] = "*****"
        elif (
            GAP_SILENCE_TITLE in (
                music_data["songs"]["next_next"]["title"],
                music_data["songs"]["next"]["title"],
                music_data["songs"]["current"]["title"],
            )
        ):
            music_data["songs"]["next_next"]["title"] = ""
            music_data["songs"]["next_next"]["duration_pretty"] = ""
            music_data["songs"]["next_next"]["comment"] = ""

        if music_data["songs"]["next"]["title"] in SECRET_TITLES:
            music_data["songs"]["next"]["title"] = "*****"
            music_data["songs"]["next"]["artist"] = "*****"
        elif (
            GAP_SILENCE_TITLE in (
                music_data["songs"]["next"]["title"],
                music_data["songs"]["current"]["title"],
            )
        ):
            music_data["songs"]["next"]["title"] = ""
            music_data["songs"]["next"]["artist"] = ""
            music_data["songs"]["next"]["duration_pretty"] = ""
            music_data["songs"]["next"]["comment"] = ""

        if music_data["songs"]["current"]["title"] == GAP_SILENCE_TITLE:
            music_data["songs"]["current"]["title"] = ""
            music_data["songs"]["current"]["artist"] = ""
            music_data["songs"]["current"]["comment"] = ""

        if (
            music_data["songs"]["current"]["title"] in (
                LAST_CALL_TITLE,
                LAST_DANCE_TITLE,
            )
        ):
            music_data["songs"]["next"]["title"] = ""
            music_data["songs"]["next"]["artist"] = ""
            music_data["songs"]["next"]["duration_pretty"] = ""
            music_data["songs"]["next"]["comment"] = ""

            music_data["songs"]["next_next"]["title"] = ""
            music_data["songs"]["next_next"]["duration_pretty"] = ""
            music_data["songs"]["next_next"]["comment"] = ""

            page_data["next_dance_style_header"] = ""  # pyright: ignore[reportUnusedVariable]
            page_data["next_header"] = ""  # pyright: ignore[reportUnusedVariable]
            page_data["next_next_header"] = ""  # pyright: ignore[reportUnusedVariable]
            page_data["next_divider"] = "<hr>"  # pyright: ignore[reportUnusedVariable]

        music_data["songs"]["current"]["comment"] = commentToStyle(music_data["songs"]["current"]["comment"])

        if music_data["songs"]["current"]["title"]:
            current_dance_style_header = "Dance Style Info:"  # pyright: ignore[reportUnusedVariable]
        else:
            music_data["current_play_head_time_and_length_pretty"] = ""

        if music_data["songs"]["next"]["title"]:
            music_data["songs"]["next"]["comment"] = commentToStyle(music_data["songs"]["next"]["comment"])

            page_data["next_divider"] = "<hr>"  # pyright: ignore[reportUnusedVariable]
            page_data["next_header"] = "Next Up:"  # pyright: ignore[reportUnusedVariable]
            page_data["next_dance_style_header"] = "Dance Style Info:"  # pyright: ignore[reportUnusedVariable]

            if music_data["songs"]["next"]["title"] == LAST_DANCE_TITLE:
                page_data["next_header"] = "LAST DANCE:"  # pyright: ignore[reportUnusedVariable]

            if music_data["songs"]["next"]["artist"]:
                music_data["songs"]["next"]["artist"] = f'by {music_data["songs"]["next"]["artist"]}'

        if music_data["songs"]["next_next"]["title"]:
            music_data["songs"]["next_next"]["comment"] = commentToStyle(music_data["songs"]["next_next"]["comment"])

            page_data["next_next_header"] = "Followed by:<br/>"  # pyright: ignore[reportUnusedVariable]

        if music_data["songs"]["current"]["title"] == LAST_CALL_TITLE:
            music_data["songs"]["next"]["title"] = "<div class=\"bigTitle\">LAST CALL FOR ALCOHOL!</div>"
        elif music_data["songs"]["current"]["title"] == LAST_DANCE_TITLE:
            music_data["songs"]["next"]["title"] = "<div class=\"bigTitle\">THANK YOU FOR COMING!</div>"

        current_playlist_name: str = music_data["current_playlist_name"]
        if (
            not music_data["songs"]["current"]["title"] or
            current_playlist_name not in DISPLAY_SONGS_FOR_PLAYLISTS
        ):
            music_data["songs"]["next_next"]["title"] = music_data["songs"]["next"]["title"]
            if not music_data["songs"]["next_next"]["title"]:
                music_data["songs"]["next_next"]["title"] = ""
            else:
                music_data["songs"]["next_next"]["title"] = "Next: " + music_data["songs"]["next_next"]["title"]
            music_data["songs"]["next"]["title"] = music_data["songs"]["current"]["title"]
            if music_data["songs"]["next"]["title"]:
                music_data["songs"]["next"]["title"] = (
                    "<br/><br/><br/><br/><br/><br/><br/>" +
                    f'Currently Playing:{music_data["songs"]["next"]["title"]}<br/>{music_data["songs"]["next_next"]["title"]}'
                )
            else:
                music_data["songs"]["next"]["title"] = ""
            music_data["songs"]["next_next"]["title"] = ""

            music_data["songs"]["current"]["title"] = (
                f'<div class="bigTitle"><br/>{EVENT_TITLE_HTML}</div>'
            )

            music_data["songs"]["current"]["artist"] = ""
            music_data["songs"]["current"]["comment"] = ""

            music_data["current_play_head_time_and_length_pretty"] = ""

            music_data["songs"]["next"]["artist"] = ""
            music_data["songs"]["next"]["duration_pretty"] = ""
            music_data["songs"]["next"]["comment"] = ""

            music_data["songs"]["next_next"]["title"] = ""
            music_data["songs"]["next_next"]["duration_pretty"] = ""
            music_data["songs"]["next_next"]["comment"] = ""

            page_data["current_dance_style_header"] = ""  # pyright: ignore[reportUnusedVariable]
            page_data["next_dance_style_header"] = ""  # pyright: ignore[reportUnusedVariable]
            page_data["next_divider"] = ""  # pyright: ignore[reportUnusedVariable]
            page_data["next_header"] = ""  # pyright: ignore[reportUnusedVariable]
            page_data["next_next_header"] = ""  # pyright: ignore[reportUnusedVariable]
        else:
            music_data["songs"]["current"]["title"] = f'<div class="title">{music_data["songs"]["current"]["title"]}</div>'

        if music_data["songs"]["current"]["artist"]:
            music_data["songs"]["current"]["artist"] = f'by {music_data["songs"]["current"]["artist"]}'

        page_data["real_time"] = datetime_datetime.now().strftime("%-I:%M:%S %p")  # pyright: ignore[reportUnusedVariable]

        with open(pathlib_Path(MY_DIR_FULLPATH + "/hud.html.j2"), "rt", encoding="utf8") as f:
            raw_message = f.read()

        message = raw_message.format_map({**globals(), **locals()})

        message_bytes = message.encode("utf8", errors="ignore")
        self.send_response(200)
        self.end_headers()
        _ = self.wfile.write(message_bytes)
        return

    #---------------------------------------------------------------------------
    def log_message(
        self,
        format: str,  # pylint: disable=redefined-builtin
        *args: list[Any],
    ) -> None:
        """Log an arbitrary message.

        This is used by all other logging functions.  Override
        it if you have specific logging wishes.

        The first argument, FORMAT, is a format string for the
        message to be logged.  If the format string contains
        any % escapes requiring parameters, they should be
        specified as subsequent arguments (it's just like
        printf!).

        The client ip and current date/time are prefixed to
        every message.

        """
        formatted_args = format%args

        message = f"{self.address_string()} - - [{self.log_date_time_string()}] {formatted_args}"

        logger.info(message)

#endregion Public Classes
################################################################################

################################################################################
#region Private Functions

#-------------------------------------------------------------------------------
def __main(argv: list[str]) -> int:
    """
    Entry point.

    Args:
        argv (list[str]): command line arguments

    Returns:
        int: return code
    """
    # ignore unused vars from func signature
    argv = argv  # pylint: disable=self-assigning-variable

    logger_log(logging_FATAL, "This module should not be run directly.")

    return 1

#endregion Private Functions
################################################################################

################################################################################
#region Immediate

if __name__ == "__main__":  # pragma: no cover
    __ret = __main(sys.argv[1:])  # pylint: disable=invalid-name
    sys.exit(__ret)

#endregion Immediate
################################################################################
