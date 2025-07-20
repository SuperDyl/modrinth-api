# ModrinthApi

This project offers python types and methods
for interacting with Modrinth's API.
Each API endpoint is represented by a method
and each returned JSON object is parsed into Python classes
with type annotations.
This should make it as easy as possible to use Modrinth's API.

Currently, only endpoints which don't require authentication are supported.
These can be accessed as part of the `ModrinthApi` object.
Create the object with your `user_agent` string
(see [the modrinth docs](https://docs.modrinth.com/api/#authentication))
and then call each method from the instance of that object.

All potential errors are noted for each method.
You should use `try-catch` blocks and deal with each error appropriately.

## Install

The current install process is to copy the `modrinth` directory into your project.
You should then be able to access the methods with `import modrinth` and `from modrinth import ...` .

## Setup

### Python

This was created using Python 3.13
but it should be made to work in any currently supported version of Python.

If you're using this as part of a project
or to further develop this project, 
I recommend setting up a virtual environment.
That can be as simple as:

```bash
python3 -m venv .venv
```

After setting up the environment, 
you can enable it in your command line with:

* MacOS/Linux: `source .venv/bin/activate`
* Windows: `.\.venv\bin\activate.bat`

### Dependencies

This project depends on `requests` and `requests-toolbelt` .
They can both be easily installed using the `requirements.txt` file:

```bash
python3 -m pip install -r requirements.txt
```

You can also install them individually:

```bash
pip install requests requests-toolbelt
```

### MyPy

You may find it helpful to install mypy and use it to track types.
I recommend installing mypy system-wide (so not within `.venv` )

```bash
python3 -m pip install mypy
```

## Development

### Tests

Run the tests with the `unittest` module:

```bash
python -m unittest discover tests
```
