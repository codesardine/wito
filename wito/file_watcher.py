import gi
gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import GLib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback, files):
        self.files = files
        self.callback = callback
        
    def on_modified(self, event):
        if not event.is_directory:
            if event.src_path.endswith(self.files):
                GLib.idle_add(self.callback)

def setup_file_watcher(app_path, callback=lambda: None, files=()):
    event_handler = FileChangeHandler(callback, files)
    observer = Observer()
    observer.schedule(event_handler, app_path, recursive=True)
    observer.start()