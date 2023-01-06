import os
import sys
import time
import json
import asyncio
import logging
import argparse
import websockets
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
    # level=logging.CRITICAL,
)

DEBOUNCE_SECONDS = 0.1

filesChanged = Queue() # threadsafe task list

class FileModifiedHandler(PatternMatchingEventHandler):
    """Event Handler to communicate modified events for consumption by ws server"""

    def __init__(
        self,
        filesChanged,
        patterns=None,
        ignore_patterns=None,
        ignore_directories=None,
        case_sensitive=False,
    ):
        super().__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.filesChanged = filesChanged
        self.last_updated_at = time.time()

    def on_any_event(self, event):
        """fill queue for consumption by websocket server"""

        if time.time() - self.last_updated_at > DEBOUNCE_SECONDS:
            filesChanged.put(event.src_path)
            self.last_updated_at = time.time()

def start_file_observer(reload_paths, reload_patterns):
    """starts observer in new thread"""

    observer = Observer()
    for path in reload_paths:
        observer.schedule(
            FileModifiedHandler(filesChanged, patterns=reload_patterns),
            path,
        )
    observer.start()

    return observer

async def serve_websocket(host, port):
    async with websockets.serve(handle_files_changed, host, port):
        await asyncio.Future() # run forever

async def handle_files_changed(websocket):
    """simple handler to consume fileChange tasks"""

    async for message in websocket:

        path = filesChanged.get() # blocks until fileChange tasks appear
        event = {
            'type' : 'fileChange',
            'path' : path,
        }
        await websocket.send(json.dumps(event))
        logging.debug(f'sent event: {event}')
        filesChanged.task_done()

def get_args():

    parser = argparse.ArgumentParser(
        prog = 'autoreload.py',
        description = '''
            Watches paths given as argument, or a pattern, starts a websocket server
            and notifies client on file modifying events. Defaults to port 5001,
            but any port (higher than 1024) can be specified with the --port option.'''
    )
    parser.add_argument(
        'reload_paths',
        nargs='*',
        default=[os.path.dirname(__file__)],
        help='Paths to be autoreloaded, defaults to parent dir of this file.'
    )
    parser.add_argument(
        '--pattern',
        nargs='*',
        action='extend',
        dest='reload_patterns',
        help='Pattern to be watched, defaults to *.html'
    )
    parser.add_argument(
        '--host',
        nargs='*',
        action='extend',
        dest='hosts',
        help='Allowed hosts for websocket server (leave empty for allowing all).'
    )
    parser.add_argument('--port', type=int, default=5001, help='Port for the websocket server.')

    args = parser.parse_args()

    if args.hosts is None:
        args.hosts = ['localhost']

    if args.reload_patterns is None:
        args.reload_patterns = ['*.html']

    return args

def cleanup(observer):

    logging.info('KeyboardInterrupt, exiting gracefully..')
    observer.stop()
    observer.join()
    logging.info('observer cleaned up, exiting.')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

if __name__ == '__main__':

    try:
        args = get_args()

        logging.info('starting observer...')
        observer = start_file_observer(args.reload_paths, args.reload_patterns)

        asyncio.run(serve_websocket(args.hosts, args.port))

        if observer:
            observer.join()

        logging.info('observer joined')

    except KeyboardInterrupt:
        cleanup(observer)
