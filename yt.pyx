#!/usr/bin/env python3
# cython: language_level=3
"""
Script to play media from YouTube

@author: Sheikh Saad Abdullah
My Github: https://github.com/cybarspace
"""
# required imports
from shutil import which as installed  # to check dependencies
from urllib import error as urlerr # no internet connection
from urllib import request  # to get data from YouTube
from urllib import parse  # to parse data obtained
import readline  # for a more user-friendly prompt
import getopt  # to parse command-line arguments
import sys  # to exit with error codes
import os  # to execute media player
import re  # to find media URL from search results

# important constants (some can be altered by environment variables)
cdef:
    # the nth result to play
    int RES_NUM = int(os.environ.get("YT_NUM", 1))
    # play either "video" or "music" when no args given
    str OP_MODE = os.environ.get("YT_MODE", "music")
    # where to put downloaded files
    str DLOAD_DIR = os.environ.get("YT_DLOAD_DIR", "$HOME/Videos/")
    # the media player to use
    str PLAYER = "mpv"
    # program to process the youtube videos
    str DOWNLOADER = "youtube-dl"
# PS: Make sure to change the DLOAD_DIR to what you prefer...
# especially if you're using this script from Windows


def error(int err_code=0, str msg=".", **kwargs):
    """
    Show an error message and exit with requested error code

    @param err_code: the error code
    @param msg: the error message
    @param **kwargs: extra messages
    """
    cdef str err, err_msg
    # if no error message given...
    if msg == ".":
        # set the error message to usage info
        msg = str(
            f"Usage: ytplay [OPTIONS] <search query>\n"
            + "         OPTIONS:\n"
            + "             -h                    Show this help text\n"
            + "             -d  <search query>    Download video to {DLOAD_DIR}\n"
            + "             -v  <search query>    Play video (script plays audio-only by default)\n"
            + "             -u  <search query>    Fetch video URL"
        )
    # print the given or default error message
    print(msg)
    # if any extra messages are given...
    for err, err_msg in kwargs.items():
        # print the extra messages
        print(f"{err}: {err_msg}")
    # exit with given or default error code
    sys.exit(err_code)


cpdef void check_deps(list deps_list):
    """
    Check if required dependencies are installed

    @param deps_list: list of dependencies to check
    """
    cdef str deps
    # check each item in given dependency list
    # and see if it is installed on the system
    for deps in deps_list:
        # if it is not installed
        if not installed(deps):
            # show an error message and exit with code 1
            error(1, msg=f"Dependency {deps} not found.\nPlease install it.")


def filter_dupes(list li):
    """
    Generate to filter out duplicates from a list of strings

    @param li: the list to be filtered
    """
    cdef:
        str id  # a video ID in the list li
        set seen = set()  # set of seen IDs
    # for each video ID in list li...
    for id in li:
        # if it's unique...
        if id not in seen:
            # add it to the list of seen IDs
            seen.add(id)
            # and return it to the caller
            yield id


cpdef str get_media_url(str search_str="rickroll"):
    """
    Function to get media URL

    @param search_str: the string to search for
    """
    cdef:
        str query_string, html_content, video_id, media_url
        list search_results
    # compile regex pattern for faster search
    VIDEO_ID_RE = re.compile(r'"videoId":"(.{11})"')
    # format the given search string for use in URLs
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
        # raise an error and quit
        error(1, "No internet connection.")
    # find the first video ID from result page
    search_results = list(filter_dupes(VIDEO_ID_RE.findall(html_content)))
    # if no results are found...
    if len(search_results) == 0:
        # print error message and exit
        error(msg="No results found.")
    # select the nth result and deduce its URL
    video_id = search_results[RES_NUM - 1]  # extract the video ID
    media_url = "https://www.youtube.com/watch?v=" + video_id  # process the URL
    # return the URL of requested media
    return media_url


cpdef void play(str options, str search_str):
    """
    Call the media player and play requested media

    @param options: the command line arguments to the player
    @param search_str: the string to search for
    """
    # check if dependencies are satisfied
    check_deps([PLAYER, DOWNLOADER])
    # if everything is ok, play requested media
    os.system(f"{PLAYER} {options} {get_media_url(search_str)}")


cpdef void download(str search_str):
    """
    Call the media downloader and download requested media

    @param search_str: the string to search for
    """
    # check if dependencies are satisfied
    check_deps(
        [DOWNLOADER, "ffmpeg"]
    )  # ffmpeg may be needed to merge downloaded media
    # if everything is ok, download requested media
    os.system(
        f"{DOWNLOADER} -o '{DLOAD_DIR}%(title)s.%(ext)s' {get_media_url(search_str)}"
    )


cpdef str sentinel_prompt(list ans, str sym="λ"):
    """
    Propmt to keep asking user for input
    until a valid input is given

    @param ans the initil user input
    @param sym the symbol to show in the prompt (purely decorative)
    @return string of query words
    """
    # while no answer is given...
    while len(ans) == 0:
        # keep nagging user for input
        print("Please enter search query:")
        ans = input(f"❮{sym}❯ ").split()
    # return the entered words as a string
    return str(" ".join(ans).strip())


cpdef void main():
    """
    Main program logic
    """
    cdef:
        str req_search, flags, answer, prompt_sym
        list opts, extras
    # parse flags and arguments
    try:
        # decide whether to play video or audio only for the session
        opts, extras = getopt.getopt(sys.argv[1:], "hudv:")

        # if options contain help flag...
        if "-h" in opts[0]:
            # show help and exit normally
            error()
        # if options contain URL flag...
        if "-u" in opts[0]:
            # show the URL and quit
            error(0, get_media_url(opts[0][1] + " ".join(extras).rstrip()))
        # if options contain download flag...
        elif "-d" in opts[0]:
            # process the name of media to search
            req_search = opts[0][1] + " ".join(extras).rstrip()
            # download the requested media
            download(req_search)
            # exit normally
            sys.exit()
        # if options contain video flag...
        elif "-v" in opts[0]:
            # process the name of media to search
            req_search = opts[0][1] + " ".join(extras).rstrip()
            # set flags to empty, to use defaults
            flags = ""
    # if invalid flags are used...
    except getopt.GetoptError:
        error(2, UnknownArgs="Unknown options given.")
    # when no flags are given...
    except IndexError:
        # and no arguments are given...
        if OP_MODE == "music":
            # and default operation mode is set to music...
            prompt_sym = "🎵"
            flags = "--ytdl-format=bestaudio --no-video"
        elif OP_MODE == "video":
            # and default operation mode is set to video...
            prompt_sym = "🎬"
            flags = ""
        else:
            # if default operation mode is invalid, raise error
            error(
                2,
                UnknownValue="variable OP_MODE has an unknown value."
                        + "\nValid options are \"music\" and \"video\""
            )
        # when arguments are given, prepare to play media
        req_search = sentinel_prompt(extras, prompt_sym)

    # while the user doesn't quit by pressing ^C (Ctrl+C)...
    try:
        # play the requested item and loop over input
        while req_search not in {"q", ""}:
            # call the mpv media player with processed flags and URL
            play(flags, req_search)
            # when done, ask if user wants to repeat the last played media
            answer = input("Play again? (y/n): ")
            # process user request
            if answer.lower() in {"n", ""}:
                # if user answers no, ask what to play next, or quit
                req_search = input("Play next (q to quit): ")
            elif answer.lower() == "y":
                # if user answers yes, keep playing
                continue
            else:
                # if invalid option is chosen, exit with code 2
                error(2, "Unrecognized option. Quitting...")
    # if user presses ^C (Ctrl+C) to quit the program
    except KeyboardInterrupt:
        # show a message and quit
        error(0, "\nQuitting...")
    # exit normally when everything is done
    error(0, "")


# when invoked as a program...
if __name__ == "__main__":
    # execute the main function and process flags and arguments accordingly
    main()

