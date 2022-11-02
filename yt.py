#!/usr/bin/env python3
# cython: language_level=3
"""Script to play media from YouTube

Author:
    Sheikh Saad Abdullah

Repo:
    https://github.com/cybardev/ytpy
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
MEDIA_PLAYER: str = "mpv"
DOWNLOADER: str = "youtube-dl"
DOWNLOAD_DIR: str = os.environ.get(
    "YT_DLOAD_DIR",
    os.path.expanduser("~")
    + ("\\Videos\\" if platform.system() == "Windows" else "/Videos/"),
)


def error(err_code=0, msg="", **kwargs):
    """Show an error message and exit with requested error code

    Args:
        err_code (int, optional): the error code. Defaults to 0.
        msg (str, optional): the error message. Defaults to "".
    """
    print(msg)
    for err, err_msg in kwargs.items():
        print(f"{err}: {err_msg}")

    sys.exit(err_code)


def check_deps(deps_list: list[str]):
    """Check if required dependencies are installed

    Args:
        deps_list (list[str]): list of dependencies to check
    """
    for deps in deps_list:
        if not installed(deps):
            error(1, msg=f"Dependency {deps} not found.\nPlease install it.")


def filter_dupes(id_list: list[str]):
    """Generator to filter out duplicates from a list of strings
    Used instead of set() to preserve order of search results

    Args:
        li (list[str]): the list to be filtered

    Yields:
        video_id (str): unique video ID
    """
    seen = set()
    for video_id in id_list:
        if video_id not in seen:
            seen.add(video_id)
            yield video_id


def get_media_url(search_str: str, result_num: int) -> str:
    """Function to get media URL

    Args:
        search_str (str): the string to search for

    Returns:
        str: the deduced media URL
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

    len_results = len(search_results)
    if len_results == 0 or len_results < result_num:
        error(msg="No results found.")

    video_id = search_results[result_num - 1]
    media_url = "https://www.youtube.com/watch?v=" + video_id

    return media_url


def play(media_url: str, options: str):
    """Call the media player and play requested media

    Args:
        media_url (str): the command line arguments to the player
        options (str): the string to search for
    """
    os.system(f"{MEDIA_PLAYER} {options} {media_url}")


def getopts() -> argparse.Namespace:
    """Retrieve command-line arguments

    Returns:
        argparse.Namespace: command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Play YouTube media without API",
        epilog="List of mpv hotkeys: https://defkey.com/mpv-media-player-shortcuts",
        allow_abbrev=False,
    )
    parser.add_argument(
        "query",
        help="media to play",
        metavar="SEARCH_STRING",
        type=str,
        nargs="*",
    )
    parser.add_argument(
        "-n",
        help="nth result to play or download",
        metavar="RESULT_NUM",
        type=int,
        default=1,
        dest="res_num",
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


def arg_parse(args: argparse.Namespace) -> tuple:
    """Process parsed command-line arguments

    Args:
        args (argparse.Namespace): parsed arguments

    Returns:
        tuple: media query string, mpv flags
    """
    query: str = " ".join(args.query)
    flags: str = ""

    if args.url_mode:
        error(0, get_media_url(query, args.res_num))

    if not args.video_mode:
        flags = "--ytdl-format=bestaudio --no-video"

    if args.download_mode:
        check_deps([DOWNLOADER, "ffmpeg"])
        if flags:
            flags = "-f 'bestaudio' -x --audio-format mp3"
        os.system(
            f"{DOWNLOADER} -o '{DOWNLOAD_DIR}%(title)s.%(ext)s' {flags} \
                {get_media_url(query, args.res_num)}"
        )
        sys.exit(0)

    while not query:
        query = " ".join(input(f"❮{'🎵' if flags else '🎬'}❯ ").split()).strip()

    return query, flags, args.res_num


def loop(query, flags, res_num):
    """Play the chosen media as user requests

    Args:
        query (str): media to play
        flags (str): mpv flags
    """
    cache_url: str = ""

    while query not in ("", "q"):
        media_url = cache_url if cache_url else get_media_url(query, res_num)
        play(media_url, flags)

        answer = input("Play again? (y/n): ")
        if answer.lower() != "y":
            cache_url = ""
            query = input("Play next (q to quit): ")


if __name__ == "__main__":
    try:
        loop(*arg_parse(getopts()))
    except KeyboardInterrupt:
        pass
    error(0, "\nQuitting...")
