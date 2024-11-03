import os
import gi
gi.require_version('WebKit', '6.0')
from gi.repository import WebKit
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class MergedContent:
    content: str
    sources: List[str]
    error_files: List[tuple[str, str]]


def extension_manager(wito_base_path, app_base_path, dev_mode, api, webview):
    """Load and merge all extension files."""
    try:
        # Collect files from both directories
        wito_files = _collect_extension_files(wito_base_path)
        app_files = _collect_extension_files(app_base_path)

        # Merge and inject CSS
        wito_css = _merge_files(dev_mode, wito_files['css'], file_type='css')
        app_css = _merge_files(dev_mode, app_files['css'], file_type='css')

        if wito_css and wito_css.content:
            _inject_css(webview, wito_css.content, "wito-styles")
            if dev_mode:
                print(f"Injected Wito CSS from: {', '.join(wito_css.sources)}")

        if app_css and app_css.content:
            _inject_css(webview, app_css.content, "app-styles")  # Fixed: added webview parameter
            if dev_mode:
                print(f"Injected App CSS from: {', '.join(app_css.sources)}")

        # Merge and inject JavaScript
        wito_js = _merge_files(dev_mode, wito_files['js'], file_type='js')
        app_js = _merge_files(dev_mode, app_files['js'], file_type='js')

        if wito_js and wito_js.content:
            api.eval_js(wito_js.content)
            if dev_mode:
                print(f"Injected Wito JS from: {', '.join(wito_js.sources)}")

        if app_js and app_js.content:
            api.eval_js(app_js.content)
            if dev_mode:
                print(f"Injected App JS from: {', '.join(app_js.sources)}")

        # Report any errors
        all_errors = []
        for result in [wito_css, app_css, wito_js, app_js]:
            if result and hasattr(result, 'error_files'):
                all_errors.extend(result.error_files)
        _report_errors(all_errors)

    except Exception as e:
        print(f"Error loading extensions: {str(e)}")

def _collect_extension_files(base_dir: str) -> Dict[str, List[str]]:
    """Collect all extension files from a directory."""
    files = {
        'css': [],
        'js': []
    }
    
    if not base_dir:
        return files

    ext_dir = os.path.join(base_dir, "extensions")
    if not os.path.exists(ext_dir):
        return files

    try:
        for filename in sorted(os.listdir(ext_dir)):
            file_path = os.path.join(ext_dir, filename)
            if not os.path.isfile(file_path):
                continue

            if filename.endswith('.css'):
                files['css'].append(file_path)
            elif filename.endswith('.js'):
                files['js'].append(file_path)
    except Exception as e:
        print(f"Error collecting files from {ext_dir}: {str(e)}")

    return files

def _merge_files(dev_mode: bool, file_paths: List[str], file_type: str = 'js') -> Optional[MergedContent]:
    """Merge multiple files into a single content string."""
    if not file_paths:
        return None

    merged_content = []
    processed_files = []
    error_files = []
    
    for file_path in file_paths:
        try:
            content = None
            try:
                content = Path(file_path).read_text()
            except OSError as e:
                error_files.append((file_path, str(e)))
                print(f"Error reading {file_path}: {str(e)}")
                continue

            if not content:
                continue

            file_name = os.path.basename(file_path)
            
            # Add source mapping in dev mode
            if dev_mode:
                merged_content.append(f"\n/* Source: {file_name} */")
            
            # Minify in production mode
            if not dev_mode:
                if file_type == 'css':
                    content = _minify_css(content)
                elif file_type == 'js':
                    content = _minify_js(content)
            
            merged_content.append(content)
            processed_files.append(file_name)
            
        except Exception as e:
            error_files.append((file_path, str(e)))
            print(f"Error processing {file_path}: {str(e)}")

    return MergedContent(
        content="\n".join(merged_content) if merged_content else "",
        sources=processed_files,
        error_files=error_files
    )

def _minify_css(content: str) -> str:
    """Basic CSS minification."""
    return content.strip()

def _minify_js(content: str) -> str:
    """Basic JavaScript minification."""
    return content.strip()

def _inject_css(webview, css_content: str, identifier: str):
    """Inject CSS content into the WebView."""
    if not css_content:
        return

    try:
        style_sheet = WebKit.UserStyleSheet(
            source=css_content,
            injected_frames=WebKit.UserContentInjectedFrames.TOP_FRAME,
            level=WebKit.UserStyleLevel.USER,
        )
        webview.content_manager.add_style_sheet(style_sheet)
    except Exception as e:
        print(f"Error injecting CSS {identifier}: {str(e)}")

def _report_errors(error_files: List[tuple[str, str]]):
    """Report any errors that occurred during file processing."""
    if error_files:
        print("\nErrors occurred while processing the following files:")
        for file_path, error in error_files:
            print(f"- {os.path.basename(file_path)}: {error}")
    