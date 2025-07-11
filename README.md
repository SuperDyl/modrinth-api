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

## Setup

### Python

This was created using Python 3.13
but it should be made to work in any currently supported version of Python.

`pip install requests types-requests`