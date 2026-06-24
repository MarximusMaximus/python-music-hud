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

# TODO: animated time bar
# TODO: static lyrics
# TODO: timed by line lyrics
# TODO: timed by word lyrics
# TODO: asyncio http server?
# TODO: websockets?

################################################################################
#region Imports

#===============================================================================
#region stdlib

from copy import (
    deepcopy                        as copy_deepcopy,
)
from dataclasses import (
    asdict,                         # as asdict,  # intentionally using short name
    dataclass,                      # as dataclass,  # intentionally using short name
)
from functools import (
    lru_cache                       as functools_lru_cache,
)
from http import (
    HTTPStatus                      as http_HTTPStatus,
)
from http.server import (
    HTTPServer                      as http_server_HTTPServer,
    BaseHTTPRequestHandler          as http_server_BaseHTTPRequestHandler,
)
from json import (
    dumps                           as json_dumps,
    loads                           as json_loads,
)
from os import (
    PathLike                        as os_PathLike,
)
from pathlib import (
    Path                            as pathlib_Path,
)
from threading import (
    Thread                          as threading_Thread,
)
from time import (
    sleep                           as time_sleep,
    time                            as time_time,
)
from typing import (
    Any,                            # as Any,  # intentionally using short name
    # Type,                           # as Type,  # intentionally using short name
    # TypedDict,                      # as TypedDict,  # intentionally using short name
)
from urllib.parse import (
    urlparse                        as urllib_parse_urlparse,
)

#endregion stdlib
#===============================================================================

#===============================================================================
#region third party

from ScriptingBridge import SBApplication  # type: ignore[reportGeneralTypesIssues,import]  # pylint: disable=no-name-in-module,import-error  # noqa: E501,B950
from Foundation import NSAutoreleasePool  # type: ignore[reportGeneralTypesIssues,import]  # pylint: disable=no-name-in-module,import-error  # noqa: E501,B950

#endregion third party
#===============================================================================

#endregion Imports
################################################################################

################################################################################
#region Types

@dataclass
class MusicHudConfig:
    server_port: int
    updates_per_second: int
    event_title_html: str
    background_color: str
    foreground_color: str
    secret_titles: list[str]
    display_songs_for_playlists: list[str]
    gap_silence_title: str
    lower_third_message_songs: dict[str, str]

@dataclass
class Track:
    title: str = ""
    artist: str = ""
    duration_in_seconds: int = 0
    grouping: str = ""
    comment: str = ""

@dataclass
class MusicData:
    current_wall_unix_timestamp_ms: int
    current_play_head_time_in_seconds: int
    current_playlist_name: str
    current: Track
    next: Track
    next_next: Track

@dataclass
class PageData:
    current_dance_style_header: str
    next_divider: str
    next_header: str
    next_dance_style_header: str
    next_next_header: str
    real_time: str

Application = Any
AppleMusicTrack = Any
AppleMusicPlaylist = Any

# pylint: disable=invalid-name
html = str

# referenced loosely from ~/.vscode/extensions/ms-python.vscode-pylance-2026.2.1/dist/typeshed-fallback/stdlib/builtins.pyi  # pylint: disable=line-too-long  # noqa: E501,B950,W505
StrOrBytesPath = str | bytes | os_PathLike[str] | os_PathLike[bytes]  # stable
FileDescriptorOrPath = int | StrOrBytesPath

#endregion Types
################################################################################

################################################################################
#region Constants

APPLE_MUSIC_STATE_PLAYING = 1800426320
APPLE_MUSIC_STATE_STOPPED = 1800426352

DEFAULT_CONFIG = MusicHudConfig(
    server_port=8080,
    updates_per_second=10,
    event_title_html="<br/>Mark<br/>&<br/>Sherry<br/>Wedding",
    background_color="#6E6856",
    foreground_color="#1d1b16",
    secret_titles=[
        "Sherry",
        "Never Gonna Give You Up (7\" Mix)",
    ],
    display_songs_for_playlists=[
        "9 Pre Dance - 30m (6:30p)",
        "10 Main Dance - 1h (8p)",
        "11 Extra Dance - 1h (?)",
        "12 Last Call - 30m (9p)",
        "13 GTFO - 30m (9:30p)",
        "14 Cleanup - 2h (10:15p)",
        "5a Dance (8:10p, <3h)",
        "5b Last Dances (10:45pm)",
    ],
    gap_silence_title="----- 30 Minutes of Silence -----",
    lower_third_message_songs={
        "\"Last Call\" (One Bourbon, One Scotch, One Beer; Mark Cut)":
            "LAST CALL FOR ALCOHOL!",
        "(I've Had) The Time of My Life": "THANK YOU FOR COMING!",
    },
)

EMPTY_TRACK_DATA_DICT = {
    "title": "",
    "artist": "",
    "duration_in_seconds": 0,
    "grouping": "",
    "comment": "",
}

EMPTY_MUSIC_DATA_DICT = {
    "current_wall_unix_timestamp_ms": 0,
    "current_play_head_time_in_seconds": 0,
    "current_playlist_name": "",
    "current": Track(**EMPTY_TRACK_DATA_DICT),  # type: ignore[arg-type]
    "next": Track(**EMPTY_TRACK_DATA_DICT),  # type: ignore[arg-type]
    "next_next": Track(**EMPTY_TRACK_DATA_DICT),  # type: ignore[arg-type]
}

#endregion Constants
################################################################################

################################################################################
#region Globals

# fence for ignoring unused arguments in a function so as to not
# ignore all unused arguments/variables in function
# example:
# def foo(arg1, arg2, arg3):
#     if g__ignore_unused_arguments__ is False:
#         arg1 = arg1 # type: ignore[unreachable] # pylint: disable=self-assigning-variable,line-too-long  # noqa: E501,B950,W505
#         arg2 = arg2 # type: ignore[unreachable] # pylint: disable=self-assigning-variable,line-too-long  # noqa: E501,B950,W505
#     x = 5
#
# in the example, arg1 and arg2 get ignored about not being used,
# but arg3 and x do not
# unfortunately the long ass disable comment is required for every single
# argument to be ignored
g__ignore_unused_arguments__: bool = True

#endregion Globals
################################################################################


################################################################################
#region Public Functions

#-------------------------------------------------------------------------------
def loadMusicHudConfig(
    path: FileDescriptorOrPath | pathlib_Path,
) -> MusicHudConfig:
    config: MusicHudConfig

    str_path: str = str(path)

    try:
        with open(file=str_path, mode="rb", encoding="utf8") as f:
            f_data = f.read()
            config = json_loads(f_data, object_hook_pairs=MusicHudConfig)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(e)
        logger.info("Failed to load config, using default config.")
        config = copy_deepcopy(DEFAULT_CONFIG)

    return config

#-------------------------------------------------------------------------------
def durationInSecondsToPretty(duration_in_seconds: int) -> str:
    minutes = int(duration_in_seconds / 60)
    seconds = int(duration_in_seconds % 60)
    length_pretty = f"{minutes:d}:{seconds:02d}"
    return length_pretty

#-------------------------------------------------------------------------------
def getApp(name: str) -> Application:
    return SBApplication.applicationWithBundleIdentifier_(name)  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long  # noqa: E501,B950

#-------------------------------------------------------------------------------
def getAppleMusic() -> Application:
    app_apple_music = getApp("com.apple.Music")
    return app_apple_music

#-------------------------------------------------------------------------------
def appleMusicTrackToOurTrack(track: AppleMusicTrack) -> Track:

    if track and track.name():
        length = int(track.finish() - track.start())
        ret_track = Track(
            title=str(track.name()),
            artist=str(track.artist()),
            duration_in_seconds=length,
            grouping=str(track.grouping()),
            comment=str(track.comment()),
        )
    else:
        ret_track = Track(**EMPTY_TRACK_DATA_DICT)  # type: ignore[arg-type]

    return ret_track

#-------------------------------------------------------------------------------
def appleMusicGetPlaylist(app_apple_music: Application) -> AppleMusicPlaylist:

    app_apple_music_playlist = None
    try:
        app_apple_music_playlist = app_apple_music.currentPlaylist()
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(e)

    return app_apple_music_playlist

#-------------------------------------------------------------------------------
def appleMusicGetPlaylistName(playlist: AppleMusicPlaylist) -> str:
    ret_name = ""

    if (
        playlist is not None
    ):
        ret_name = str(playlist.name())

    return ret_name

#-------------------------------------------------------------------------------
def appleMusicGetCurrentPlayHeadTimeInSeconds(
    app_apple_music: Application,
    current_track: AppleMusicTrack,
) -> int:
    ret_time = 0

    try:
        raw_time = int(app_apple_music.playerPosition())

        # adjust raw_time by track start time b/c the track can start playing
        # from a time greater than 0, such as if skipping a long silence or intro
        current_start = int(current_track.start())

        cooked_time = raw_time - current_start
        ret_time = max(cooked_time, 0)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(e)

    return ret_time

#-------------------------------------------------------------------------------
def appleMusicGetCurrentAppleTrack(app_apple_music: Application) -> AppleMusicTrack:
    app_apple_music_track: AppleMusicTrack = None
    try:
        app_apple_music_track = app_apple_music.currentTrack()
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(e)

    return app_apple_music_track

#-------------------------------------------------------------------------------
@functools_lru_cache()
def appleMusicGetNextTrack(
    current_playlist: AppleMusicPlaylist,
    current_apple_track: AppleMusicTrack,
    offset: int = 1,
) -> AppleMusicTrack:

    app_apple_music_track: AppleMusicTrack = None
    try:
        if current_playlist:
            current_index = current_apple_track.index()
            playlist_tracks = current_playlist.tracks()
            next_index = current_index + 1

            loop_count = 0
            while True:
                loop_count = loop_count + 1
                if loop_count >= 100:
                    break

                # TODO: explain this better
                app_apple_music_track = playlist_tracks[next_index - 1]  # b/c playlist index is offset, first is index -1  # noqa: E501,B950

                if app_apple_music_track is not None:
                    next_index = next_index + 1

                    if app_apple_music_track.enabled():
                        offset = offset - 1

                if (
                    offset <= 0 or
                    app_apple_music_track is None
                ):
                    break
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(e)

    return app_apple_music_track

#-------------------------------------------------------------------------------
def getMusicData() -> MusicData:
    """
    TODO
    """

    pool = NSAutoreleasePool.alloc().init()  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long  # noqa: E501,B950

    music_data = MusicData(**EMPTY_MUSIC_DATA_DICT)  # type: ignore[arg-type]

    app_apple_music: Application = getAppleMusic()

    if (
        app_apple_music is not None and
        app_apple_music.isRunning() and
        app_apple_music.playerState() == APPLE_MUSIC_STATE_PLAYING
    ):
        current_playlist = appleMusicGetPlaylist(app_apple_music)
        music_data.current_playlist_name = appleMusicGetPlaylistName(current_playlist)

        current_apple_track = appleMusicGetCurrentAppleTrack(app_apple_music)
        music_data.current = appleMusicTrackToOurTrack(current_apple_track)
        music_data.current_play_head_time_in_seconds = \
            appleMusicGetCurrentPlayHeadTimeInSeconds(
                app_apple_music,
                current_apple_track,
            )
        music_data.current_wall_unix_timestamp_ms = int(time_time() * 1000)

        next_apple_track = appleMusicGetNextTrack(
            current_playlist=current_playlist,
            current_apple_track=current_apple_track,
        )
        music_data.next = appleMusicTrackToOurTrack(next_apple_track)

        next_next_apple_track = appleMusicGetNextTrack(
            current_playlist=current_playlist,
            current_apple_track=current_apple_track,
            offset=2,
        )
        music_data.next_next = appleMusicTrackToOurTrack(next_next_apple_track)

    else:
        logger.debug(msg="no music app playing")

    del pool

    return music_data

#-------------------------------------------------------------------------------
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

    ret: str = ""
    if comment:
        ret = "<li>" + comment.replace(",", "</li><li>") + "</li>"
    ret += "<li>Whatever Feels Right</li>"

    return ret

#endregion Public Functions
################################################################################

################################################################################
#region Public Classes

#===============================================================================
class MusicHudServer():
    """
    MusicHudServer handles managing communication between Music Player and
    HTTP requests.
    """

    config: MusicHudConfig
    keep_running = True
    server_thread: threading_Thread | None = None
    music_data_thread: threading_Thread | None = None
    test_case: Any = None
    music_data_buffers: list[MusicData] = [
        MusicData(**EMPTY_MUSIC_DATA_DICT),  # type: ignore[arg-type]
        MusicData(**EMPTY_MUSIC_DATA_DICT),  # type: ignore[arg-type]
    ]
    music_data_buffer_presentation_index: int = 0

    #---------------------------------------------------------------------------
    def __init__(
        self,
        *args: Any,
        config: MusicHudConfig | None = None,
        **kwargs: Any,
    ):
        """
        Args:
            config (MusicHudConfig | None, optional): Configuration settings object.
                Defaults to None.
        """
        super().__init__(*args, **kwargs)
        if config is None:
            config = copy_deepcopy(DEFAULT_CONFIG)
        self.config = config

    #---------------------------------------------------------------------------
    def runServer(
        self,
    ) -> None:
        """
        Run the server in a separate thread.
        """

        logger.debug("setting up server")

        self.server_thread = threading_Thread(
            target=self.serverThread,
            args=[
                MusicHudHTTPRequestHandler,
            ],
        )
        self.server_thread.start()

        self.music_data_thread = threading_Thread(
            target=self.musicDataThread,
            args=[],
        )
        self.music_data_thread.start()

        self.server_thread.join()
        self.music_data_thread.join()

        logger.debug("tearing down server")

    #---------------------------------------------------------------------------
    def musicDataThread(self) -> None:
        """
        Function that is the Apple Music communication thread's run loop.
        """  # noqa: D401

        pool = NSAutoreleasePool.alloc().init()  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long  # noqa: E501,B950

        logger.debug(msg="musicDataThread started")

        while self.keep_running:
            new_music_data = getMusicData()

            buffer_index = (self.music_data_buffer_presentation_index + 1) % 2
            self.music_data_buffers[buffer_index] = new_music_data
            self.music_data_buffer_presentation_index = buffer_index

            # logger.debug(time_time())

            # TODO: rate limit to 1 per 200ms; takes variable length of time,
            # so we cannot just sleep 0.5...
            # BUT it currently takes 250ms on M1 Max to run...
            time_sleep(0)

        logger.debug("musicDataThread stopped")

        del pool

    #---------------------------------------------------------------------------
    def serverThread(self, handler_cls: Any) -> None:
        """
        Function that is the server's thread's run loop.
        """  # noqa: D401

        pool = NSAutoreleasePool.alloc().init()  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long  # noqa: E501,B950

        logger.debug("starting HTTP server")

        server = MusicHudHTTPServer(
            server_address=("localhost", self.config.server_port),
            RequestHandlerClass=handler_cls,
            config=self.config,
            server=self,
        )

        logger.debug("HTTP server started")

        while self.keep_running:
            server.handle_request()
            # try to be nice to other threads
            time_sleep(0)
            # os_sched_yield()
        server.server_close()

        logger.debug("HTTP server stopped")

        del pool

    #---------------------------------------------------------------------------
    def stopServer(self) -> None:
        """
        Stop the server by flagging the run loop and waiting for thread to join.
        """

        self.keep_running = False

#===============================================================================
class MusicHudHTTPServer(http_server_HTTPServer):
    """
    HTTP Server that responds to http requests.
    """

    server: MusicHudServer
    config: MusicHudConfig

    #-------------------------------------------------------------------------
    def __init__(
        self,
        *args: Any,
        server: MusicHudServer,
        config: MusicHudConfig | None = None,
        **kwargs: Any,
    ):
        """
        HTTP Server that responds to http requests.

        Args:
            config (MusicHudConfig | None, optional): Configuration settings object.
            Defaults to None.
        """

        super().__init__(*args, **kwargs)
        self.server = server
        if config is None:
            config = copy_deepcopy(DEFAULT_CONFIG)
        self.config = config

#===============================================================================
class MusicHudHTTPRequestHandler(http_server_BaseHTTPRequestHandler):
    """
    TODO
    """

    server: MusicHudHTTPServer  # pyright: ignore[reportIncompatibleVariableOverride]

    #---------------------------------------------------------------------------
    def _do_get__stop_server(
        self,
    ) -> None:
        """
        TODO: write doc
        """
        self.server.server.stopServer()
        self.send_response(200)
        self.end_headers()

    #---------------------------------------------------------------------------
    def _do_get__root(
        self,
    ) -> None:
        """
        _summary_
        """

        with (
            open(
                file=pathlib_Path(MY_DIR_FULLPATH + "/hud.html"),
                mode="rt",
                encoding="utf8",
            )
        ) as f:
            message = f.read()

        message_bytes = message.encode("utf8", errors="ignore")
        self.send_response(200)
        self.end_headers()
        _ = self.wfile.write(message_bytes)

    #---------------------------------------------------------------------------
    def _do_get__config(
        self,
    ) -> None:

        data: dict[Any, Any] = {}

        config: MusicHudConfig = self.server.config

        data["config"] = asdict(config)

        message = json_dumps(data)

        message_bytes = message.encode("utf8", errors="ignore")
        self.send_response(200)
        self.end_headers()
        _ = self.wfile.write(message_bytes)

    #---------------------------------------------------------------------------
    def _do_get__data(
        self,
    ) -> None:
        data: dict[Any, Any] = {}

        music_hud_server: MusicHudServer = self.server.server
        music_data = music_hud_server.music_data_buffers[
            music_hud_server.music_data_buffer_presentation_index
        ]

        data["music_data"] = asdict(music_data)

        message = json_dumps(data)

        message_bytes = message.encode("utf8", errors="ignore")
        self.send_response(200)
        self.end_headers()
        _ = self.wfile.write(message_bytes)

    #---------------------------------------------------------------------------
    def do_GET(self) -> None:  # pylint: disable=invalid-name  # noqa: C901
        """
        TODO: write doc
        """
        # pylint: disable=possibly-unused-variable

        pool = NSAutoreleasePool.alloc().init()  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long  # noqa: E501,B950

        parsed_path = urllib_parse_urlparse(self.path)
        real_path = parsed_path.path
        # headers = self.headers

        match real_path:
            #...................................................................
            case "/STOP_SERVER":
                self._do_get__stop_server()

            #...................................................................
            case "/":
                self._do_get__root()

            #...................................................................
            case "/config":
                self._do_get__config()

            #...................................................................
            case "/data":
                self._do_get__data()

            #...................................................................
            case _:
                self.send_response(404)
                self.end_headers()

        del pool

    #---------------------------------------------------------------------------
    def log_request(
        self,
        code: Any = "-",
        size: Any = "-",
    ) -> None:
        """Log an accepted request.

        This is called by send_response().
        """
        if isinstance(code, http_HTTPStatus):
            code = code.value
        self.log_message(
            '"%s" %s %s',
            self.requestline,
            str(code),
            str(size),
        )

    #---------------------------------------------------------------------------
    def log_error(
        self,
        format: str,  # pylint: disable=redefined-builtin
        *args: Any,
    ) -> None:
        """Log an error.

        This is called when a request cannot be fulfilled.  By
        default it passes the message on to log_message().

        Arguments are the same as for log_message().
        """
        formatted_args = format % args
        formatted_args = formatted_args.translate(self._control_char_table)  # type: ignore[attr-defined]  # noqa: E501,B950,W505

        message = (
            f"{self.address_string()} - - " +
            f"[{self.log_date_time_string()}] {formatted_args}"
        )

        logger.error(message)

    #---------------------------------------------------------------------------
    def log_message(
        self,
        format: str,  # pylint: disable=redefined-builtin
        *args: Any,
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
        formatted_args = format % args
        formatted_args = formatted_args.translate(self._control_char_table)  # type: ignore[attr-defined]  # noqa: E501,B950,W505

        message = (
            f"{self.address_string()} - - " +
            f"[{self.log_date_time_string()}] {formatted_args}"
        )

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
    if g__ignore_unused_arguments__ is False:
        argv = argv  # type: ignore[unreachable] # pylint: disable=self-assigning-variable,line-too-long  # noqa: E501,B950,W505

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
