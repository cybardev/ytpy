![figlet](https://user-images.githubusercontent.com/50134239/109390169-2c1b9000-793a-11eb-94d4-d6b3edc631b7.png)

## A Python script to play media from YouTube without needing API keys.

### Sections:

Click to navigate.

- [Dependencies](#Dependencies)
- [Installation](#Installation)
- [Usage](#Usage)
    - [Examples](#Examples)
- [Credits](#Credits)
- [Extras](#Extras)

### Dependencies
- [Python 3](https://www.python.org/downloads/) (tested on PyPy 3.7.9 and CPython 3.9.1)
- [mpv](https://github.com/mpv-player/mpv)
- [youtube-dl](https://github.com/ytdl-org/youtube-dl)
- [ffmpeg](https://github.com/FFmpeg/FFmpeg)

### Installation
- Download the file from the Releases page: [ytplay](https://github.com/cybarspace/ytplay/releases/download/v1.1.0/ytplay)
- Place it in your `$PATH` and make it executable.
- Enjoy!

### Usage
```
Usage: ytplay [OPTIONS] <search query>
           OPTIONS:
             -h                    Show this help text
             -d  <search query>    Download video
             -v  <search query>    Play video (audio-only if not specified)
             -u  <search query>    Fetch video URL

List of mpv hotkeys: https://defkey.com/mpv-media-player-shortcuts
```

#### Examples
- Stream audio:

	`ytplay gurenge band cover`

- Watch a video:

	`ytplay -v rickroll`

- Download a video:

	`ytplay -d penguin flock`

- Play the audio of the second search result:

    `YT_NUM=2 ytplay plastic love daft punk`

- Download a video to a directory other than `$HOME/Videos` (default location):

    `YT_DLOAD_DIR=$HOME/Downloads/ ytplay -d darude sandstorm`

PS: [Here](https://defkey.com/mpv-media-player-shortcuts)'s a list of mpv keyboard shortcuts for your convenience.

### Credits
- [pystardust](https://github.com/pystardust)'s [ytfzf](https://github.com/pystardust/ytfzf)
- [This article](https://www.codeproject.com/articles/873060/python-search-youtube-for-video) I found during my quest to implement a simplified version of ytfzf in Python3

### Extras
**About the `.pyx` file...**

#### I'm currently not updating it anymore. Please consider using the `.py` file instead.

Cython is supposed to be faster but I don't really know Cython so I couldn't optimize it as well. If you can do so, feel free to make a fork, and maybe even a pull request so the script can be improved. It'll be a learning experience for me as well.

As for the performance... It may be slightly faster but the program is still network-bound. Which means, faster internet = faster query = media is played sooner.

Compile an executable file using [this shell script](https://github.com/cybarspace/cymake) if you want.
