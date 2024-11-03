def get_info(win):
        display = win.get_display()
        monitor_list = display.get_monitors()
        monitors = []
        for i in range(monitor_list.get_n_items()):
            monitor = monitor_list.get_item(i)
            geometry = monitor.get_geometry()
            is_primary = geometry.x == 0 and geometry.y == 0
            scale_factor = monitor.get_scale_factor()
            monitors.append({
                "index": i,
                "position": {
                    "x": geometry.x,
                    "y": geometry.y
                },
                "size": {
                    "width": geometry.width * scale_factor,
                    "height": geometry.height * scale_factor
                },
                "is_valid": monitor.is_valid(),
                "is_primary": is_primary
            })
            
        return {
            "number_of_monitors": len(monitors),
            "monitors": monitors
        }