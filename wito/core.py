import os
import gi
import json
import inspect
from concurrent.futures import Future
gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import WebKit, Gio, GLib
from wito.interface import API
from wito.utils import app_base_path, wito_base_path
from wito.extensions.ext_loader import extension_manager


class WitoProtocolHandler:
    def __init__(self):
        pass

    def handle_request(self, request):
        uri = request.get_uri()
        scheme, path = uri.split('://', 1)        
        path = path.split('?')[0]        
        file_path = os.path.join(app_base_path(), path)
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            content_type, _ = Gio.content_type_guess(file_path, None)
            with open(file_path, 'rb') as f:
                contents = f.read()
            
            stream = Gio.MemoryInputStream.new_from_data(contents, None)
        else:
            request.finish_error(Gio.IOErrorEnum.NOT_FOUND, "File not found")

        request.finish(stream, len(contents), content_type)
        return True


class WebView(WebKit.WebView):
    def __init__(self, window, extended_api, wito_config):
        self.content_manager = WebKit.UserContentManager()
        super().__init__(user_content_manager=self.content_manager)
        self.app_base_path = app_base_path()
        self.wito_base_path = wito_base_path()
        self.dev_mode = wito_config.get("devMode")
        self.wito_dev_mode = wito_config.get("witoDevMode")
        self.generate_bindings = wito_config.get("generateBindings", True)
        context = self.get_context()
        settings = self.get_settings()

        if self.dev_mode:
            settings.set_property("enable-developer-extras", self.dev_mode)
            settings.set_property("enable-write-console-messages-to-stdout", True)
        
        protocol_handler = WitoProtocolHandler()        
        context.register_uri_scheme("wito", protocol_handler.handle_request)
        if extended_api:
            self.api = extended_api(self, window, wito_config.get("version"), wito_config.get("witoDevMode"))
        else:
            self.api = API(self, window, wito_config.get("version"), wito_config.get("witoDevMode"))

        self.connect("load-changed", self.on_load_changed)
        self.get_user_content_manager().register_script_message_handler("Invoke")
        self.get_user_content_manager().connect("script-message-received::Invoke", self.on_invoke)
        
        settings.set_enable_javascript(True)
        settings.set_hardware_acceleration_policy(WebKit.HardwareAccelerationPolicy.ALWAYS)
        settings.set_user_agent_with_application_details("Wito", wito_config.get("version"))
        self.load_uri('wito://index.html')
        self.inject_bindings() 
        self.load_extensions()
        self.cleanup()

    def cleanup(self):
        if not self.dev_mode:
            del self.app_base_path
        del self.wito_base_path

    def load_extensions(self):
        extension_manager(
            self.wito_base_path,
            self.app_base_path,
            self.wito_dev_mode,
            self.api,
            self
            )

    def on_load_changed(self, web_view, load_event):
        if load_event == WebKit.LoadEvent.FINISHED:
            self.api.execute_pending_js()
            if self.dev_mode:
                from wito.file_watcher import setup_file_watcher
                inspector = self.get_inspector()
                if inspector:
                    inspector.show()
                    GLib.timeout_add_seconds(
                        1,
                        setup_file_watcher,
                        self.app_base_path,
                        self.reload,
                        ('.html', '.js', '.css'))

    def inject_bindings(self):
        try:
            with open(f"{self.wito_base_path}/js/interface.js", 'r') as file:
                interface_js = file.read()

            if self.generate_bindings:
                with open(f"{self.wito_base_path}/js/method_template.js", 'r') as file:
                    method_template = file.read()
                    
                with open(f"{self.wito_base_path}/js/property_template.js", 'r') as file:
                    property_template = file.read()

                # Generate method bindings
                method_bindings = []
                for method_name, method in inspect.getmembers(self.api, inspect.ismethod):
                    if hasattr(method, '_exposed'):
                        params = inspect.signature(method).parameters
                        params_list = ', '.join(params.keys())
                        args_object = ', '.join(f"{name}: {name}" for name in params.keys())
                        
                        binding = method_template\
                            .replace('METHOD_NAME', method_name)\
                            .replace('PARAMS', params_list)\
                            .replace('ARGS_OBJECT', args_object)
                        method_bindings.append(binding)

                # Generate property bindings
                property_bindings = []
                for prop_name, prop in inspect.getmembers(self.api.__class__, lambda o: isinstance(o, property)):
                    if hasattr(prop.fget, '_exposed'):
                        binding = property_template.replace('PROP_NAME', prop_name)
                        property_bindings.append(binding)

                js_bindings = interface_js\
                    .replace('// METHOD_BINDINGS_PLACEHOLDER', '\n'.join(method_bindings))\
                    .replace('// PROPERTY_BINDINGS_PLACEHOLDER', '\n'.join(property_bindings))\
                    .replace('// WITO_DEV_MODE_PLACEHOLDER', str(self.wito_dev_mode).lower())\
                    .replace('// APP_DEV_MODE_PLACEHOLDER', str(self.dev_mode).lower())
            else:
                js_bindings = interface_js\
                    .replace('// WITO_DEV_MODE_PLACEHOLDER', str(self.wito_dev_mode).lower())\
                    .replace('// APP_DEV_MODE_PLACEHOLDER', str(self.dev_mode).lower())

            # Create and add the user script
            user_script = WebKit.UserScript.new(
                js_bindings,
                WebKit.UserContentInjectedFrames.TOP_FRAME,
                WebKit.UserScriptInjectionTime.START,
                None,
                None
            )
            self.get_user_content_manager().add_script(user_script)
        except Exception as e:
            print(f"Error injecting wito.js and bindings: {e}")


    def on_invoke(self, user_content_manager, js_result):
        call_id = None
        try:
            message = js_result.to_string()
            if self.wito_dev_mode:
                print(f"Received message: {message}")
            data = json.loads(message)
            method_name = data.get('method')
            args = data.get('args', {})
            call_id = data.get('id')

            if method_name in self.api.exposed_methods:
                method = self.api.exposed_methods[method_name]
                result = method(**args)
                if self.wito_dev_mode:
                    print(f"Calling method: {method_name}")
                    print(f"Method result: {result}")

                if isinstance(result, Future):
                    self.handle_future(call_id, result)
                else:
                    self.send_response(call_id, result)
            else:
                print(f"Method not found: {method_name}")
                self.send_error(call_id, f"Method '{method_name}' not found")
        except Exception as e:
            print(f"Error in on_invoke: {e}")
            if call_id is not None:
                self.send_error(call_id, str(e))

    def handle_future(self, call_id, future):
        def on_future_done(future):
            try:
                result = future.result(timeout=30)
                self.send_response(call_id, result)
            except TimeoutError:
                self.send_error(call_id, "Operation timed out")
            except Exception as e:
                self.send_error(call_id, str(e))

        future.add_done_callback(on_future_done)

    def send_response(self, call_id, result):
        try:
            js = f"wito._resolveCall('{call_id}', {json.dumps(result)})"
            self.api.eval_js(js)
        except TypeError as e:
            print(f"Error serializing result: {e}")
            self.send_error(call_id, "Error serializing result")

    def send_error(self, call_id, error_message):
        js = f"wito._rejectCall('{call_id}', {json.dumps(error_message)})"
        self.api.eval_js(js)

