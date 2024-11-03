import inspect
import json
from gi.repository import GLib, Gio


class PythonJavaScriptBridge:
    def __init__(self, webview, window, version, wito_dev_mode):
        self.wito_dev_mode = wito_dev_mode
        self.view = webview
        self.win = window
        self.version = version
        self.exposed_methods = {}
        self.pending_js = []
        self.register_exposed_methods()
        self.win.connect('realize', self.on_realize)

    def register_exposed_methods(self):
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, '_exposed'):
                if self.wito_dev_mode:
                    print(f"Registering exposed method: {name}")
                self.exposed_methods[name] = method

    def eval_js(self, js, callback=None):
        if self.wito_dev_mode:
            print(f"Evaluating JS: {js}")
        if self.view.is_loading():
            self.pending_js.append((js, callback))
        else:
            self.view.evaluate_javascript(js, -1, None, callback or None)

    def execute_pending_js(self):
        while self.pending_js:
            if self.wito_dev_mode:
                print("Executing pending JS")   
            js, callback = self.pending_js.pop(0)
            self.view.evaluate_javascript(js, -1, None, callback or None)

    def emit_event(self, event, data):
        """
        Emits an event to the JavaScript layer with associated data.

        This method bridges Python and JavaScript by triggering events in the JavaScript
        environment. It serializes the Python data to JSON and calls the JavaScript
        _emitEvent method.

        Args:
            event (str): The name of the event to emit.
            data (Any): The data to pass with the event. Must be JSON-serializable.

        Raises:
            TypeError: If data cannot be serialized to JSON.
            ValueError: If event name contains invalid characters.

        Example:
            ```python
            # Simple event with string data
            interface.emit_event('user_logged_in', 'John Doe')

            # Event with dictionary data
            interface.emit_event('data_updated', {
                'id': 123,
                'status': 'complete',
                'timestamp': '2023-01-01'
            })

            # Event with list data
            interface.emit_event('items_changed', [1, 2, 3, 4])
            ```

        Note:
            - The data must be JSON-serializable
            - Event names should follow JavaScript naming conventions
            - The JavaScript layer must have the _emitEvent method defined
            - Large data structures may impact performance

        See Also:
            - eval_js: Method used to execute JavaScript code
            - json.dumps: JSON serialization method
        """
        js = f"wito._emitEvent('{event}', {json.dumps(data)})"
        self.eval_js(js)

    def on_realize(self, widget):
        self.settings = Gio.Settings.new("org.gnome.desktop.interface")
        self.settings.connect("changed::color-scheme", self.on_theme_change)
        self.win.get_display().get_monitors().connect('items-changed', self.on_monitors_changed)
        GLib.idle_add(self.set_initial_theme)

    def check_theme(self):
        try:
            color_scheme = self.settings.get_string("color-scheme")
            is_dark = color_scheme == "prefer-dark"
            if self.wito_dev_mode:
                print(self.settings.list_keys())
                print(f"Color scheme: {color_scheme}", f"isDark:{is_dark}")
            return is_dark
        except Exception as e:
            print(f"Error checking theme: {e}")

    def set_initial_theme(self):
        is_dark = self.check_theme()
        self.set_body_theme_class(is_dark)

    def on_theme_change(self, settings, key):        
        is_dark = self.check_theme()
        self.set_body_theme_class(is_dark)

    def theme_emit_change_event(self):
        """
        Emits a JavaScript event to notify about desktop theme mode changes.
        
        Evaluates JavaScript code that triggers a 'isDarkTheme' event with an empty
        payload object.
        
        Example JavaScript usage:            
            wito.addEventListener('isDarkTheme', (event) => {
                // Handle screen change event
                console.log('Screen configuration changed');
            });

        Note:
            - This event automatically gets subscribed to when the bridge is instantiated.
            - The event automatically adds light-theme or dark-theme classes to document body.
        """
        js = "wito._emitEvent('isDarkTheme', {})"
        self.eval_js(js)


    def set_body_theme_class(self, is_dark):
        theme_class = 'dark-theme' if is_dark else 'light-theme'
        js = f"""
            document.body.classList.remove('dark-theme', 'light-theme');
            document.body.classList.add('{theme_class}');
            console.log('Desktop changed to {theme_class}');
        """
        self.eval_js(js)

    def on_monitors_changed(self, list_model, position, removed, added):
        self.screen_emit_change_event()

    def screen_emit_change_event(self):
        """
        Emits a JavaScript event to notify about screen configuration changes.
        
        Evaluates JavaScript code that triggers a 'screenChange' event with an empty
        payload object.
        
        Example JavaScript usage:            
            wito.addEventListener('screenChange', (event) => {
                // Handle screen change event
                console.log('Screen configuration changed');
            });
        """
        js = "wito._emitEvent('screenChange', {})"
        self.eval_js(js)