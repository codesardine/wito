import os
import sys
import json

def get_desktop_env():
    desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
    current_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    
    if current_desktop:
        return current_desktop.split(':')[0]
    
    elif desktop_session:
        if desktop_session in ['gnome', 'kde', 'xfce']:
            return desktop_session
        elif 'xfce' in desktop_session:
            return 'xfce'
        elif desktop_session.startswith('ubuntu'):
            return 'gnome'
        
    # Check for specific environment variables
    elif os.environ.get('KDE_FULL_SESSION'):
        return 'kde'
    elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
        return 'gnome'
    
    return None

def app_base_path():
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    else:
        if os.path.isabs(sys.argv[0]):
            path = os.path.dirname(sys.argv[0])
        else:
            path = os.path.dirname(os.path.abspath(sys.argv[0]))
            
            if not os.path.exists(path):
                path = os.path.dirname(os.path.abspath(__file__))
    
    return path
    
def wito_base_path():
    return os.path.dirname(os.path.abspath(__file__))

def load_config():
    """Load application configuration from a JSON file located in the same directory as the HTML file."""
    config_file = app_base_path() + '/wito-config.json'
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file '{config_file}' not found.")

    with open(config_file, 'r') as f:
        config = json.load(f)

    return config