import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib
from wito.window import Window
from wito.utils import load_config

class Application(Gtk.Application):
    def __init__(self, extended_api, config, dev_mode, wito_dev_mode=False):
        win_config = config.get("window")
        title = win_config.get("title")
        super().__init__(
            application_id=f"io.wito.{title.replace(' ', '')}",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.config = config
        self.version = "0.1"  
        self.dev_mode = dev_mode
        self.wito_dev_mode = wito_dev_mode
        self.window = None
        self.extended_api = extended_api

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        if not self.window:
            self.window = Window(
                extended_api = self.extended_api,
                config = self.config,
                application=self,
                version=self.version,
                dev_mode=self.dev_mode,
                wito_dev_mode = self.wito_dev_mode
            )

    def run(self):
        self.register()
        self.activate()
        self.quit()


def start(extended_api = None, dev_mode: bool = False):

    config = load_config()
    app = Application(extended_api, config, dev_mode=dev_mode)
    app.run()

    while Gtk.Window.get_toplevels().get_n_items() > 0:
        GLib.MainContext.default().iteration(True)
