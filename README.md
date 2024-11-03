# Wito

Wito is a Python-based, Linux-only desktop application framework that bridges web technologies with native system capabilities through WebKit. It allows to create efficient, modern applications with the flexibility of web interfaces and the performance of native desktop applications. Wito offers seamless interoperability between JavaScript and Python.

This was done out out my disire to have a framework for fast Linux prototyping and is not tested across diferent distributions.

## Dependencies
* GTK 4
* WebKit 6
* Python Gobject Introspection

## Quick Started
Check examples directory

```
poetry build
poetry install

```

Python example

```
from wito.application import start


if __name__ == "__main__":
    start(
        dev_tools=True  # Enable dev tools 
    )
```

JavaScript example

```
wito.onReady(() => {
    await wito.notify('Hello', 'This is a notification', 'normal');    
});
```

[API Docs](https://codesardine.github.io/wito/)
