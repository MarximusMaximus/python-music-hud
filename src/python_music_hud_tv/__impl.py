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

# TODO: render full config into page from server side rendering at page load
# TODO: move display logic from server side data to client side processing
# TODO: time offset fixing
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
    event_title_html: str
    background_color: str
    foreground_color: str
    secret_titles: list[str]
    display_songs_for_playlists: list[str]
    gap_silence_title: str
    last_call_title: str
    last_dance_title: str

@dataclass
class Track:
    title: str = ""
    artist: str = ""
    duration_in_seconds: int = 0
    duration_pretty: str = ""
    grouping: str = ""
    comment: str = ""

@dataclass
class MusicData:
    current_play_head_time_in_seconds: int
    current_play_head_time_pretty: str
    current_play_head_time_and_length_pretty: str
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
    event_title_html="Mark<br/>&<br/>Sherry<br/>Wedding",
    background_color="#6E6856",
    foreground_color="#1d1b16",
    secret_titles=[
        "Sherry",
        "Never Gonna Give You Up (7\" Mix)",
    ],
    display_songs_for_playlists=[
        "SPOTIFY",
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
    last_call_title="Last Call (One Bourbon, One Scotch, One Beer)",
    last_dance_title="(I've Had) The Time of My Life",
)

EMPTY_PAGE_DATA_DICT = {
    "current_dance_style_header": "",
    "next_divider": "",
    "next_header": "",
    "next_dance_style_header": "",
    "next_next_header": "",
    "real_time": "",
}

EMPTY_TRACK_DATA_DICT = {
    "title": "",
    "artist": "",
    "duration_in_seconds": 0,
    "duration_pretty": "",
    "grouping": "",
    "comment": "",
}

EMPTY_MUSIC_DATA_DICT = {
    "current_play_head_time_in_seconds": 0,
    "current_play_head_time_pretty": "",
    "current_play_head_time_and_length_pretty": "",
    "current_playlist_name": "",
    "current": Track(**EMPTY_TRACK_DATA_DICT),  # type: ignore[arg-type]
    "next": Track(**EMPTY_TRACK_DATA_DICT),  # type: ignore[arg-type]
    "next_next": Track(**EMPTY_TRACK_DATA_DICT),  # type: ignore[arg-type]
}
# EMPTY_MUSIC_DATA = MusicData(
#     current_play_head_time_in_seconds=0,
#     current_play_head_time_pretty="",
#     current_play_head_time_and_length_pretty="",
#     current_playlist_name="",
#     current=Track(
#         "",
#         "",
#         0,
#         "",
#         "",
#         "",
#     ),
#     next=Track(
#         "",
#         "",
#         0,
#         "",
#         "",
#         "",
#     ),
#     next_next=Track(
#         "",
#         "",
#         0,
#         "",
#         "",
#         "",
#     ),
# )

#endregion Constants
################################################################################

################################################################################
#region Globals

g_app_apple_music: Any = SBApplication.applicationWithBundleIdentifier_("com.apple.Music")  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long  # noqa: E501,B950

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
def appleMusicTrackToOurTrack(track: AppleMusicTrack) -> Track:
    # ret_track: Track = {
    #     "title": "",
    #     "artist": "",
    #     "duration_in_seconds": 0,
    #     "duration_pretty": "",
    #     "grouping": "",
    #     "comment": "",
    # }

    if track and track.name():
        length = int(track.finish() - track.start())
        # ret_track = {
        #     "title": str(track.name()),
        #     "artist": str(track.artist()),
        #     "duration_in_seconds": length,
        #     "duration_pretty": durationInSecondsToPretty(length),
        #     "grouping": str(track.grouping()),
        #     "comment": str(track.comment()),
        # }
        ret_track = Track(
            title=str(track.name()),
            artist=str(track.artist()),
            duration_in_seconds=length,
            duration_pretty=durationInSecondsToPretty(length),
            grouping=str(track.grouping()),
            comment=str(track.comment()),
        )
    else:
        ret_track = Track(**EMPTY_TRACK_DATA_DICT)  # type: ignore[arg-type]

    return ret_track

#-------------------------------------------------------------------------------
def appleMusicGetPlaylistName() -> str:
    ret_name = ""

    app_apple_music = getApp("com.apple.Music")

    if (
        app_apple_music is not None and
        app_apple_music.isRunning() and
        app_apple_music.playerState() == APPLE_MUSIC_STATE_PLAYING
    ):
        app_apple_music_playlist = app_apple_music.currentPlaylist()
        if app_apple_music_playlist:
            ret_name = str(app_apple_music_playlist.name())

    return ret_name

#-------------------------------------------------------------------------------
def appleMusicGetCurrentPlayHeadTimeInSeconds() -> int:
    ret_time = 0

    app_apple_music = getApp("com.apple.Music")

    if (
        app_apple_music is not None and
        app_apple_music.isRunning() and
        app_apple_music.playerState() == APPLE_MUSIC_STATE_PLAYING
    ):
        raw_time = int(app_apple_music.playerPosition())

        # adjust raw_time by track start time b/c the track can start playing
        # from a time greater than 0, such as if skipping a long silence or intro
        current_track = g_app_apple_music.currentTrack()
        current_start = int(current_track.start())

        cooked_time = raw_time - current_start
        ret_time = max(cooked_time, 0)

    return ret_time

#-------------------------------------------------------------------------------
def appleMusicGetCurrentTrack() -> Track:
    app_apple_music = getApp("com.apple.Music")

    app_apple_music_track: AppleMusicTrack = None
    if (
        app_apple_music is not None and
        app_apple_music.isRunning() and
        app_apple_music.playerState() == APPLE_MUSIC_STATE_PLAYING
    ):
        app_apple_music_track = app_apple_music.currentTrack()

    ret_track = appleMusicTrackToOurTrack(app_apple_music_track)

    return ret_track

#-------------------------------------------------------------------------------
def appleMusicGetNextTrack(offset: int = 1) -> Track:
    app_apple_music = getApp("com.apple.Music")

    app_apple_music_track: AppleMusicTrack = None
    if (
        app_apple_music is not None and
        app_apple_music.isRunning() and
        app_apple_music.playerState() == APPLE_MUSIC_STATE_PLAYING
    ):
        app_apple_music_playlist = app_apple_music.currentPlaylist()
        if app_apple_music_playlist:
            current_track = g_app_apple_music.currentTrack()
            current_index = current_track.index()
            playlist_tracks = app_apple_music_playlist.tracks()
            next_index = current_index + 1

            loop_count = 0
            while True:
                loop_count = loop_count + 1
                if loop_count >= 100:
                    break

                app_apple_music_track = playlist_tracks[next_index - 1]  # b/c playlist index is offset, first is index -1  # noqa: E501,B950

                if app_apple_music_track is not None:
                    next_index = next_index + 1

                    if app_apple_music_track.enabled():
                        offset = offset - 1

                loop_count = loop_count + 1
                if (
                    offset <= 0 or
                    app_apple_music_track is None
                ):
                    break

    ret_track = appleMusicTrackToOurTrack(app_apple_music_track)

    return ret_track

#-------------------------------------------------------------------------------
def getMusicData() -> MusicData:
    """
    TODO
    """

    pool = NSAutoreleasePool.alloc().init()  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long  # noqa: E501,B950

    # music_data: MusicData = copy_deepcopy(EMPTY_MUSIC_DATA)
    music_data = MusicData(**EMPTY_MUSIC_DATA_DICT)  # type: ignore[arg-type]

    if (
        g_app_apple_music is not None and
        g_app_apple_music.isRunning() and
        g_app_apple_music.playerState() == APPLE_MUSIC_STATE_PLAYING
    ):
        # logger.debug("getting info from Apple Music App")
        music_data.current = appleMusicGetCurrentTrack()
        music_data.next = appleMusicGetNextTrack()
        music_data.next_next = appleMusicGetNextTrack(offset=2)
        music_data.current_play_head_time_in_seconds = \
            appleMusicGetCurrentPlayHeadTimeInSeconds()
        music_data.current_playlist_name = appleMusicGetPlaylistName()

        music_data.current_play_head_time_pretty = \
            durationInSecondsToPretty(music_data.current_play_head_time_in_seconds)

        music_data.current_play_head_time_and_length_pretty = (
            f'{music_data.current_play_head_time_pretty}/' +
            f'{music_data.current.duration_pretty}'
        )
    else:
        logger.debug("no music app playing")

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

    ret = "<li>" + comment.replace(",", "</li><li>") + "</li>" if comment else ""
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
    # music_data: MusicData = copy_deepcopy(EMPTY_MUSIC_DATA)
    music_data: MusicData = MusicData(**EMPTY_MUSIC_DATA_DICT)  # type: ignore[arg-type]

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
        _summary_
        """

        pool = NSAutoreleasePool.alloc().init()  # type: ignore[reportGeneralTypesIssues]  # pylint: disable=line-too-long  # noqa: E501,B950

        logger.debug(msg="musicDataThread started")

        while self.keep_running:
            new_music_data = getMusicData()
            self.music_data = new_music_data
            # TODO: rate limit to 1 per 500ms; takes variable length of time,
            # so we cannot just sleep 0.5
            time_sleep(0)
            # os_sched_yield()

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
        config: MusicHudConfig,
    ) -> None:
        """
        TODO: write doc
        """

        if g__ignore_unused_arguments__ is False:
            config = config  # type: ignore[unreachable] # pylint: disable=self-assigning-variable,line-too-long  # noqa: E501,B950,W505

        self.server.server.stopServer()
        self.send_response(200)
        self.end_headers()

    #---------------------------------------------------------------------------
    def _do_get__root(self, config: MusicHudConfig) -> None:
        """
        _summary_
        """

        # page_data : PageData = {  # pyright: ignore[reportUnusedVariable]
        #     "current_dance_style_header": "",
        #     "next_divider": "",
        #     "next_header": "",
        #     "next_dance_style_header": "",
        #     "next_next_header": "",
        #     "real_time": "",
        # }
        page_data = PageData(**EMPTY_PAGE_DATA_DICT)

        current_playlist_name: str = ""

        # GIL allows us to copy the whole data structure instead of locking it
        # for the whole function; better? worse?
        music_data = copy_deepcopy(self.server.server.music_data)

        if music_data.next_next.title in config.secret_titles:
            music_data.next_next.title = "*****"
        elif (
            config.gap_silence_title in (
                music_data.next_next.title,
                music_data.next.title,
                music_data.current.title,
            )
        ):
            music_data.next_next.title = ""
            music_data.next_next.duration_pretty = ""
            music_data.next_next.comment = ""

        if music_data.next.title in config.secret_titles:
            music_data.next.title = "*****"
            music_data.next.artist = "*****"
        elif (
            config.gap_silence_title in (
                music_data.next.title,
                music_data.current.title,
            )
        ):
            music_data.next.title = ""
            music_data.next.artist = ""
            music_data.next.duration_pretty = ""
            music_data.next.comment = ""

        if (
            music_data.current.title ==
            config.gap_silence_title
        ):
            music_data.current.title = ""
            music_data.current.artist = ""
            music_data.current.comment = ""

        if (
            music_data.current.title in (
                config.last_call_title,
                config.last_dance_title,
            )
        ):
            music_data.next.title = ""
            music_data.next.artist = ""
            music_data.next.duration_pretty = ""
            music_data.next.comment = ""

            music_data.next_next.title = ""
            music_data.next_next.duration_pretty = ""
            music_data.next_next.comment = ""

            page_data.next_dance_style_header = ""
            page_data.next_header = ""
            page_data.next_next_header = ""
            page_data.next_divider = "<hr>"

        music_data.current.comment = \
            commentToStyle(music_data.current.comment)

        if music_data.current.title:
            page_data.current_dance_style_header = "Dance Style Info:"
        else:
            music_data.current_play_head_time_and_length_pretty = ""

        if music_data.next.title:
            music_data.next.comment = \
                commentToStyle(music_data.next.comment)

            page_data.next_divider = "<hr>"
            page_data.next_header = "Next Up:"
            page_data.next_dance_style_header = "Dance Style Info:"

            if (
                music_data.next.title ==
                config.last_dance_title
            ):
                page_data.next_header = "LAST DANCE:"

            if music_data.next.artist:
                music_data.next.artist = (
                    f'by {music_data.next.artist}'
                )

        if music_data.next_next.title:
            music_data.next_next.comment = \
                commentToStyle(music_data.next_next.comment)

            page_data.next_next_header = "Followed by:<br/>"

        if music_data.current.title == config.last_call_title:
            music_data.next.title = \
                "<div class=\"bigTitle\">LAST CALL FOR ALCOHOL!</div>"
        elif (
            music_data.current.title ==
            config.last_dance_title
        ):
            music_data.next.title = \
                "<div class=\"bigTitle\">THANK YOU FOR COMING!</div>"

        current_playlist_name = music_data.current_playlist_name
        if (
            not music_data.current.title or
            current_playlist_name not in config.display_songs_for_playlists
        ):
            music_data.next_next.title = \
                music_data.next.title
            if not music_data.next_next.title:
                music_data.next_next.title = ""
            else:
                music_data.next_next.title = \
                    "Next: " + music_data.next_next.title
            music_data.next.title = \
                music_data.current.title
            if music_data.next.title:
                music_data.next.title = (
                    "<br/><br/><br/><br/><br/><br/><br/>Currently Playing:" +
                    f'{music_data.next.title}<br/>' +
                    f'{music_data.next_next.title}'
                )
            else:
                music_data.next.title = ""
            music_data.next_next.title = ""

            music_data.current.title = (
                f'<div class="bigTitle"><br/>{config.event_title_html}</div>'
            )

            music_data.current.artist = ""
            music_data.current.comment = ""

            music_data.current_play_head_time_and_length_pretty = ""

            music_data.next.artist = ""
            music_data.next.duration_pretty = ""
            music_data.next.comment = ""

            music_data.next_next.title = ""
            music_data.next_next.duration_pretty = ""
            music_data.next_next.comment = ""

            page_data.current_dance_style_header = ""
            page_data.next_dance_style_header = ""
            page_data.next_divider = ""
            page_data.next_header = ""
            page_data.next_next_header = ""
        else:
            music_data.current.title = (
                '<div class="title">' +
                f'{music_data.current.title}' +
                "</div>"
            )

        if music_data.current.artist:
            music_data.current.artist = \
                f'by {music_data.current.artist}'

        with (
            open(
                file=pathlib_Path(MY_DIR_FULLPATH + "/hud.html.j2"),
                mode="rt",
                encoding="utf8",
            )
        ) as f:
            raw_message = f.read()

        message = raw_message.format_map({**globals(), **locals()})

        message_bytes = message.encode("utf8", errors="ignore")
        self.send_response(200)
        self.end_headers()
        _ = self.wfile.write(message_bytes)

    #---------------------------------------------------------------------------
    def _do_get__data(self, config: MusicHudConfig) -> None:

        # page_data : PageData = {  # pyright: ignore[reportUnusedVariable]
        #     "current_dance_style_header": "",
        #     "next_divider": "",
        #     "next_header": "",
        #     "next_dance_style_header": "",
        #     "next_next_header": "",
        #     "real_time": "",
        # }
        page_data = PageData(**EMPTY_PAGE_DATA_DICT)

        current_playlist_name: str = ""

        data: dict[Any, Any] = {}

        # GIL allows us to copy the whole data structure instead of locking it
        # for the whole function; better? worse?
        music_data = copy_deepcopy(self.server.server.music_data)

        if music_data.next_next.title in config.secret_titles:
            music_data.next_next.title = "*****"
        elif (
            config.gap_silence_title in (
                music_data.next_next.title,
                music_data.next.title,
                music_data.current.title,
            )
        ):
            music_data.next_next.title = ""
            music_data.next_next.duration_pretty = ""
            music_data.next_next.comment = ""

        if music_data.next.title in config.secret_titles:
            music_data.next.title = "*****"
            music_data.next.artist = "*****"
        elif (
            config.gap_silence_title in (
                music_data.next.title,
                music_data.current.title,
            )
        ):
            music_data.next.title = ""
            music_data.next.artist = ""
            music_data.next.duration_pretty = ""
            music_data.next.comment = ""

        if (
            music_data.current.title ==
            config.gap_silence_title
        ):
            music_data.current.title = ""
            music_data.current.artist = ""
            music_data.current.comment = ""

        if (
            music_data.current.title in (
                config.last_call_title,
                config.last_dance_title,
            )
        ):
            music_data.next.title = ""
            music_data.next.artist = ""
            music_data.next.duration_pretty = ""
            music_data.next.comment = ""

            music_data.next_next.title = ""
            music_data.next_next.duration_pretty = ""
            music_data.next_next.comment = ""

            page_data.next_dance_style_header = ""
            page_data.next_header = ""
            page_data.next_next_header = ""
            page_data.next_divider = "<hr>"

        music_data.current.comment = commentToStyle(
            music_data.current.comment,
        )

        if music_data.current.title:
            page_data.current_dance_style_header = "Dance Style Info:"
        else:
            music_data.current_play_head_time_and_length_pretty = ""

        if music_data.next.title:
            music_data.next.comment = (
                commentToStyle(
                    music_data.next.comment,
                )
            )

            page_data.next_divider = "<hr>"
            page_data.next_header = "Next Up:"
            page_data.next_dance_style_header = "Dance Style Info:"

            if (
                music_data.next.title == \
                    config.last_dance_title
            ):
                page_data.next_header = "LAST DANCE:"

            if music_data.next.artist:
                music_data.next.artist = (
                    f'by {music_data.next.artist}'
                )

        if music_data.next_next.title:
            music_data.next_next.comment = (
                commentToStyle(
                    music_data.next_next.comment,
                )
            )

            page_data.next_next_header = "Followed by:<br/>"

        if (
            music_data.current.title == \
                config.last_call_title
        ):
            music_data.next.title = (
                "<div class=\"bigTitle\">LAST CALL FOR ALCOHOL!</div>"
            )
        elif (
            music_data.current.title ==
            config.last_dance_title
        ):
            music_data.next.title = (
                "<div class=\"bigTitle\">THANK YOU FOR COMING!</div>"
            )

        current_playlist_name = music_data.current_playlist_name
        if (
            not music_data.current.title or
            current_playlist_name not in config.display_songs_for_playlists
        ):
            music_data.next_next.title = \
                music_data.next.title

            if not music_data.next_next.title:
                music_data.next_next.title = ""
            else:
                music_data.next_next.title = \
                    "Next: " + music_data.next_next.title

            music_data.next.title = \
                music_data.current.title

            if music_data.next.title:
                music_data.next.title = (
                    "<br/><br/><br/><br/><br/><br/><br/>Currently Playing:" +
                    f'{music_data.next.title}<br/>' +
                    f'{music_data.next_next.title}'
                )
            else:
                music_data.next.title = ""

            music_data.next_next.title = ""

            music_data.current.title = (
                f'<div class="bigTitle"><br/>{config.event_title_html}</div>'
            )

            music_data.current.artist = ""
            music_data.current.comment = ""

            music_data.current_play_head_time_and_length_pretty = ""

            music_data.next.artist = ""
            music_data.next.duration_pretty = ""
            music_data.next.comment = ""

            music_data.next_next.title = ""
            music_data.next_next.duration_pretty = ""
            music_data.next_next.comment = ""

            page_data.current_dance_style_header = ""
            page_data.next_dance_style_header = ""
            page_data.next_divider = ""
            page_data.next_header = ""
            page_data.next_next_header = ""
        else:
            music_data.current.title = (
                f'{music_data.current.title}'
            )

        if music_data.current.artist:
            music_data.current.artist = (
                f'by {music_data.current.artist}'
            )

        data["music_data"] = asdict(music_data)
        data["page_data"] = asdict(page_data)

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

        config: MusicHudConfig = self.server.config

        parsed_path = urllib_parse_urlparse(self.path)
        real_path = parsed_path.path
        # headers = self.headers

        match real_path:
            #...................................................................
            case "/STOP_SERVER":
                self._do_get__stop_server(config)

            #...................................................................
            case "/":
                self._do_get__root(config)

            case "/data":
                self._do_get__data(config)

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
