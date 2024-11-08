import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk
from wito.core import WebView as webview


class Window(Gtk.ApplicationWindow):
    def __init__(self, *args, extended_api, config, application, **kwargs):
        win_config = config.get("window")
        super().__init__(*args, application=application, **kwargs)

        self.app = application
        self.webview = webview(self, extended_api, config.get("wito"))
        self.set_default_size(
            win_config.get("width"),
            win_config.get("height"))
        
        if win_config.get("isResizable"):
            self.set_resizable(win_config.get("isResizable", True))
                
        if win_config.get("isFullScreen"):
            self.fullscreen()
        elif win_config.get("isMaximized"):
            self.maximize()
        
        self.set_title(win_config.get("title"))
        self.set_child(self.webview)
        self.connect("close-request", self.on_close_request)
        self.connect('realize', self.on_realize)
        self.cleanup()
        self.present()

        
    def cleanup(self):
        del self.webview
        
    def on_realize(self, widget):
        # seems on wayland windows cannot be centered
        self.present()

    def on_close_request(self, *args):
        """Handle the window close request by destroying the window."""
        self.destroy()
        if self.app:
            self.app.quit()
        else:
            print("Warning: Application reference not found. Unable to quit the application.")
        return True 

    def show(self):
        super().show()
    