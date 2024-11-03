import os
from functools import wraps
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from gi.repository import Gtk
from wito.utils import app_base_path
from wito.notifications import notify
import wito.screen
from wito.bridge import PythonJavaScriptBridge
  

class API(PythonJavaScriptBridge):
    num_cpus = max(os.cpu_count() or 1, 4) # Default to 4 if cpu_count() returns None
    workers = min(num_cpus + 1, 16) # Use the number of CPU cores + 1, but cap it at 16
    executor = ThreadPoolExecutor(workers)
    # print(f"Number of CPUs: {num_cpus}")
    def __init__(self, webview, window, version, wito_dev_mode):
        super().__init__(webview, window, version, wito_dev_mode)
    
    @staticmethod
    def thread(func):
        """Decorator that runs a method in a separate Python thread.

        This decorator executes the method in a new thread to prevent blocking
        the main thread. Particularly useful for I/O operations or
        long-running tasks.

        Example:
            ```python
            class MyClass:
                @expose
                @thread  
                def long_operation(self):
                    time.sleep(1)
                    return {"status": "completed"}
            ```

        Note:
            - Should be used for I/O or CPU-intensive operations
            - When used with @expose, @thread must be the inner decorator
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            def task():
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    return {"error": str(e)}

            future = API.executor.submit(task)
            return future

        return wrapper

    @staticmethod
    def expose(func):
        """Decorator that exposes a Python objects to the JavaScript runtime.

        Example:
            ```python
            class MyClass:
                def __init__(self, my_value):
                    self.my_property = my_value

                    @expose
                    def my_method(self, param):
                        return {"result": param}
                    
                    @property # read only property.
                    @expose  
                    def my_property(self):
                        return {"result": self.my_property}
                    
                    @my_property.setter # combine with above to turn it in a write property.
                    @expose  
                    def my_property(self, value):
                        self.my_property = value
                        return {"success": True}
            ```

        Note:
            - All exposed methods become async in JavaScript
            - Return values must be JSON-serializable
            - Can be combined with @thread decorator
        """
        func._exposed = True
        return func

    @expose
    def get_theme_mode(self):
        """Get the current theme mode of the application.

        Returns:
            dict: Dictionary containing theme mode status
                - is_dark (bool): True if dark theme is active
                - is_light (bool): True if light theme is active

        JavaScript Usage:
            ```javascript
            const theme = await wito.get_theme_mode();
            console.log('Dark mode:', theme.is_dark);
            console.log('Light mode:', theme.is_light);
            ```
        """
        settings = Gtk.Settings.get_default()
        is_dark = settings.get_property("gtk-application-prefer-dark-theme")
        return {
            "is_dark": is_dark,
            "is_light": not is_dark
        }

    @expose
    def screen_get_info(self):
        """Get information about the current screen.

        Returns:
            dict: Information includes geometry, position, size and primary and secondary monitors.

        JavaScript Usage:
            ```javascript
            const screenInfo = await wito.screen_get_info();
            console.log('Screen info:', screenInfo);
            ```
        """
        return wito.screen.get_info(self.win)

    @expose
    def win_is_fullscreen(self):
        """Check if the window is in fullscreen mode.

        Returns:
            bool: True if window is fullscreen, False otherwise

        JavaScript Usage:
            ```javascript
            const isFullscreen = await wito.win_is_fullscreen();
            console.log('Is fullscreen:', isFullscreen);
            ```
        """
        return self.win.is_fullscreen()

    @expose
    def win_fullscreen(self):
        """Set the window to fullscreen mode.

        JavaScript Usage:
            ```javascript
            await wito.win_fullscreen();
            ```
        """
        self.win.fullscreen()

    @expose
    def win_unfullscreen(self):
        """Exit fullscreen mode.

        JavaScript Usage:
            ```javascript
            await wito.win_unfullscreen();
            ```
        """
        self.win.unfullscreen()

    @expose
    def win_get_focus(self):
        """Check if the window has focus..

        JavaScript Usage:
            ```javascript
            const winGetfocus = await wito.win_get_focus();
            ```
        """
        self.win.get_focus()

    @expose
    def win_set_focus(self):
        """Set focus to the window.

        JavaScript Usage:
            ```javascript
            await wito.win_set_focus();
            ```
        """
        self.win.set_focus(self.view)

    @expose
    def win_set_title(self, title):
        """Set the window title.

        Args:
            title (str): The new title for the window

        Returns:
            dict: Status of the operation
                - success (bool): True if title was set successfully

        JavaScript Usage:
            ```javascript
            await wito.win_set_title('My App Title');
            ```
        """
        self.win.set_title(title)
        return {"success": True}

    @expose
    def win_get_size(self):
        """Get the current window size.

        Returns:
            dict: Window dimensions
                - width (int): Window width in pixels
                - height (int): Window height in pixels

        JavaScript Usage:
            ```javascript
            const size = await wito.win_get_size();
            console.log(`Window size: ${size.width}x${size.height}`);
            ```
        """
        width, height = self.window.get_size()
        return {"width": width, "height": height}

    @expose
    def win_set_size(self, width, height):
        """Set the window size.

        Args:
            width (int): Desired window width in pixels
            height (int): Desired window height in pixels

        Returns:
            dict: Status of the operation
                - success (bool): True if size was set successfully

        JavaScript Usage:
            ```javascript
            await wito.win_set_size(800, 600);
            ```
        """
        self.window.resize(width, height)
        return {"success": True}

    @expose
    def fs_get_app_path(self):
        """Get the application's base path.

        Returns:
            dict: Application path information
                - path (str): The base path of the application

        JavaScript Usage:
            ```javascript
            const appPath = await wito.fs_get_app_path();
            console.log('App path:', appPath.path);
            ```
        """
        return {"path": app_base_path()}

    @expose
    @thread
    def fs_list_dir(self, path):
        """List contents of a directory.

        Args:
            path (str): Path to the directory to list

        Returns:
            dict: Directory contents
                - contents (Liststr): List of file/directory names
                - error (str, optional): Error message if operation failed

        JavaScript Usage:
            ```javascript
            const result = await wito.fs_list_dir('/path/to/directory');
            if (result.contents) {
                console.log('Directory contents:', result.contents);
            } else {
                console.error('Error:', result.error);
            }
            ```
        """
        try:
            return {"contents": [str(p.name) for p in Path(path).iterdir()]}
        except OSError as e:
            return {"error": str(e)}

    @expose
    def fs_create_dir(self, path):
        """Create a new directory.

        Args:
            path (str): Path where to create the directory

        Returns:
            dict: Operation result
                - success (bool): True if directory was created
                - path (str): Absolute path of created directory
                - error (str, optional): Error message if operation failed

        JavaScript Usage:
            ```javascript
            const result = await wito.fs_create_dir('/path/to/new/directory');
            if (result.success) {
                console.log('Created directory at:', result.path);
            } else {
                console.error('Error:', result.error);
            }
            ```
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return {"success": True, "path": str(Path(path).resolve())}
        except OSError as e:
            return {"error": str(e)}

    @expose
    @thread
    def fs_del_file(self, path):
        """Delete a file.

        Args:
            path (str): Path to the file to delete

        Returns:
            dict: Operation result
                - success (bool): True if file was deleted
                - error (str, optional): Error message if operation failed

        JavaScript Usage:
            ```javascript
            const result = await wito.fs_del_file('/path/to/file.txt');
            if (result.success) {
                console.log('File deleted successfully');
            } else {
                console.error('Error:', result.error);
            }
            ```
        """
        try:
            Path(path).unlink()
            return {"success": True}
        except OSError as e:
            return {"error": str(e)}

    @expose
    @thread
    def fs_read_file(self, path):
        """Read contents of a file.

        Args:
            path (str): Path to the file to read

        Returns:
            dict: File contents or error
                - content (str): The contents of the file
                - error (str, optional): Error message if operation failed

        JavaScript Usage:
            ```javascript
            const result = await wito.fs_read_file('/path/to/file.txt');
            if (result.content) {
                console.log('File contents:', result.content);
            } else {
                console.error('Error:', result.error);
            }
            ```
        """
        try:
            return {"content": Path(path).read_text()}
        except OSError as e:
            return {"error": str(e)}

    @expose
    @thread
    def fs_save_file(self, path, content):
        """Write content to a file.

        Args:
            path (str): Path to the file to write
            content (str): Content to write to the file

        Returns:
            dict: Operation result
                - success (bool): True if file was written successfully
                - error (str, optional): Error message if operation failed

        JavaScript Usage:
            ```javascript
            const result = await wito.fs_save_file('/path/to/file.txt', 'Hello World!');
            if (result.success) {
                console.log('File written successfully');
            } else {
                console.error('Error:', result.error);
            }
            ```
        """
        try:
            Path(path).write_text(content)
            return {"success": True}
        except OSError as e:
            return {"error": str(e)}
        
    @expose
    def fs_file_exists(self, path):
        """Check if a file or directory exists.

        Args:
            path (str): Path to check

        Returns:
            dict: Check result
                - exists (bool): True if path exists
                - is_file (bool): True if path is a file
                - is_dir (bool): True if path is a directory
                - error (str, optional): Error message if operation failed

        JavaScript Usage:
            ```javascript
            const result = await wito.fs_file_exists('/path/to/check');
            if (result.exists) {
                console.log('Path exists');
                console.log('Is file:', result.is_file);
                console.log('Is directory:', result.is_dir);
            }
            ```
        """
        try:
            path_obj = Path(path)
            exists = path_obj.exists()
            return {
                "exists": exists,
                "is_file": exists and path_obj.is_file(),
                "is_dir": exists and path_obj.is_dir()
            }
        except OSError as e:
            return {"error": str(e)}

    @expose
    def notify(self, title, body, priority='normal'):
        """Show a system notification.

        Args:
            title (str): Title of the notification
            body (str): Body text of the notification
            priority (str, optional): Priority level ('low', 'normal', 'high'). Defaults to 'normal'

        Returns:
            dict: Operation result
                - success (bool): True if notification was shown successfully

        JavaScript Usage:
            ```javascript
            await wito.notify('Hello', 'This is a notification', 'normal');
            ```
        """
        notify(self.win, title, body, priority)
        return {"success": True}