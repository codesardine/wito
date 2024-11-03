# Wito Configuration

The configuration file (`wito-config.json`) allows you to customize various aspects of your Wito application.

Create a wito-config.json file in your project root:

## Configuration Structure

```json
{   
    "wito": {
        "generateBindings": true
    },
    "window": {
        "title": "wito",
        "width": 1200,
        "height": 800,
        "isFullScreen": false,
        "isMaximized": false,
        "isResizable": true
    }
}
```

## Settings Reference

### Wito Settings

| Property           | Type    | Default | Description                                                      |
|--------------------|---------|---------|------------------------------------------------------------------|
| generateBindings   | boolean | true    | Enables automatic generation of JavaScript bindings for Python methods |

### Window Settings

| Property       | Type    | Default | Description                                              |
|----------------|---------|---------|----------------------------------------------------------|
| title          | string  | "wito"  | The title of the application window                      |
| width          | number  | 1200    | Initial window width in pixels                           |
| height         | number  | 800     | Initial window height in pixels                          |
| isFullScreen   | boolean | false   | Whether the window should start in fullscreen mode       |
| isMaximized    | boolean | false   | Whether the window should start maximized                |
| isResizable    | boolean | true    | Whether the window can be resized by the user            |
