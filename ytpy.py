#!/usr/bin/env python3
# cython: language_level=3
"""
Script to play media from YouTube

@author: Sheikh Saad Abdullah
@repo: https://github.com/cybardev/ytpy
"""
# required imports
from shutil import which as installed  # to check dependencies
from urllib import error as urlerr  # no internet connection
from urllib import request  # to get data from YouTube
from urllib import parse  # to parse data obtained
import readline  # for a more user-friendly prompt
import platform  # to check platform being used
import getopt  # to parse command-line arguments
import sys  # to exit with error codes
import os  # to execute media player
import re  # to find media URL from search results

# important constants (some can be altered by environment variables)
# the nth result to play or download
RESULT_NUM: int = int(os.environ.get("YT_NUM", 1))
# play either "video" or "music" when no args given
MPV_FLAGS: str = (
    ""
    if os.environ.get("YT_MODE") == "video"
    else "--ytdl-format=bestaudio --no-video"
)
# where to put downloaded files
DLOAD_DIR: str = os.environ.get(
    "YT_DLOAD_DIR",
    os.path.expanduser("~")
    + ("\\Videos\\" if platform.system() == "Windows" else "/Videos/"),
)
# the media player to use
PLAYER: str = "mpv"
# program to process the youtube videos
DOWNLOADER: str = "youtube-dl"


def error(err_code=0, msg=None, **kwargs):
    """
    Show an error message and exit with requested error code

    @param err_code: the error code
    @param msg: the error message
    @param **kwargs: extra messages
    """
    if msg == None:
        msg = str(
            "Usage: ytpy [OPTIONS] <search query>\n"
            + "           OPTIONS:\n"
            + "             -h                    Show this help text\n"
            + "             -d  <search query>    Download video\n"
            + "             -v  <search query>    Play video \
                    (script plays audio-only by default)\n"
            + "             -u  <search query>    Fetch video URL\n"
            + "\n"
            + "List of mpv hotkeys: https://defkey.com/mpv-media-player-shortcuts"
        )

    print(msg)
    for err, err_msg in kwargs.items():
        print(f"{err}: {err_msg}")

    sys.exit(err_code)


def check_deps(deps_list):
    """
    Check if required dependencies are installed

    @param deps_list: list of dependencies to check
    """
    for deps in deps_list:
        if not installed(deps):
            error(1, msg=f"Dependency {deps} not found.\nPlease install it.")


def filter_dupes(id_list):
    """
    Generator to filter out duplicates from a list of strings
    Used instead of set() to preserve order of search results

    @param li: the list to be filtered
    """
    seen = set()
    for video_id in id_list:
        if video_id not in seen:
            seen.add(video_id)
            yield video_id


def get_media_url(search_str="rickroll") -> str:
    """
    Function to get media URL

    @param search_str: the string to search for
    @return the deduced media URL
    """
    video_id_re = re.compile(r'"videoId":"(.{11})"')
    query_string = parse.urlencode({"search_query": search_str})

    # when connected to the internet...
    try:
        # get the YouTube search-result page for given search string
        html_content = (
            request.urlopen("https://www.youtube.com/results?" + query_string)
            .read()
            .decode()
        )
    # if not connected to the internet...
    except urlerr.URLError:
        error(1, "No internet connection.")

    search_results = list(filter_dupes(video_id_re.findall(html_content)))

    if len(search_results) == 0:
        error(msg="No results found.")

    video_id = search_results[RESULT_NUM - 1]
    media_url = "https://www.youtube.com/watch?v=" + video_id

    return media_url


def play(media_url, options):
    """
    Call the media player and play requested media

    @param options: the command line arguments to the player
    @param search_str: the string to search for
    """
    os.system(f"{PLAYER} {options} {media_url}")


def download(media_url):
    """
    Call the media downloader and download requested media

    @param search_str: the string to search for
    """
    os.system(
        f"{DOWNLOADER} -o '{DLOAD_DIR}%(title)s.%(ext)s' \
                {media_url}"
    )


def sentinel_prompt(ans) -> str:
    """
    Propmt to keep asking user for input
    until a valid input is given

    @param ans the initil user input
    @param sym the symbol to show in the prompt (purely decorative)
    @return string of query words
    """
    print("Please enter search query:")
    while len(ans) == 0:
        ans = " ".join(input(f"❮{'🎵' if MPV_FLAGS else '🎬'}❯ ").split()).strip()

    return ans


def optparse(opts, extras) -> tuple:
    if "-h" in opts[0]:
        error()
    if "-u" in opts[0]:
        error(0, get_media_url(opts[0][1] + " ".join(extras).rstrip()))
    elif "-d" in opts[0]:
        check_deps([DOWNLOADER, "ffmpeg"])
        download(get_media_url(opts[0][1] + " ".join(extras).rstrip()))
        sys.exit(0)
    elif "-v" in opts[0]:
        check_deps([PLAYER])
        return opts[0][1] + " ".join(extras).rstrip(), ""
    else:
        error(2, UnknownArgs="Unknown options given.")


def argparse() -> tuple:
    """
    Process flags and arguments

    @return search query and mpv flags
    """
    req_search: str = ""
    flags: str = ""

    try:
        opts, extras = getopt.getopt(sys.argv[1:], "hudv:")

        if len(opts):
            req_search, flags = optparse(opts, extras)
        else:
            check_deps([PLAYER])
            req_search = sentinel_prompt(extras)
            if not flags:
                flags = MPV_FLAGS
    except getopt.GetoptError:
        error(2, UnknownArgs="Unknown options given.")

    return req_search, flags


def loop(query, flags):
    cache_url: str = ""

    while query not in ("", "q"):
        media_url = cache_url if cache_url else get_media_url(query)
        play(media_url, flags)

        answer = input("Play again? (y/n): ")
        if answer.lower() != "y":
            cache_url = ""
            query = input("Play next (q to quit): ")


if __name__ == "__main__":
    """
    Main program logic
    """
    try:
        loop(*argparse())
    except KeyboardInterrupt:
        pass
    error(0, "\nQuitting...")
