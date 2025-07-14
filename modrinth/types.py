from typing import Literal

MODRINTH_ID = str
"""
A unique, unchanging 8-digit base62 ID used by
projects, versions, users, threads, teams, and reports.

Documentation: https://docs.modrinth.com/api/#identifiers
"""

MODRINTH_TEMP_ID = str
r"""
A user-friendly, changeable id used by projects (slugs) and usernames.

For a project, follows the regex: `^[\w!@$()``.+,"\-']{3,64}$`

Documentation: https://docs.modrinth.com/api/operations/getproject/
and https://docs.modrinth.com/api/#identifiers
"""

SHA1_HASH = str
"""
A sha1 hash. For Modrinth, this usually refers to a file's hash.

The hash is a string with regex: [0-9a-f]{40}
"""

SHA512_HASH = str
"""
A sha512 hash. For Modrinth, this usually refers to a file's hash.

The hash is a string with regex: [0-9a-f]{128}
"""

HASH = SHA1_HASH | SHA512_HASH
"""
A hash encoded as base64, usually of a file. Modrinth supports both sha1 and sha512.
"""

LOADER = str
"""
The program expected to use the given file.

This can be mod loaders like fabric or odd options like resource or data packs.
There is an official list of loaders which Modrinth recognizes.
"""

GAME_VERSION = str
"""
A version of Minecraft in a format like `1.7.10`, `1.20`, or presumably `1.21.X`.
"""

SVG = str
"""
An SVG stored as a string of the SVG's XML path data.
"""


class Empty:
    """
    A field that is missing from json data.

    This is different from `None` because it represents the field not being included.

    This is a singleton and so only one instance of it exists.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


EMPTY = Empty()
"""
A field that is missing from json data.

This is different from `None` because it represents the field not being included.
"""

IMAGE_FILE_EXTENSION = Literal[
    "png", "jpg", "jpeg", "bmp", "gif", "webp", "svg", "svgz", "rgb"
]
"""
Allowed file extensions/file types for images in Modrinth.
"""

IMAGE = bytes
"""
Some image, usually used for projects and users.

Allowed formats are `png`, `jpg`, `jpeg`, `bmp`, `gif`, `webp`, `svg`, `svgz`, and `rgb`.
"""

REQUESTED_PROJECT_STATUS = Literal["approved", "archived", "unlisted", "private", "draft"]
"""
The status that the project owner would like the project to be.
"""

SUPPORT = Literal["required", "optional", "unsupported", "unknown"]
"""
The client or server side support for this project.
"""

FILE_TYPE = Literal["required-resource-pack", "optional-resource-pack"]
"""
The type of the additional file, used mainly for adding resource packs to datapacks.
"""

VERSION_TYPE = Literal["release", "beta", "alpha"]
"""
The stage of version stability.
"""

VERSION_STATUS = Literal["listed", "archived", "draft", "unlisted", "scheduled", "unknown"]
"""
Status of the specified version.
"""

REQUESTED_VERSION_STATUS = Literal["listed", "archived", "draft", "unlisted"]
"""
The status the project owner would like the version to be.
"""

HASH_ALGORITHM = Literal["sha1", "sha512"]