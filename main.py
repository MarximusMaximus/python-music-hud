# /bin/env python

from BaseHTTPServer import (
    HTTPServer                      as BaseHTTPServer_HTTPServer,
    BaseHTTPRequestHandler          as BaseHTTPServer_BaseHTTPRequestHandler,
)

from Foundation import *
from ScriptingBridge import *

from threading import (
    Thread                          as threading_Thread,
)
from urlparse import (
    urlparse                        as urlparse_urlparse,
)

from datetime import (
    datetime                            as datetime_datetime,
)

iTunes = SBApplication.applicationWithBundleIdentifier_("com.apple.iTunes")


SERVER_PORT = 8080

def commentToStyle(comment):

    if comment is None:
        return ""

    comment = comment.split(";")[0]

    comment = comment\
        .replace("ECS", "East Coast Swing, Jitterbug")\
        .replace("WCS", "West Coast Swing")

    ret = "<li>" + comment.replace(",", "</li><li>") + "</li>" if comment else ""
    ret += "<li>Whatever Feels Right</li>"

    return ret

SECRET_TITLES = [

]

DISPLAY_SONGS_FOR_PLAYLISTS = [
    "9 Pre Dance - 30m (6:30p)",
    "10 Main Dance - 1h (8p)",
    "11 Extra Dance - 1h (?)",
    "12 Last Call - 30m (9p)",
    "13 GTFO - 30m (9:30p)",
    "14 Cleanup - 2h (10:15p)",
]

GAP_SILENCE_TITLE = "----- 30 Minutes of Silence -----"

LAST_CALL_TITLE = "Last Call (One Bourbon, One Scotch, One Beer)"

LAST_DANCE_TITLE = "Exterminate Annihilate Destroy"

#===================================================================================================================
class Server(object):
    keepRunning = True
    thread = None
    testCase = None

    #---------------------------------------------------------------------------------------------------------------
    def __init__(self):
        pass

    #---------------------------------------------------------------------------------------------------------------
    def runServer(self, handlerCls):
        self.thread = threading_Thread(
            target=self.serverThread,
            args=
            [
                handlerCls
            ]
        )
        self.thread.start()

    #---------------------------------------------------------------------------------------------------------------
    def serverThread(self, handlerCls):
        print "starting server"

        server = BaseHTTPServer_HTTPServer(('localhost', SERVER_PORT), handlerCls)

        while self.keepRunning:
            server.handle_request()
        server.server_close()

        print "server closed"

    #---------------------------------------------------------------------------------------------------------------
    def stopServer(self):
        self.keepRunning = False
        self.thread.join()

    pass

#===================================================================================================================
# noinspection PyClassHasNoInit
class GenericHandler(BaseHTTPServer_BaseHTTPRequestHandler):

    #---------------------------------------------------------------------------------------------------------------
    def do_GET(self):
        parsed_path = urlparse_urlparse(self.path)
        real_path = parsed_path.path
        headers = self.headers

        if real_path == "/STOP_SERVER":
            return
        else:
            currentTrack = iTunes.currentTrack()
            currentTitle = currentTrack.name()
            if currentTitle is not None:
                currentTitle = currentTitle.encode("utf8", "ignore")
            currentArtist = currentTrack.artist()
            if currentArtist is not None:
                currentArtist = "by " + currentArtist.encode("utf8", "ignore")
            currentComment = currentTrack.comment()
            currentStyle = commentToStyle(currentComment)
            currentIndex = currentTrack.index()
            
            currentStart = currentTrack.start()
            currentEnd = currentTrack.finish()
            currentLengthSeconds = int(currentEnd - currentStart)

            currentLengthMinutes = int(currentLengthSeconds / 60)
            currentLengthSeconds = int(currentLengthSeconds % 60)
            currentLengthPretty = "{:d}:{:02d}".format(currentLengthMinutes, currentLengthSeconds)

            currentPlayerPosition = iTunes.playerPosition()
            currentAdjustedPlayerPosition = max(currentPlayerPosition - currentStart, 0)
            currentPositionMinutes = int(currentAdjustedPlayerPosition / 60)
            currentPositionSeconds = int(currentAdjustedPlayerPosition % 60)
            currentPositionPretty = "{:d}:{:02d}".format(currentPositionMinutes, currentPositionSeconds)

            currentPositionAndLengthPretty = "{}/{}".format(currentPositionPretty, currentLengthPretty)

            currentPlaylist = iTunes.currentPlaylist()
            playlistTracks = currentPlaylist.tracks()

            currentDanceStyleHeader = "Dance Style Info:"

            nextTitle = "-"
            nextArtist = ""
            nextStyle = ""
            nextLengthPretty = ""
            nextDanceStyleHeader = ""
            nextDivider = "<hr>"
            nextHeader = "Next Up:"

            nextIndex = currentIndex + 1
            if nextIndex <= playlistTracks.count():
                nextTrack = playlistTracks[nextIndex - 1]  # b/c it's stupid.
                nextTitle = nextTrack.name()
                if nextTitle is not None:
                    nextTitle = nextTitle.encode("utf8", "ignore")
                nextArtist = nextTrack.artist()
                if nextArtist is not None:
                    nextArtist = "by " + nextArtist.encode("utf8", "ignore")
                nextComment = nextTrack.comment()
                nextStyle = commentToStyle(nextComment)

                if nextTitle in SECRET_TITLES:
                    nextTitle = "*****"
                    nextArtist = "*****"
                
                nextStart = nextTrack.start()
                nextEnd = nextTrack.finish()
                nextLengthSeconds = int(nextEnd - nextStart)
    
                nextLengthMinutes = int(nextLengthSeconds / 60)
                nextLengthSeconds = int(nextLengthSeconds % 60)
                nextLengthPretty = " - {:d}:{:02d}".format(nextLengthMinutes, nextLengthSeconds)

                nextDanceStyleHeader = "Dance Style Info:"

            nextNextTitle = ""
            nextNextComment = ""
            nextNextLengthPretty = ""
            nextNextDivider = ""
            nextNextHeader = ""

            nextNextIndex = currentIndex + 2
            if nextNextIndex <= playlistTracks.count():
                nextNextTrack = playlistTracks[nextNextIndex - 1]  # b/c it's stupid.
                nextNextTitle = nextNextTrack.name()
                if nextNextTitle is not None:
                    nextNextTitle = nextNextTitle.encode("utf8", "ignore")
                
                nextNextComment = nextNextTrack.comment()
                if nextNextComment is not None:
                    nextNextComment = nextNextComment.split(";")[0]
                    if nextNextComment:
                        nextNextComment += ", "
                    nextNextComment += "Whatever Feels Right"
                    nextNextComment = "<br/>" + nextNextComment\
                        .replace("ECS", "East Coast Swing, Jitterbug")\
                        .replace("WCS", "West Coast Swing")

                
                nextNextStart = nextNextTrack.start()
                nextNextEnd = nextNextTrack.finish()
                nextNextLengthSeconds = int(nextNextEnd - nextNextStart)
    
                nextNextLengthMinutes = int(nextNextLengthSeconds / 60)
                nextNextLengthSeconds = int(nextNextLengthSeconds % 60)
                nextNextLengthPretty = " - {:d}:{:02d}".format(nextNextLengthMinutes, nextNextLengthSeconds)

                nextNextDivider = "<hr>"
                nextNextHeader = "Followed by:<br/>"

                if nextNextTitle in SECRET_TITLES:
                    nextNextTitle = "*****"

            currentPlaylistName = currentPlaylist.name()

            if (
                nextNextTitle == GAP_SILENCE_TITLE or
                nextTitle == GAP_SILENCE_TITLE or
                currentTitle == GAP_SILENCE_TITLE
            ):
                nextNextTitle = ""
                nextNextComment = ""
                nextNextLengthPretty = ""
                nextNextDivider = ""
                nextNextHeader = ""

            if (
                nextTitle == GAP_SILENCE_TITLE or
                currentTitle == GAP_SILENCE_TITLE
            ):
                nextTitle = ""
                nextArtist = ""
                nextStyle = ""
                nextLengthPretty = ""
                nextDanceStyleHeader = ""
                nextDivider = ""
                nextHeader = ""
            elif nextTitle == LAST_DANCE_TITLE:
                nextHeader = "LAST DANCE:"

            if currentTitle == GAP_SILENCE_TITLE:
                currentTitle = ""
            elif currentTitle == LAST_CALL_TITLE:
                nextTitle = "<div class=\"bigTitle\">LAST CALL FOR ALCOHOL!</div>"
                nextArtist = ""
                nextStyle = ""
                nextLengthPretty = ""
                nextDanceStyleHeader = ""
                nextDivider = "<hr>"
                nextHeader = ""
                nextNextTitle = ""
                nextNextArtist = ""
                nextNextStyle = ""
                nextNextLengthPretty = ""
                nextNextDanceStyleHeader = ""
                nextNextHeader = ""
                nextNextComment = ""
            elif currentTitle == LAST_DANCE_TITLE:
                nextTitle = "<div class=\"bigTitle\">THANK YOU FOR COMING!</div>"
                nextArtist = ""
                nextStyle = ""
                nextLengthPretty = ""
                nextDanceStyleHeader = ""
                nextDivider = "<hr>"
                nextHeader = ""

            if (
                not currentTitle or
                currentPlaylistName not in DISPLAY_SONGS_FOR_PLAYLISTS
            ):
                nextNextTitle = nextTitle
                if not nextNextTitle or nextNextTitle == "-":
                    nextNextTitle = ""
                else:
                    nextNextTitle = "Next: " + nextNextTitle
                nextTitle = currentTitle
                if nextTitle:
                    nextTitle = "<br/><br/><br/><br/><br/><br/><br/>" + nextTitle + "<br/>" + nextNextTitle
                else:
                    nextTitle = ""
                nextNextTitle = ""

                currentTitle = "<div class=\"bigTitle\"><br/>Laura<br/>&<br/>Jeff<br/>Wedding</div>"
                currentArtist = ""
                currentPositionAndLengthPretty = ""
                currentDanceStyleHeader = ""
                currentStyle = ""

                nextArtist = ""
                nextStyle = ""
                nextLengthPretty = ""
                nextDanceStyleHeader = ""
                nextDivider = ""
                nextHeader = ""

                nextNextComment = ""
                nextNextLengthPretty = ""
                nextNextDivider = ""
                nextNextHeader = ""
            else:
                currentTitle = "<div class=\"title\">" + currentTitle + "</div>"


            realTime = datetime_datetime.now().strftime("%-I:%M:%S %p")

            message = (
                """
                <!DOCTYPE html>
                <html>
                <head>
                <html lang="en"> 
                <meta http-equiv="refresh" content="1" />
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
                <style>
                    body {
                        font-family: Big Caslon, -system, -system-font, Arial;
                        background-color: #000000;
                        color: rgba(212,175,55, 1);
                    }
                
                    body table {
                        margin: 0;
                        margin-left: 1%;
                        margin-right: 1%;
                    }
                
                    ul {
                        -webkit-column-count: 2;
                        margin: 0;
                        margin-left: 0.5em;
                    }
                    
                    li {
                        margin-left: 0.5em;
                    }
                
                    hr {
                        border: 1px;
                        border-style: solid;
                        margin-top: 20px;
                        margin-bottom: 20px;
                    }
                
                    .bottom {
                        position: absolute;
                        top: 600px;
                        width: 1900px;
                    }
                    .bottom-right {
                        position: absolute;
                        top: 646px;
                        left: 1000px;
                        width: 800px;
                    }
                
                    .currentTitle {
                        font-size: 4vw;
                    }
                    .currentTitle div.title {
                        width: 68%;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }
                    .currentTitle div.time {
                        position: absolute;
                        top: 1%;
                        right: 1%;
                    }
                    .currentArtist {
                        font-size: 2vw;
                        color: rgba(212,175,55, 0.8);
                    }
                    .currentStyleHeader {
                        font-size: 2vw;
                        color: rgba(212,175,55, 0.8);
                    }
                    .currentStyle {
                        font-size: 4.2vw;
                    }
                    
                    table.nextTable {
                        color: rgba(212,175,55, 0.7);
                    }
                    
                    table.nextNextTable {
                        font-size: 1.5vw;
                        color: rgba(212,175,55, 0.7);
                    }
                    
                    .headerNext {
                        font-size: 2.5vw;
                    }
                    .nextTitle {
                        font-size: 2vw;
                    }
                    .nextArtist {
                        font-size: 1.5vw;
                    }
                    .nextStyleHeader {
                        font-size: 1.5vw;
                    }
                    .nextStyle {
                        font-size: 2vw;
                    }
                    
                    div.realTime {
                        position: absolute;
                        bottom: 1%;
                        right: 1%;
                        font-size: 4vw;
                        color: rgba(212,175,55, 0.4);
                    }
                    
                    div.bigTitle {
                        font-size: 7.5vw; 
                        text-align: center;
                        width: 100%;
                    }
                </style>
                </head>
                """ +
                """
                <body><div max-width="100%">
                    <table width="98%">
                        <tr><td class="currentTitle">
                            <div class="time">{currentPositionAndLengthPretty}</div>
                            {currentTitle}
                        </td></tr>
                    </table>
                    <table width="98%">
                        <tr><td class="currentArtist">
                            {currentArtist}
                        </td></tr>
                        <tr><td class="currentStyleHeader">
                            {currentDanceStyleHeader}
                        </td></tr>
                        <tr><td class="currentStyle">
                            <ul>
                                {currentStyle}
                            </ul>
                        </td></tr>
                    </table>
                    <div class="bottom">
                        {nextDivider}
                        <table class="nextTable">
                            <tr>
                                <td class="headerNext">
                                    {nextHeader}
                                </td>
                            </tr>
                            <tr><td class="nextTitle">
                                {nextTitle} {nextLengthPretty}
                            </td></tr>
                            <tr><td class="nextArtist">
                                {nextArtist}
                            </td></tr>
                            <tr><td class="nextStyleHeader">
                                {nextDanceStyleHeader}
                            </td></tr>
                            <tr><td class="nextStyle">
                                <ul>
                                    {nextStyle}
                                </ul>
                            </td></tr>
                        </table>
                    </div>
                    <div class="bottom-right">
                        <table class="nextNextTable">
                            <tr>
                                <td>
                                    {nextNextHeader} {nextNextTitle} {nextNextLengthPretty} {nextNextComment}
                                </td>
                            </tr>
                        </table>
                    </div>
                    <div class="realTime">
                        {realTime}
                    </div>
                </div></body>
                </html>
                """.format(
                    **locals()
                )
            )
            self.send_response(200)
            self.end_headers()
            self.wfile.write(message)
            return



def main():

    print "starting server"

    server = BaseHTTPServer_HTTPServer(('localhost', SERVER_PORT), GenericHandler)

    while True:
        server.handle_request()




if __name__ == "__main__":
    main()
