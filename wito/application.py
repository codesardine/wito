import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib
from wito.window import Window
from wito.utils import load_config

class Application(Gtk.Application):
    def __init__(self, extended_api, config, dev_mode=False, wito_dev_mode=False):
        win_config = config.get("window")
        title = win_config.get("title")
        if "wito" not in config:
           config["wito"] = {}
        
        wito_config = config.get("wito")
        wito_config["devMode"] = dev_mode
        wito_config["witoDevMode"] = wito_dev_mode
        wito_config["version"] = "0.1"

        super().__init__(
            application_id=f"io.wito.{title.replace(' ', '')}",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        self.config = config
        self.window = None
        self.extended_api = extended_api

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        if not self.window:
            self.window = Window(
                extended_api = self.extended_api,
                config = self.config,
                application=self
            )

        self.cleanup()

    def run(self):
        self.register()
        self.activate()
        self.quit()

    def cleanup(self):
        attributes_to_cleanup = [
            'extended_api',
            'config',
            'window',
        ]
        
        for attr in attributes_to_cleanup:
            if hasattr(self, attr) and attr is not None:
                delattr(self, attr)


def start(extended_api = None, dev_mode: bool = False):

    config = load_config()
    app = Application(extended_api, config, dev_mode=dev_mode)
    app.run()

    while Gtk.Window.get_toplevels().get_n_items() > 0:
        GLib.MainContext.default().iteration(True)
