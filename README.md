# yt.py

## A Python script to play media from YouTube without needing API keys

![figlet][banner_img]

### Sections

Click to navigate.

-   [Dependencies](#Dependencies)
-   [Installation](#Installation)
-   [Usage](#Usage)
    -   [Examples](#Examples)
-   [Credits](#Credits)
-   [Extras](#Extras)

### Dependencies

-   [Python 3][python] (tested on PyPy 3.7.9 and CPython 3.9.1)
-   [mpv][mpv]
-   [youtube-dl][ytdl]
-   [ffmpeg][ffmpeg]

### Installation

-   Download the file from the Releases page: [yt.py][release]
-   Place it in your `$PATH` and make it executable.
-   Enjoy!

### Usage

```sh
usage: yt.py [-h] [-u] [-v] [-d] [-n NUM] [-o DIR] [SEARCH_STRING ...]

Play YouTube media without API

positional arguments:
  SEARCH_STRING         media to play

options:
  -h, --help            show this help message and exit
  -u, --url             display URL instead of playing
  -v, --video           play video instead of music
  -d, --download        download media instead of playing
  -n NUM, --num NUM     nth result to play or download
  -o DIR, --output DIR  folder to save downloaded media

List of mpv hotkeys: https://defkey.com/mpv-media-player-shortcuts
```

#### Examples

-   Stream audio:

    `yt.py gurenge band cover`

-   Download audio:

    `yt.py -d astronomia`

-   Watch a video:

    `yt.py -v rickroll`

-   Download a video:

    `yt.py -dv penguin flock`

-   Play the audio of the second search result:

    `yt.py -n 2 plastic love daft punk`

-   Download a video to a directory other than `$HOME/Videos` (default location):

    `yt.py -do "$HOME/Music/" darude sandstorm`

PS: [Here][mpv_hotkeys]'s a list of mpv keyboard shortcuts for your convenience.

### Credits

-   [pystardust][pystardust]'s [ytfzf][ytfzf]
-   [This article][article] I found during my quest to implement a simplified version of ytfzf in Python3

### Extras

#### About the `.pyx` file

**I'm currently not updating it anymore. Please consider using the `.py` file instead**

Cython is supposed to be faster but I don't really know Cython so I couldn't optimize it as well. If you can do so, feel free to make a fork, and maybe even a pull request so the script can be improved. It'll be a learning experience for me as well.

As for the performance... It may be slightly faster but the program is still network-bound. Which means, faster internet = faster query = media is played sooner.

Compile an executable file using [this shell script][cymake] if you want.

<!-- Images -->

[banner_img]: https://user-images.githubusercontent.com/50134239/109390169-2c1b9000-793a-11eb-94d4-d6b3edc631b7.png

<!-- Links -->

[release]: https://github.com/cybardev/ytpy/releases/download/v2.0/yt.py
[python]: https://www.python.org/downloads/
[mpv]: https://github.com/mpv-player/mpv
[ytdl]: https://github.com/ytdl-org/youtube-dl
[ffmpeg]: https://github.com/FFmpeg/FFmpeg
[mpv_hotkeys]: https://defkey.com/mpv-media-player-shortcuts
[pystardust]: https://github.com/pystardust
[ytfzf]: https://github.com/pystardust/ytfzf
[article]: https://www.codeproject.com/articles/873060/python-search-youtube-for-video
[cymake]: https://github.com/cybarspace/cymake
