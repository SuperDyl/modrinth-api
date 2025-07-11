MODRINTH_ID = str
"""
A unique, unchanging 8-digit base62 ID used by
projects, versions, users, threads, teams, and reports.

Documentation: https://docs.modrinth.com/api/#identifiers
"""

MODRINTH_TEMP_ID = str
"""
A user-friendly, changeable id used by projects (slugs) and usernames.

For a project, follows the regex: `^[\w!@$()`.+,"\-']{3,64}$`

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
A hash, usually of a file. Modrinth supports both sha1 and sha512.
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
