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
import argparse  # to parse command-line arguments
import readline  # for a more user-friendly prompt
import platform  # to check platform being used
import sys  # to exit with error codes
import os  # to execute media player
import re  # to find media URL from search results

# important constants (some can be altered by environment variables)
# the nth result to play or download
RESULT_NUM: int = int(os.environ.get("YT_NUM", 1))
# play either "video" or "music" when no args given
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


def error(err_code=0, msg="", **kwargs):
    """
    Show an error message and exit with requested error code

    @param err_code: the error code
    @param msg: the error message
    @param **kwargs: extra messages
    """
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


def get_media_url(search_str) -> str:
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


def getopts():
    parser = argparse.ArgumentParser(
        description="Play YouTube media without API",
        epilog="List of mpv hotkeys: https://defkey.com/mpv-media-player-shortcuts",
        allow_abbrev=False,
    )
    parser.add_argument(
        "query",
        help="media to play",
        metavar="search_string",
        type=str,
        nargs="*",
    )
    parser.add_argument(
        "-u",
        "--url",
        help="display URL instead of playing",
        action="store_true",
        dest="url_mode",
    )
    parser.add_argument(
        "-v",
        "--video",
        help="play video instead of music",
        action="store_true",
        dest="video_mode",
    )
    parser.add_argument(
        "-d",
        "--download",
        help="download media instead of playing",
        action="store_true",
        dest="download_mode",
    )
    return parser.parse_args()


def arg_parse(args) -> tuple:
    """
    Process flags and arguments

    @return search query and mpv flags
    """
    query: str = " ".join(args.query)
    flags: str = ""

    if args.url_mode:
        error(0, get_media_url(query))

    if not args.video_mode:
        flags = "--ytdl-format=bestaudio --no-video"

    if args.download_mode:
        check_deps([DOWNLOADER, "ffmpeg"])
        os.system(
            f"{DOWNLOADER} -o '{DLOAD_DIR}%(title)s.%(ext)s' \
                {get_media_url(query)}"
        )
        sys.exit(0)

    while not query:
        query = " ".join(input(f"❮{'🎵' if flags else '🎬'}❯ ").split()).strip()

    return query, flags


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
        loop(*arg_parse(getopts()))
    except KeyboardInterrupt:
        pass
    error(0, "\nQuitting...")
