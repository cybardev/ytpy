#!/usr/bin/env python3
# cython: language_level=3
"""Script to play media from YouTube

Author:
    Sheikh Saad Abdullah (cybardev)

Repo:
    https://github.com/cybardev/ytpy
"""
# required imports
from types import MappingProxyType  # make truly immutable constants
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

CONST = MappingProxyType(
    {
        "media_player": "mpv",
        "downloader": "yt-dlp",
        "converter": "ffmpeg",
        "video_id_re": re.compile(r'"videoId":"(.{11})"'),
        "fixed_mode_signal": -1,
    }
)


def error(msg: str = "", code: int = 0, **kwargs):
    """Show an error message and exit with requested error code

    Args:
        msg (str, optional): error message. Defaults to ""
        code (int, optional): error code. Defaults to 0
    """
    print(msg)
    for err, err_msg in kwargs.items():
        print(f"{err}: {err_msg}")

    sys.exit(code)


def check_deps(deps_list: list):
    """Check if required dependencies are installed

    Args:
        deps_list (list[str]): list of dependencies to check
    """
    for deps in deps_list:
        if not installed(deps):
            error(f"Dependency {deps} not found.\nPlease install it.", code=1)


def filter_dupes(id_list: list[str]):
    """Generator to filter out duplicates from a list of strings
    Used instead of set() to preserve order of search results

    Args:
        li (list[str]): list to be filtered

    Yields:
        video_id (str): unique video ID
    """
    seen = set()
    for video_id in id_list:
        if video_id not in seen:
            seen.add(video_id)
            yield video_id


def validate_url(url: str) -> bool:
    try:
        return bool(request.urlopen(url))
    except (urlerr.URLError, ValueError):
        return False


def get_media_url(search_str: str, result_num: int) -> str:
    """Retrieve URL of requested media

    Args:
        search_str (str): string to search for
        result_num (int): nth result to play

    Returns:
        str: the deduced media URL
    """
    try:
        # if URL is given, ensure validity and return
        if validate_url(search_str):
            return search_str

        # get the YouTube search-result page for given search string
        html_content = (
            request.urlopen(
                "https://www.youtube.com/results?"
                + parse.urlencode({"search_query": search_str})
            )
            .read()
            .decode()
        )
    except urlerr.URLError:
        error("No internet connection.", code=1)

    search_results = list(
        filter_dupes(CONST["video_id_re"].findall(html_content))
    )

    if not (0 < len(search_results) >= result_num):
        error("No results found.")

    return "https://www.youtube.com/watch?v=" + search_results[result_num - 1]


def play(media_url: str, options: str):
    """Call the media player and play requested media

    Args:
        media_url (str): command line arguments to the player
        options (str): URL of media to play
    """
    os.system(f"{CONST['media_player']} {options} {media_url}")


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
        "-u",
        "--url",
        help="display URL instead of playing",
        action="store_true",
        dest="url_mode",
    )
    parser.add_argument(
        "-f",
        "--fixed",
        help="play media from given URL",
        action="store_true",
        dest="fixed_mode",
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
    parser.add_argument(
        "-n",
        "--num",
        help="nth result to play or download",
        metavar="NUM",
        type=int,
        dest="res_num",
        default=1,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="folder to save downloaded media",
        metavar="DIR",
        type=str,
        dest="download_dir",
        default=os.path.expanduser("~")
        + (
            "\\Downloads\\" if "Windows" in platform.system() else "/Downloads/"
        ),
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
        error(get_media_url(query, args.res_num))

    if not args.video_mode:
        flags = "--ytdl-format=bestaudio --no-video"

    if args.fixed_mode:
        return query, flags, CONST["fixed_mode_signal"]

    if args.download_mode:
        check_deps([CONST["downloader"], CONST["converter"]])
        if flags:
            flags = "-f 'bestaudio' -x --audio-format mp3"
        os.system(
            f"{CONST['downloader']} -o '{args.download_dir}%(title)s.%(ext)s' \
                {flags} {get_media_url(query, args.res_num)}"
        )
        sys.exit(0)

    check_deps([CONST["media_player"]])
    while not query:
        query = " ".join(input(f"❮{'🎵' if flags else '🎬'}❯ ").split()).strip()

    return query, flags, args.res_num


def loop(query: str, flags: str, res_num: int):
    """Play the chosen media as user requests

    Args:
        query (str): media to play
        flags (str): mpv flags
        res_num (int): nth result to play
    """
    if res_num == CONST["fixed_mode_signal"]:
        play(query, flags)
    else:
        media_url: str = ""
        while query not in ("", "q"):
            # only fetch media URL if it's not cached
            if not media_url:
                media_url = get_media_url(query, res_num)

            play(media_url, flags)

            answer = input("Play again? (y/n): ")
            if answer.lower() != "y":
                media_url = ""  # clear cache
                query = input("Play next (q/Enter to quit): ")


if __name__ == "__main__":
    try:
        loop(*arg_parse(getopts()))
    except (KeyboardInterrupt, EOFError) as sentinel:
        pass
    error("\nQuitting...")
