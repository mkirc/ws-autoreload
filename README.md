# ws-autoreload

A file-watching websocket server for autoreloading files in
the browser.

## Installation

Clone this repository, install packages via `pip install -r requirements.txt`,
add 'autoreload.js' to the .html you want to reload and get crackin'.

## Usage
```
usage: autoreload.py [-h] [--pattern [RELOAD_PATTERNS ...]]
                     [--host [HOSTS ...]] [--port PORT]
                     [reload_paths ...]

Watches paths given as argument, or a pattern, starts a websocket server and
notifies client on file modifying events. Defaults to port 5001, but any
port (higher than 1024) can be specified with the --port option.

positional arguments:
  reload_paths          Paths to be autoreloaded, defaults to parent dir of
                        this file.

optional arguments:
  -h, --help            show this help message and exit
  --pattern [RELOAD_PATTERNS ...]
                        Pattern to be watched, defaults to *.html
  --host [HOSTS ...]    Allowed hosts for websocket server ('' for
                        allowing all).
  --port PORT           Port for the websocket server.
```

## Notes

* The 'autoreload.js' script tries to connect to localhost:5001, so keep
in mind to adjust the port there as well.

* You can adjust the verbosity of the server by modifying the loglevel in
'autoreload.py'. Setting it to `CRITICAL` effectively mutes output to stdout.
