import os
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib


def notify(win, title, body, priority='normal'):
    # We need a desktop file for notification to work
    try:
        # Get DBus connection
        connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)

        # Get app information
        app_id = win.get_application().get_application_id()
        theme = Gtk.IconTheme.new()
        
        # Look for .desktop file
        desktop_file_locations = [
            f"/usr/share/applications/{app_id}.desktop",
            f"/usr/local/share/applications/{app_id}.desktop",
            os.path.expanduser(f"~/.local/share/applications/{app_id}.desktop")
        ]

        app_name = None
        icon_path = ""
        
        # Get app name and icon from desktop file
        for desktop_file_path in desktop_file_locations:
            if os.path.exists(desktop_file_path):
                try:
                    desktop_file = Gio.DesktopAppInfo.new_from_filename(desktop_file_path)
                    if desktop_file:
                        icon_name = desktop_file.get_icon().to_string()
                        app_name = desktop_file.get_name()
                        
                        # Try to get icon path
                        if not os.path.exists(icon_name):
                            icon_info = theme.lookup_icon(
                                icon_name,
                                None,
                                48,
                                1,
                                Gtk.TextDirection.NONE,
                                0
                            )
                            if icon_info:
                                icon_path = icon_info.get_filename()
                        else:
                            icon_path = icon_name
                except Exception as e:
                    print(f"Error reading desktop file: {e}")

        # Convert priority to urgency level
        urgency = {
            'low': 0,
            'normal': 1,
            'high': 2,
            'urgent': 2
        }.get(priority, 1)

        # Create hints dictionary using GLib.Variant
        hints = {
            'urgency': GLib.Variant('y', urgency),
            'desktop-entry': GLib.Variant('s', app_id),
            'category': GLib.Variant('s', f'{app_id}.notification')
        }

        # Create parameters variant
        params = GLib.Variant('(susssasa{sv}i)', (
            app_name or app_id,  # app_name (use app_id if app_name not found)
            0,                   # replaces_id
            icon_path,          # app_icon
            title,              # summary
            body,               # body
            [],                 # actions
            hints,              # hints
            -1                  # timeout
        ))

        # Send notification
        result = connection.call_sync(
            'org.freedesktop.Notifications',          
            '/org/freedesktop/Notifications',         
            'org.freedesktop.Notifications',         
            'Notify',                                 
            params,                                   
            GLib.VariantType('(u)'),                 
            Gio.DBusCallFlags.NONE,                  
            -1,                                       
            None                                     
        )

        if result:
            notification_id = result.unpack()[0]
            return {"success": True, "id": notification_id}
        else:
            return {"success": False, "message": "Failed to get notification ID"}

    except Exception as e:
        print(f"Failed to send notification: {str(e)}")
        return {"success": False, "message": f"Failed to send notification: {str(e)}"}




