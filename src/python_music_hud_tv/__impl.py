"""
python-music-hud-tv
"""
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

###############################################################################
#region Imports

#===============================================================================
#region stdlib

from datetime import (
    datetime                            as datetime_datetime,
)

from http.server import (
    HTTPServer                      as http_server_HTTPServer,
    BaseHTTPRequestHandler          as http_server_BaseHTTPRequestHandler,
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
)

#endregion stdlib
#===============================================================================

#===============================================================================
#region third party

from ScriptingBridge import SBApplication  # type: ignore[reportGeneralTypesIssues,import]  # pylint: disable=no-name-in-module

#endregion third party
#===============================================================================

#endregion Imports
################################################################################

################################################################################
#region Constants

STATE_PLAYING = 1800426320
STATE_STOPPED = 1800426352

SERVER_PORT = 8080

BGCOLOR="#6E6856"
FGCOLOR="29,27,22"

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

g_app_apple_music: Any = SBApplication.applicationWithBundleIdentifier_("com.apple.Music")  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long
g_app_spotify: Any = SBApplication.applicationWithBundleIdentifier_("com.spotify.client")  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long

#endregion Globals
################################################################################


################################################################################
#region Public Functions

def commentToStyle(comment: str | None) -> str:
    """
    TODO
    """

    if comment is None:
        return ""

    comment = comment.split(";")[0]

    comment = comment\
        .replace("ECS", "East Coast Swing, Jitterbug")\
        .replace("WCS", "West Coast Swing")

    ret = "<li>" + comment.replace(",", "</li><li>") + "</li>" if comment else ""
    ret += "<li>Whatever Feels Right</li>"

    return ret

#endregion Public Functions
################################################################################

################################################################################
#region Public Classes

#===============================================================================
class Server(object):
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
        print("setting up server")

        self.thread = threading_Thread(
            target=self.serverThread,
            args=
            [
                handler_cls
            ]
        )
        self.thread.start()

    #---------------------------------------------------------------------------
    def serverThread(self, handler_cls: Any) -> None:
        """
        TODO
        """
        print("starting server")

        server = http_server_HTTPServer(('localhost', SERVER_PORT), handler_cls)

        while self.keep_running:
            server.handle_request()
        server.server_close()

        print("server closed")

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
        parsed_path = urllib_parse_urlparse(self.path)
        real_path = parsed_path.path
        # headers = self.headers

        current_track: Any
        current_playlist: Any
        playlist_tracks: Any

        current_title: str | None = ""
        current_artist: str | None = ""
        current_comment: str | None = ""
        current_length_pretty: str | None = ""
        current_position_and_length_pretty: str | None = ""
        current_dance_style_header: str | None = ""
        current_style: str | None = ""
        current_start: int = 0
        current_end: int = 0
        current_length_in_seconds: int = 0
        current_player_position_as_float: float = 0
        current_player_position_in_seconds: int = 0
        current_length_minutes: int = 0
        current_length_seconds: int = 0
        current_playlist_name: str = ""

        next_title: str | None = ""
        next_artist: str | None = ""
        next_style: str | None = ""
        next_length_pretty: str | None = ""
        next_dance_style_header: str | None = ""
        next_divider: str | None = ""
        next_header: str | None = ""

        next_next_title: str | None = ""
        next_next_comment: str | None = ""
        next_next_length_pretty: str | None = ""
        next_next_header: str | None = ""

        if real_path == "/STOP_SERVER":
            return
        elif g_app_apple_music is not None and g_app_apple_music.isRunning() and g_app_apple_music.playerState() == STATE_PLAYING:
            print("getting info from Apple Music App")
            current_track = g_app_apple_music.currentTrack()
            current_title = current_track.name()
            current_artist = current_track.artist()
            if current_artist:
                current_artist = "by " + current_artist
            current_comment = current_track.comment()
            current_style = commentToStyle(current_comment)
            current_index = current_track.index()

            current_start = current_track.start()
            current_end = current_track.finish()
            current_length_in_seconds = int(current_end - current_start)

            current_length_minutes = int(current_length_in_seconds / 60)
            current_length_seconds = int(current_length_in_seconds % 60)
            current_length_pretty = f"{current_length_minutes:d}:{current_length_seconds:02d}"

            current_player_position_in_seconds = g_app_apple_music.playerPosition()
            current_adjusted_player_position = max(current_player_position_in_seconds - current_start, 0)
            current_position_minutes = int(current_adjusted_player_position / 60)
            current_position_seconds = int(current_adjusted_player_position % 60)
            current_position_pretty = f"{current_position_minutes:d}:{current_position_seconds:02d}"

            current_position_and_length_pretty = f"{current_position_pretty}/{current_length_pretty}"

            current_playlist = g_app_apple_music.currentPlaylist()
            playlist_tracks = current_playlist.tracks()

            current_dance_style_header = "Dance Style Info:"

            next_title = "-"
            next_artist = ""
            next_style = ""
            next_length_pretty = ""
            next_dance_style_header = ""
            next_divider = "<hr>"
            next_header = "Next Up:"

            next_index = current_index + 1
            if next_index <= playlist_tracks.count():
                next_track = playlist_tracks[next_index - 1]  # b/c playlist index is offset, first is index -1
                next_title = next_track.name()
                next_artist = next_track.artist()
                if next_artist is not None:
                    next_artist = "by " + next_artist
                next_comment = next_track.comment()
                next_style = commentToStyle(next_comment)

                if next_title in SECRET_TITLES:
                    next_title = "*****"
                    next_artist = "*****"

                next_start = next_track.start()
                next_end = next_track.finish()
                next_length_seconds = int(next_end - next_start)

                next_length_minutes = int(next_length_seconds / 60)
                next_length_seconds = int(next_length_seconds % 60)
                next_length_pretty = f" - {next_length_minutes:d}:{next_length_seconds:02d}"

                next_dance_style_header = "Dance Style Info:"

            next_next_title = ""
            next_next_comment = ""
            next_next_length_pretty = ""
            next_next_header = ""

            next_next_index = current_index + 2
            if next_next_index <= playlist_tracks.count():
                next_next_track = playlist_tracks[next_next_index - 1]  # b/c playlist index is offset, first is index -1
                next_next_title = next_next_track.name()

                next_next_comment = next_next_track.comment()
                if next_next_comment is not None:
                    next_next_comment = next_next_comment.split(";")[0]
                    if next_next_comment:
                        next_next_comment += ", "
                    next_next_comment += "Whatever Feels Right"
                    next_next_comment = "<br/>" + next_next_comment\
                        .replace("ECS", "East Coast Swing, Jitterbug")\
                        .replace("WCS", "West Coast Swing")


                next_next_start = next_next_track.start()
                next_next_end = next_next_track.finish()
                next_next_length_seconds = int(next_next_end - next_next_start)

                next_next_length_minutes = int(next_next_length_seconds / 60)
                next_next_length_seconds = int(next_next_length_seconds % 60)
                next_next_length_pretty = f" - {next_next_length_minutes:d}:{next_next_length_seconds:02d}"

                next_next_header = "Followed by:<br/>"

                if next_next_title in SECRET_TITLES:
                    next_next_title = "*****"

            current_playlist_name = current_playlist.name()

            if (
                next_next_title == GAP_SILENCE_TITLE or
                next_title == GAP_SILENCE_TITLE or
                current_title == GAP_SILENCE_TITLE
            ):
                next_next_title = ""
                next_next_comment = ""
                next_next_length_pretty = ""
                next_next_header = ""

            if (
                next_title == GAP_SILENCE_TITLE or
                current_title == GAP_SILENCE_TITLE
            ):
                next_title = ""
                next_artist = ""
                next_style = ""
                next_length_pretty = ""
                next_dance_style_header = ""
                next_divider = ""
                next_header = ""
            elif next_title == LAST_DANCE_TITLE:
                next_header = "LAST DANCE:"

            if current_title == GAP_SILENCE_TITLE:
                current_title = ""
            elif current_title == LAST_CALL_TITLE:
                next_title = "<div class=\"bigTitle\">LAST CALL FOR ALCOHOL!</div>"
                next_artist = ""
                next_style = ""
                next_length_pretty = ""
                next_dance_style_header = ""
                next_divider = "<hr>"
                next_header = ""
                next_next_title = ""
                next_next_length_pretty = ""
                next_next_header = ""
                next_next_comment = ""
            elif current_title == LAST_DANCE_TITLE:
                next_title = "<div class=\"bigTitle\">THANK YOU FOR COMING!</div>"
                next_artist = ""
                next_style = ""
                next_length_pretty = ""
                next_dance_style_header = ""
                next_divider = "<hr>"
                next_header = ""
        elif g_app_spotify is not None and g_app_spotify.isRunning() and g_app_spotify.playerState() == STATE_PLAYING:
            print("getting info from Spotify App")
            current_playlist_name = "SPOTIFY"

            current_track = g_app_spotify.currentTrack()
            current_title = current_track.name()
            current_artist = current_track.artist()
            if current_artist:
                current_artist = "by " + current_artist

            current_length_in_seconds = current_track.duration() // 1000

            current_length_minutes = int(current_length_in_seconds / 60)
            current_length_seconds = int(current_length_in_seconds % 60)
            current_length_pretty = f"{current_length_minutes:d}:{current_length_seconds:02d}"

            current_player_position_as_float = g_app_spotify.playerPosition()
            current_adjusted_player_position = int(current_player_position_as_float)
            current_position_minutes = int(current_adjusted_player_position / 60)
            current_position_seconds = int(current_adjusted_player_position % 60)
            current_position_pretty = f"{current_position_minutes:d}:{current_position_seconds:02d}"

            current_position_and_length_pretty = f"{current_position_pretty}/{current_length_pretty}"
        else:
            print("no music app playing")

        if (
            not current_title or
            current_playlist_name not in DISPLAY_SONGS_FOR_PLAYLISTS
        ):
            next_next_title = next_title
            if not next_next_title or next_next_title == "-":
                next_next_title = ""
            else:
                next_next_title = "Next: " + next_next_title
            next_title = current_title
            if next_title:
                next_title = "<br/><br/><br/><br/><br/><br/><br/>Currently Playing: " + next_title + "<br/>" + next_next_title
            else:
                next_title = ""
            next_next_title = ""

            current_title = "<div class=\"bigTitle\"><br/>Mark<br/>&<br/>Sherry<br/>Wedding</div>"
            current_artist = ""
            current_position_and_length_pretty = ""
            current_dance_style_header = ""
            current_style = ""

            next_artist = ""
            next_style = ""
            next_length_pretty = ""
            next_dance_style_header = ""
            next_divider = ""
            next_header = ""

            next_next_comment = ""
            next_next_length_pretty = ""
            next_next_header = ""
        else:
            current_title = "<div class=\"title\">" + current_title + "</div>"


        real_time = datetime_datetime.now().strftime("%-I:%M:%S %p")

        message = (
            f"""
            <!DOCTYPE html>
            <html>
            <head>
            <html lang="en">
            <meta http-equiv="refresh" content="1" />
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
            <style>
                body {{
                    font-family: Big Caslon, -system, -system-font, Arial;
                    background-color: {BGCOLOR};
                    color: rgba({FGCOLOR}, 1);
                }}

                body table {{
                    margin: 0;
                    margin-left: 1%;
                    margin-right: 1%;
                }}

                ul {{
                    -webkit-column-count: 2;
                    margin: 0;
                    margin-left: 0.5em;
                }}

                li {{
                    margin-left: 0.5em;
                }}

                hr {{
                    border: 1px;
                    border-style: solid;
                    margin-top: 20px;
                    margin-bottom: 20px;
                }}

                .bottom {{
                    position: absolute;
                    top: 600px;
                    width: 1900px;
                }}
                .bottom-right {{
                    position: absolute;
                    top: 646px;
                    left: 1000px;
                    width: 800px;
                }}

                .currentTitle {{
                    font-size: 4vw;
                }}
                .currentTitle div.title {{
                    width: 68%;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }}
                .currentTitle div.time {{
                    position: absolute;
                    top: 1%;
                    right: 1%;
                }}
                .currentArtist {{
                    font-size: 2vw;
                    color: rgba({FGCOLOR}, 0.8);
                }}
                .currentStyleHeader {{
                    font-size: 2vw;
                    color: rgba({FGCOLOR}, 0.8);
                }}
                .currentStyle {{
                    font-size: 4.2vw;
                }}

                table.nextTable {{
                    color: rgba({FGCOLOR}, 0.7);
                }}

                table.nextNextTable {{
                    font-size: 1.5vw;
                    color: rgba({FGCOLOR}, 0.7);
                }}

                .headerNext {{
                    font-size: 2.5vw;
                }}
                .nextTitle {{
                    font-size: 2vw;
                }}
                .nextArtist {{
                    font-size: 1.5vw;
                }}
                .nextStyleHeader {{
                    font-size: 1.5vw;
                }}
                .nextStyle {{
                    font-size: 2vw;
                }}

                div.realTime {{
                    position: absolute;
                    bottom: 1%;
                    right: 1%;
                    font-size: 4vw;
                    color: rgba({FGCOLOR}, 0.4);
                }}

                div.bigTitle {{
                    font-size: 7.5vw;
                    text-align: center;
                    width: 100%;
                }}
            </style>
            </head>
            <body><div max-width="100%">
                <table width="98%">
                    <tr><td class="currentTitle">
                        <div class="time">{current_position_and_length_pretty}</div>
                        {current_title}
                    </td></tr>
                </table>
                <table width="98%">
                    <tr><td class="currentArtist">
                        {current_artist}
                    </td></tr>
                    <tr><td class="currentStyleHeader">
                        {current_dance_style_header}
                    </td></tr>
                    <tr><td class="currentStyle">
                        <ul>
                            {current_style}
                        </ul>
                    </td></tr>
                </table>
                <div class="bottom">
                    {next_divider}
                    <table class="nextTable">
                        <tr>
                            <td class="headerNext">
                                {next_header}
                            </td>
                        </tr>
                        <tr><td class="nextTitle">
                            {next_title} {next_length_pretty}
                        </td></tr>
                        <tr><td class="nextArtist">
                            {next_artist}
                        </td></tr>
                        <tr><td class="nextStyleHeader">
                            {next_dance_style_header}
                        </td></tr>
                        <tr><td class="nextStyle">
                            <ul>
                                {next_style}
                            </ul>
                        </td></tr>
                    </table>
                </div>
                <div class="bottom-right">
                    <table class="nextNextTable">
                        <tr>
                            <td>
                                {next_next_header} {next_next_title} {next_next_length_pretty} {next_next_comment}
                            </td>
                        </tr>
                    </table>
                </div>
                <div class="realTime">
                    {real_time}
                </div>
            </div></body>
            </html>
            """
        )

        message_bytes = message.encode("utf8", errors="ignore")
        self.send_response(200)
        self.end_headers()
        _ = self.wfile.write(message_bytes)
        return

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
