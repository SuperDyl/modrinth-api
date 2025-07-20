from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Literal, TypeAlias, TypeVar, cast

from modrinth.types import (
    Empty,
    EMPTY,
    FILE_TYPE,
    GAME_VERSION,
    HASH,
    HASH_ALGORITHM,
    LOADER,
    MODRINTH_ID,
    MODRINTH_TEMP_ID,
    PROJECT_STATUS,
    PROJECT_TYPE,
    REQUESTED_PROJECT_STATUS,
    REQUESTED_VERSION_STATUS,
    SHA1_HASH,
    SHA512_HASH,
    SUPPORT,
    SVG,
    VERSION_STATUS,
    VERSION_TYPE,
)

DATE_FORMAT = "%YYYY-%MM-%DD"


@dataclass
class VersionNumber:
    """
    A semantic version number.

    The semantic version is essentially major.minor.patch.
    See https://en.wikipedia.org/wiki/Software_versioning#Semantic_versioning
    and https://docs.modrinth.com/api/operations/getversionfromidornumber/
    """

    major: int
    minor: int
    patch: int

    @classmethod
    def from_version_number_str(cls, version_number_str: str) -> "VersionNumber":
        major, minor, patch = version_number_str.split(".")

        return VersionNumber(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
        )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return (
            f"VersionNumber(major={self.major}, minor={self.minor}, patch={self.patch})"
        )


@dataclass
class VersionDependency:
    """
    A specific version of a project that this version depends on.

    Documentation: https://docs.modrinth.com/api/operations/getprojectversions/#responses
    See Array/dependencies
    """

    version_id: MODRINTH_ID | None
    project_id: MODRINTH_ID | None
    file_name: str | None
    dependency_type: Literal["required", "optional", "incompatible", "embedded"]

    @classmethod
    def from_json(cls, json_: dict) -> "VersionDependency":
        """
        Convert a dictionary representation of a JSON `VersionDependency` object into a Python object.

        :param json_: The dictionary containing the same keys expected by `VersionDependency`
        :raise KeyError: If `json_["dependency_type"]` is not defined.
        """
        return VersionDependency(
            version_id=json_.get("version_id"),
            project_id=json_.get("project_id"),
            file_name=json_.get("file_name"),
            dependency_type=json_["dependency_type"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON VersionDependency object.
        """
        return {
            "version_id": self.version_id,
            "project_id": self.project_id,
            "file_name": self.file_name,
            "dependency_type": self.dependency_type,
        }


@dataclass
class HashMapping:
    """
    Hashes of the file.

    Documentation: https://docs.modrinth.com/api/operations/getprojectversions/#responses
    See Array/files/hashes
    """

    sha512: SHA512_HASH
    sha1: SHA1_HASH

    @classmethod
    def from_json(cls, json_: dict) -> "HashMapping":
        """
        :param json_: The dictionary containing the same keys expected by `HashMapping`
        :raise KeyError: If either `json_["sha512"]` or `json_["sha1"]` are not defined.
        """
        return HashMapping(
            sha512=json_["sha512"],
            sha1=json_["sha1"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `HashMapping` object.
        """
        return {
            "sha512": self.sha512,
            "sha1": self.sha1,
        }


@dataclass
class VersionFile:
    """
    A file available for download for this version.

    Documentation: https://docs.modrinth.com/api/operations/getprojectversions/#responses
    See Array/files
    """

    hashes: HashMapping
    url: str
    filename: str
    primary: bool
    size: int
    file_type: FILE_TYPE | None

    @classmethod
    def from_json(cls, json_: dict) -> "VersionFile":
        """
        :param json_: The dictionary containing the same keys expected by `VersionFile`
        :raise KeyError: If any values for `VersionFile` or `HashMapping` (within `hashes`) are not defined.
        """
        return VersionFile(
            hashes=HashMapping.from_json(json_["hashes"]),
            url=json_["url"],
            filename=json_["filename"],
            primary=json_["primary"],
            size=json_["size"],
            file_type=json_["file_type"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `VersionFile` object.
        """
        return {
            "hashes": self.hashes.to_json(),
            "url": self.url,
            "filename": self.filename,
            "primary": self.primary,
            "size": self.size,
            "file_type": self.file_type,
        }


@dataclass
class Version:
    """
    All data associated with a specific version of a project.

    Documentation: https://docs.modrinth.com/api/operations/getprojectversions/#responses
    """

    name: str
    version_number: VersionNumber
    changelog: str | None
    dependencies: list[VersionDependency]
    game_versions: list[GAME_VERSION]
    version_type: VERSION_TYPE
    loaders: list[str]
    featured: bool
    status: VERSION_STATUS
    requested_status: REQUESTED_VERSION_STATUS | None
    id: MODRINTH_ID
    project_id: MODRINTH_ID
    author_id: MODRINTH_ID
    date_published: datetime
    downloads: int
    changelog_url: str | None
    files: list[VersionFile]

    @classmethod
    def from_json(cls, json_: dict) -> "Version":
        """
        :param json_: The dictionary containing the same keys expected by `Version`
        :raise KeyError: If any required values for `Version` are not defined.
        """
        return Version(
            name=json_["name"],
            version_number=VersionNumber.from_version_number_str(
                json_["version_number"]
            ),
            changelog=json_.get("changelog"),
            dependencies=[
                VersionDependency.from_json(x) for x in json_["dependencies"]
            ],
            game_versions=json_["game_versions"],
            version_type=json_["version_type"],
            loaders=json_["loaders"],
            featured=json_["featured"],
            status=json_["status"],
            requested_status=json_.get("requested_status"),
            id=json_["id"],
            project_id=json_["project_id"],
            author_id=json_["author_id"],
            date_published=datetime.fromisoformat(json_["date_published"]),
            downloads=json_["downloads"],
            changelog_url=json_.get("changelog_url"),
            files=[VersionFile.from_json(x) for x in json_["files"]],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `Version` object.
        """
        return {
            "name": self.name,
            "version_number": str(self.version_number),
            "changelog": self.changelog,
            "dependencies": [d.to_json() for d in self.dependencies],
            "game_versions": self.game_versions,
            "version_type": self.version_type,
            "loaders": self.loaders,
            "featured": self.featured,
            "status": self.status,
            "requested_status": self.requested_status,
            "id": self.id,
            "project_id": self.project_id,
            "author_id": self.author_id,
            "date_published": self.date_published.strftime(DATE_FORMAT),
            "downloads": self.downloads,
            "changelog_url": self.changelog_url,
            "files": [f.to_json() for f in self.files],
        }


@dataclass
class VersionDependencyCreate:
    """
    A specific version of a project that this version depends on.

    Mostly used when creating a new version.

    Documentation: https://docs.modrinth.com/api/operations/createversion/
    See Array/dependencies
    """

    version_id: MODRINTH_ID | None | Empty
    project_id: MODRINTH_ID | None | Empty
    file_name: str | None | Empty
    dependency_type: Literal["required", "optional", "incompatible", "embedded"]

    @classmethod
    def from_json(cls, json_: dict) -> "VersionDependencyCreate":
        """
        Convert a dictionary representation of a JSON `VersionDependencyCreate` object into a Python object.

        :param json_: The dictionary containing the same keys expected by `VersionDependencyCreate`
        :raise KeyError: If `json_["dependency_type"]` is not defined.
        """
        return VersionDependencyCreate(
            version_id=json_.get("version_id", Empty),
            project_id=json_.get("project_id", Empty),
            file_name=json_.get("file_name", Empty),
            dependency_type=json_["dependency_type"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON VersionDependencyCreate object.
        """
        output: dict = {
            "dependency_type": self.dependency_type,
        }

        if not isinstance(self.version_id, Empty):
            output["version_id"] = self.version_id
        if not isinstance(self.project_id, Empty):
            output["project_id"] = self.project_id
        if not isinstance(self.file_name, Empty):
            output["file_name"] = self.file_name

        return output


@dataclass
class VersionCreate:
    """
    All data associated with a specific version of a project.

    Documentation: https://docs.modrinth.com/api/operations/getprojectversions/#responses
    """

    name: str | Empty
    version_number: VersionNumber | Empty
    changelog: str | None | Empty
    dependencies: list[VersionDependencyCreate] | Empty
    game_versions: list[GAME_VERSION] | Empty
    version_type: VERSION_TYPE | Empty
    loaders: list[str] | Empty
    featured: bool | Empty
    status: VERSION_STATUS | Empty
    requested_status: REQUESTED_VERSION_STATUS | None | Empty
    project_id: MODRINTH_ID
    file_parts: list[str]
    primary_file: str | Empty

    @classmethod
    def from_json(cls, json_: dict) -> "VersionCreate":
        """
        :param json_: The dictionary containing the same keys expected by `VersionCreate`
        :raise KeyError: If any required values for `VersionCreate` are not defined.
        """
        version_number: VersionNumber | Empty = EMPTY
        if x := json_.get("version_number", EMPTY) != EMPTY:
            version_number = VersionNumber.from_version_number_str(x)
        dependencies: list[VersionDependencyCreate] | Empty = EMPTY
        if x := json_.get("dependencies", EMPTY) != EMPTY:
            dependencies = [VersionDependencyCreate.from_json(d) for d in x]

        return VersionCreate(
            name=json_.get("name", EMPTY),
            version_number=version_number,
            changelog=json_.get("changelog", EMPTY),
            dependencies=dependencies,
            game_versions=json_.get("game_versions", EMPTY),
            version_type=json_.get("version_type", EMPTY),
            loaders=json_.get("loaders", EMPTY),
            featured=json_.get("featured", EMPTY),
            status=json_.get("status", EMPTY),
            requested_status=json_.get("requested_status", EMPTY),
            project_id=json_["project_id"],
            file_parts=json_["file_parts"],
            primary_file=json_.get("primary_file", EMPTY),
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `VersionCreate` object.
        """

        output: dict = {
            "project_id": self.project_id,
            "file_parts": self.file_parts,
        }

        if not isinstance(self.name, Empty):
            output["name"] = self.name
        if not isinstance(self.version_number, Empty):
            output["version_number"] = str(self.version_number)
        if not isinstance(self.changelog, Empty):
            output["changelog"] = self.changelog
        if not isinstance(self.dependencies, Empty):
            output["dependencies"] = [d.to_json() for d in self.dependencies]
        if not isinstance(self.game_versions, Empty):
            output["game_versions"] = self.game_versions
        if not isinstance(self.version_type, Empty):
            output["version_type"] = self.version_type
        if not isinstance(self.loaders, Empty):
            output["loaders"] = self.loaders
        if not isinstance(self.featured, Empty):
            output["featured"] = self.featured
        if not isinstance(self.status, Empty):
            output["status"] = self.status
        if not isinstance(self.requested_status, Empty):
            output["requested_status"] = self.requested_status
        if not isinstance(self.primary_file, Empty):
            output["primary_file"] = self.primary_file

        return output


@dataclass
class SingleHashMapping:
    """
    A pairing of a file hash with the algorithm used.

    This is primary used when modifying a version.

    https://docs.modrinth.com/api/operations/modifyversion/#request
    See primary_file
    """

    algorithm: HASH_ALGORITHM
    hash: HASH

    @classmethod
    def from_json(cls, json_: list[str]) -> "SingleHashMapping":
        """
        :param json_: The list containing the same values expected by `SingleHashMapping`
        :raise KeyError: If any required values for `SingleHashMapping` are not defined.
        """
        try:
            return SingleHashMapping(
                algorithm=cast(HASH_ALGORITHM, json_[0]),
                hash=json_[1],
            )
        except IndexError as index_error:
            raise KeyError(index_error)

    def to_json(self) -> list[str]:
        """
        Convert back into a dictionary representation of a JSON `SingleHashMapping` object.
        """
        return [
            self.algorithm,
            self.hash,
        ]


@dataclass
class FileType:
    """
    Data representing a file to be edited.

    Primarily used when modifying a version.

    Documentation: https://docs.modrinth.com/api/operations/modifyversion/#responses
    See fil_types
    """

    algorithm: HASH_ALGORITHM
    hash: HASH
    file_type: FILE_TYPE | None

    @classmethod
    def from_json(cls, json_: dict) -> "FileType":
        """
        :param json_: The dictionary containing the same keys expected by `FileType`
        :raise KeyError: If any required values for `FileType` are not defined.
        """
        return FileType(
            algorithm=json_["algorithm"],
            hash=json_["hash"],
            file_type=json_["file_type"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `FileType` object.
        """
        return {
            "algorithm": self.algorithm,
            "hash": self.hash,
            "file_type": self.file_type,
        }


@dataclass
class VersionPatch:
    """
    All data necessary for updating a specific version of a project.

    Documentation: https://docs.modrinth.com/api/operations/modifyversion/#responses
    """

    name: str | Empty
    version_number: VersionNumber | Empty
    changelog: str | None | Empty
    dependencies: list[VersionDependency] | Empty
    game_versions: list[GAME_VERSION] | Empty
    version_type: VERSION_TYPE | Empty
    loaders: list[str] | Empty
    featured: bool | Empty
    status: VERSION_STATUS | Empty
    requested_status: REQUESTED_VERSION_STATUS | Empty
    primary_file: SingleHashMapping | Empty
    file_types: list[FileType] | Empty

    @classmethod
    def from_json(cls, json_: dict) -> "VersionPatch":
        """
        :param json_: The dictionary containing the same keys expected by `VersionPatch`
        :raise KeyError: If any required values for `VersionPatch` are not defined.
        """
        version_number: VersionNumber | Empty = EMPTY
        if x := json_.get("version_number", EMPTY) != EMPTY:
            version_number = VersionNumber.from_version_number_str(x)

        dependencies: list[VersionDependency] | Empty = EMPTY
        if x := json_.get("dependencies", EMPTY) != EMPTY:
            dependencies = [VersionDependency.from_json(vd) for vd in x]

        primary_file: SingleHashMapping | Empty = EMPTY
        if x := json_.get("primary_file", EMPTY) != EMPTY:
            primary_file = SingleHashMapping.from_json(x)

        file_types: list[FileType] | Empty = EMPTY
        if x := json_.get("file_types", EMPTY) != EMPTY:
            file_types = [FileType.from_json(f) for f in x]

        return VersionPatch(
            name=json_.get("name", EMPTY),
            version_number=version_number,
            changelog=json_.get("changelog"),
            dependencies=dependencies,
            game_versions=json_.get("game_versions", EMPTY),
            version_type=json_.get("version_type", EMPTY),
            loaders=json_.get("loaders", EMPTY),
            featured=json_.get("featured", EMPTY),
            status=json_.get("status", EMPTY),
            requested_status=json_.get("requested_status", EMPTY),
            primary_file=primary_file,
            file_types=file_types,
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `VersionPatch` object.
        """
        output: dict = {}

        if not isinstance(self.name, Empty):
            output["name"] = self.name
        if not isinstance(self.version_number, Empty):
            output["version_number"] = str(self.version_number)
        if not isinstance(self.changelog, Empty):
            output["changelog"] = self.changelog
        if not isinstance(self.dependencies, Empty):
            output["dependencies"] = [d.to_json() for d in self.dependencies]
        if not isinstance(self.game_versions, Empty):
            output["game_versions"] = self.game_versions
        if not isinstance(self.version_type, Empty):
            output["version_type"] = self.version_type
        if not isinstance(self.loaders, Empty):
            output["loaders"] = self.loaders
        if not isinstance(self.featured, Empty):
            output["featured"] = self.featured
        if not isinstance(self.status, Empty):
            output["status"] = self.status
        if not isinstance(self.requested_status, Empty):
            output["requested_status"] = self.requested_status
        if not isinstance(self.primary_file, Empty):
            output["primary_file"] = self.primary_file.to_json()
        if not isinstance(self.file_types, Empty):
            output["file_types"] = [f.to_json() for f in self.file_types]

        return output


@dataclass
class Payout:
    """
    Data related to a user's payout status.

    This data is only available to user's getting their own data.

    Documentation: https://docs.modrinth.com/api/operations/getuser/#responses
    See payout_data
    """

    balance: float
    payout_wallet: Literal["paypal", "venmo"]
    payout_wallet_type: Literal["email", "phone", "user_handle"]
    payout_address: str

    @classmethod
    def from_json(cls, json_: dict) -> "Payout":
        """
        :param json_: The dictionary containing the same keys expected by `Payout`
        :raise KeyError: If any required values for `Payout` are not defined.
        """
        return Payout(
            balance=json_["balance"],
            payout_wallet=json_["payout_wallet"],
            payout_wallet_type=json_["payout_wallet_type"],
            payout_address=json_["payout_address"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `Payout` object.
        """
        return {
            "balance": self.balance,
            "payout_wallet": self.payout_wallet,
            "payout_wallet_type": self.payout_wallet_type,
            "payout_address": self.payout_address,
        }


@dataclass
class PayoutPatch:
    """
    Data related to a user's payout status when updating that data.

    Documentation: https://docs.modrinth.com/api/operations/modifyuser/#request-body
    See payout_data
    """

    payout_wallet: Literal["paypal", "venmo"] | Empty
    payout_wallet_type: Literal["email", "phone", "user_handle"] | Empty
    payout_address: str | Empty

    @classmethod
    def from_json(cls, json_: dict) -> "PayoutPatch":
        """
        :param json_: The dictionary containing the same keys expected by `PayoutPatch`
        """
        return PayoutPatch(
            payout_wallet=json_.get("payout_wallet", EMPTY),
            payout_wallet_type=json_.get("payout_wallet_type", EMPTY),
            payout_address=json_.get("payout_address", EMPTY),
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `PayoutPatch` object.
        """
        output: dict = {}

        if not isinstance(self.payout_wallet, Empty):
            output["payout_wallet"] = self.payout_wallet
        if not isinstance(self.payout_wallet_type, Empty):
            output["payout_wallet_type"] = self.payout_wallet_type
        if not isinstance(self.payout_address, Empty):
            output["payout_address"] = self.payout_address

        return output


@dataclass
class Badges:
    """
    Any badges applicable to a user. These are currently unused and undisplayed, and as such are subject to change.

    The data is sent as a number bitfield where the 7 smallest bits available.
    This object stores the bits as 7 boolean flags.

    Documentation: https://docs.modrinth.com/api/operations/getuser/#responses
    See badges
    """

    unused: bool
    EARLY_MODPACK_ADOPTER: bool
    EARLY_RESPACK_ADOPTER: bool
    EARLY_PLUGIN_ADOPTER: bool
    ALPHA_TESTER: bool
    CONTRIBUTOR: bool
    TRANSLATOR: bool

    @classmethod
    def from_bitfield(cls, bitfield: int) -> "Badges":
        """
        :param bitfield: The bitfield encoded as an integer.
        """
        return Badges(
            unused=bitfield & 1 == 1,
            EARLY_MODPACK_ADOPTER=bitfield & 2 == 1,
            EARLY_RESPACK_ADOPTER=bitfield & 4 == 1,
            EARLY_PLUGIN_ADOPTER=bitfield & 8 == 1,
            ALPHA_TESTER=bitfield & 16 == 1,
            CONTRIBUTOR=bitfield & 32 == 1,
            TRANSLATOR=bitfield & 64 == 1,
        )

    def to_bitfield(self) -> int:
        """
        Convert the boolean flags back into a bitfield.

        :returns: The reconstructed bitfield encoded as an integer.
        """
        return (
            (self.unused * 1)
            + (self.EARLY_MODPACK_ADOPTER * 2)
            + (self.EARLY_RESPACK_ADOPTER * 4)
            + (self.EARLY_PLUGIN_ADOPTER * 8)
            + (self.ALPHA_TESTER * 16)
            + (self.CONTRIBUTOR * 32)
            + (self.TRANSLATOR * 64)
        )


@dataclass
class User:
    """
    The data associated with a user.

    If the user is authenticated and gets their own data,
    some nullable fields will have values.
    This includes: `email`, `payout_data`, `auth_providers`, `email_verified`, `has_password`, and `has_totp`.
    They are accessed using a different API endpoint.

    Documentation: https://docs.modrinth.com/api/operations/getuser/#responses
    """

    username: str
    name: str | None
    email: str | None
    bio: str
    payout_date: Payout | None
    id: str
    avatar_url: str
    created: datetime
    role: Literal["admin", "moderator", "developer"]
    badges: Badges
    auth_providers: list[str] | None
    email_verified: bool | None
    has_password: bool | None
    has_totp: bool | None
    github_id: None

    @classmethod
    def from_json(cls, json_: dict) -> "User":
        """
        :param json_: The dictionary containing the same keys expected by `User`
        :raise KeyError: If any required values for `User` are not defined.
        """
        payout_date_json: dict | None = json_.get("payout_date")

        return User(
            username=json_["username"],
            name=json_.get("name"),
            email=json_.get("email"),
            bio=json_["bio"],
            payout_date=(
                None if payout_date_json is None else Payout.from_json(payout_date_json)
            ),
            id=json_["id"],
            avatar_url=json_["avatar_url"],
            created=datetime.fromisoformat(json_["created"]),
            role=json_["role"],
            badges=Badges.from_bitfield(json_["badges"]),
            auth_providers=json_.get("auth_providers"),
            email_verified=json_.get("email_verified"),
            has_password=json_.get("has_password"),
            has_totp=json_.get("has_totp"),
            github_id=json_.get("github_id"),
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `User` object.
        """
        return {
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "bio": self.bio,
            "payout_date": self.payout_date,
            "id": self.id,
            "avatar_url": self.avatar_url,
            "created": self.created.strftime(DATE_FORMAT),
            "role": self.role,
            "badges": self.badges.to_bitfield(),
            "auth_providers": self.auth_providers,
            "email_verified": self.email_verified,
            "has_password": self.has_password,
            "has_totp": self.has_totp,
            "github_id": self.github_id,
        }


@dataclass
class PersonalUser:
    """
    The data associated with this user.

    This is different from `User` because some previous null fields will have values.
    This includes: `email`, `payout_data`, `auth_providers`, `email_verified`, `has_password`, and `has_totp`.

    Documentation: https://docs.modrinth.com/api/operations/getuserfromauth/
    """

    username: str
    name: str | None
    email: str | None
    bio: str
    payout_date: Payout | None
    id: str
    avatar_url: str
    created: datetime
    role: Literal["admin", "moderator", "developer"]
    badges: Badges
    auth_providers: list[str]
    email_verified: bool
    has_password: bool
    has_totp: bool
    github_id: None

    @classmethod
    def from_json(cls, json_: dict) -> "PersonalUser":
        """
        :param json_: The dictionary containing the same keys expected by `PersonalUser`
        :raise KeyError: If any required values for `PersonalUser` are not defined.
        """
        payout_date_json: dict | None = json_.get("payout_date")

        return PersonalUser(
            username=json_["username"],
            name=json_.get("name"),
            email=json_.get("email"),
            bio=json_["bio"],
            payout_date=(
                None if payout_date_json is None else Payout.from_json(payout_date_json)
            ),
            id=json_["id"],
            avatar_url=json_["avatar_url"],
            created=datetime.fromisoformat(json_["created"]),
            role=json_["role"],
            badges=Badges.from_bitfield(json_["badges"]),
            auth_providers=json_["auth_providers"],
            email_verified=json_["email_verified"],
            has_password=json_["has_password"],
            has_totp=json_["has_totp"],
            github_id=json_.get("github_id"),
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `PersonalUser` object.
        """
        return {
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "bio": self.bio,
            "payout_date": self.payout_date,
            "id": self.id,
            "avatar_url": self.avatar_url,
            "created": self.created.strftime(DATE_FORMAT),
            "role": self.role,
            "badges": self.badges.to_bitfield(),
            "auth_providers": self.auth_providers,
            "email_verified": self.email_verified,
            "has_password": self.has_password,
            "has_totp": self.has_totp,
            "github_id": self.github_id,
        }

    def to_user(self) -> User:
        return User(
            username=self.username,
            name=self.name,
            email=self.email,
            bio=self.bio,
            payout_date=self.payout_date,
            id=self.id,
            avatar_url=self.avatar_url,
            created=self.created,
            role=self.role,
            badges=self.badges,
            auth_providers=self.auth_providers,
            email_verified=self.email_verified,
            has_password=self.has_password,
            has_totp=self.has_totp,
            github_id=self.github_id,
        )


# TODO: Add notes about EMPTY and None to other objects
@dataclass
class UserPatch:
    """
    The user data that can be edited via a patch request.

    Fields marked as `EMPTY` are not included in the request.
    Fields marked as `None` are marked as `null` in the request.

    Documentation: https://docs.modrinth.com/api/operations/modifyuser/#request-body
    """

    username: str | Empty
    name: str | None | Empty
    email: str | None | Empty
    bio: str | None | Empty
    payout_date: PayoutPatch | Empty

    @classmethod
    def from_json(cls, json_: dict) -> "UserPatch":
        """
        :param json_: The dictionary containing the same keys expected by `UserPatch`
        """
        payout_date_json: dict | Empty = json_.get("payout_date", EMPTY)

        return UserPatch(
            username=json_.get("username", EMPTY),
            name=json_.get("name", EMPTY),
            email=json_.get("email", EMPTY),
            bio=json_.get("bio", EMPTY),
            payout_date=(
                payout_date_json
                if isinstance(payout_date_json, Empty)
                else PayoutPatch.from_json(payout_date_json)
            ),
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `UserPatch` object.
        """
        output: dict = {}

        if not isinstance(self.username, Empty):
            output["username"] = self.username
        if not isinstance(self.name, Empty):
            output["name"] = self.name
        if not isinstance(self.email, Empty):
            output["email"] = self.email
        if not isinstance(self.bio, Empty):
            output["bio"] = self.bio
        if not isinstance(self.payout_date, Empty):
            output["payout_date"] = self.payout_date

        return output


@dataclass
class DonationLink:
    """
    Access for donating to a project.

    Documentation: https://docs.modrinth.com/api/operations/getproject/#responses
    See donation_urls
    """

    id: str
    platform: str
    url: str

    @classmethod
    def from_json(cls, json_: dict) -> "DonationLink":
        """
        :param json_: The dictionary containing the same keys expected by `DonationLink`
        :raise KeyError: If any required values for `DonationLink` are not defined.
        """
        return DonationLink(
            id=json_["id"],
            platform=json_["platform"],
            url=json_["url"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `DonationLink` object.
        """
        return {
            "id": self.id,
            "platform": self.platform,
            "url": self.url,
        }


@dataclass
class Color:
    """
    The RGB color of a project.

    This is usually automatically generated based on the project icon.
    It is sent as an RGB integer.

    Documentation: https://docs.modrinth.com/api/operations/getproject/#responses
    See color
    """

    red: int
    green: int
    blue: int

    @classmethod
    def from_rgb_int(cls, rgb_int: int) -> "Color":
        """
        :param rgb_int: The color stored as the integer concatenation of the bytes red + green + blue.
        """
        return Color(
            red=(rgb_int >> 16) % 256,
            green=(rgb_int >> 8) % 256,
            blue=rgb_int % 256,
        )

    def to_rgb_int(self) -> int:
        """
        :returns: The color stored as the integer concatenation of the bytes red + green + blue.
        """
        return (self.red << 16) + (self.green << 8) + (self.blue)


@dataclass
class ModeratorMessage:
    """
    A message that a moderator has left for a project.

    Documentation: https://docs.modrinth.com/api/operations/getproject/#responses
    See moderator_message
    """

    message: str
    body: str | None

    @classmethod
    def from_json(cls, json_: dict) -> "ModeratorMessage":
        """
        :param json_: The dictionary containing the same keys expected by `ModeratorMessage`
        :raise KeyError: If any required values for `ModeratorMessage` are not defined.
        """
        return ModeratorMessage(
            message=json_["message"],
            body=json_.get("body"),
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `ModeratorMessage` object.
        """
        return {
            "message": self.message,
            "body": self.body,
        }


@dataclass
class License:
    """
    A project license.

    Documentation: https://docs.modrinth.com/api/operations/getproject/#responses
    See license
    """

    id: str
    name: str
    url: str | None

    @classmethod
    def from_json(cls, json_: dict) -> "License":
        """
        :param json_: The dictionary containing the same keys expected by `License`
        :raise KeyError: If any required values for `License` are not defined.
        """
        return License(
            id=json_["id"],
            name=json_["name"],
            url=json_.get("url"),
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `License` object.
        """
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
        }


@dataclass
class GalleryItem:
    """
    An item within a project's gallery.

    Documentation: https://docs.modrinth.com/api/operations/getproject/#responses
    See gallery
    """

    url: str
    featured: bool
    title: str | None
    description: str | None
    created: datetime
    ordering: int

    @classmethod
    def from_json(cls, json_: dict) -> "GalleryItem":
        """
        :param json_: The dictionary containing the same keys expected by `GalleryItem`
        :raise KeyError: If any required values for `GalleryItem` are not defined.
        """
        return GalleryItem(
            url=json_["url"],
            featured=json_["featured"],
            title=json_.get("title"),
            description=json_.get("description"),
            created=datetime.fromisoformat(json_["created"]),
            ordering=json_["ordering"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `GalleryItem` object.
        """
        return {
            "url": self.url,
            "featured": self.featured,
            "title": self.title,
            "description": self.description,
            "created": self.created.strftime(DATE_FORMAT),
            "ordering": self.ordering,
        }


@dataclass
class Project:
    """
    A modrinth project.

    Documentation: https://docs.modrinth.com/api/operations/getproject/#responses
    """

    slug: MODRINTH_TEMP_ID
    title: str
    description: str
    categories: list[str]
    client_side: SUPPORT
    server_side: SUPPORT
    body: str
    status: PROJECT_STATUS
    requested_status: REQUESTED_PROJECT_STATUS | None
    additional_categories: list[str]
    issues_url: str | None
    source_url: str | None
    wiki_url: str | None
    discord_url: str | None
    donation_urls: list[DonationLink]
    project_type: PROJECT_TYPE
    downloads: int
    icon_url: str | None
    color: Color | None
    thread_id: MODRINTH_ID
    monetization_status: Literal["monetized", "demonetized", "force-demonetized"]
    id: MODRINTH_ID
    team: MODRINTH_ID
    body_url: None
    moderator_message: ModeratorMessage
    published: datetime
    updated: datetime
    approved: datetime | None
    queued: datetime | None
    followers: int
    license: License
    versions: list[MODRINTH_ID]
    game_versions: list[GAME_VERSION]
    loaders: list[LOADER]
    gallery: list[GalleryItem]

    @classmethod
    def from_json(cls, json_: dict) -> "Project":
        """
        :param json_: The dictionary containing the same keys expected by `Project`
        :raise KeyError: If any required values for `Project` are not defined.
        """
        color_rgb_int: int | None = json_.get("color")
        approved_json: str | None = json_.get("approved_json")
        queued_json: str | None = json_.get("queued_json")

        return Project(
            slug=json_["slug"],
            title=json_["title"],
            description=json_["description"],
            categories=json_["categories"],
            client_side=json_["client_side"],
            server_side=json_["server_side"],
            body=json_["body"],
            status=json_["status"],
            requested_status=json_.get("requested_status"),
            additional_categories=json_["additional_categories"],
            issues_url=json_.get("issues_url"),
            source_url=json_.get("source_url"),
            wiki_url=json_.get("wiki_url"),
            discord_url=json_.get("discord_url"),
            donation_urls=[DonationLink.from_json(d) for d in json_["donation_urls"]],
            project_type=json_["project_type"],
            downloads=json_["downloads"],
            icon_url=json_.get("icon_url"),
            color=None if color_rgb_int is None else Color.from_rgb_int(color_rgb_int),
            thread_id=json_["thread_id"],
            monetization_status=json_["monetization_status"],
            id=json_["id"],
            team=json_["team"],
            body_url=json_.get("body_url"),
            moderator_message=ModeratorMessage.from_json(json_["moderator_message"]),
            published=datetime.fromisoformat(json_["published"]),
            updated=datetime.fromisoformat(json_["updated"]),
            approved=(
                None if approved_json is None else datetime.fromisoformat(approved_json)
            ),
            queued=None if queued_json is None else datetime.fromisoformat(queued_json),
            followers=json_["followers"],
            license=License.from_json(json_["license"]),
            versions=json_["versions"],
            game_versions=json_["game_versions"],
            loaders=json_["loaders"],
            gallery=[GalleryItem.from_json(g) for g in json_["gallery"]],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `Project` object.
        """
        return {
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "categories": self.categories,
            "client_side": self.client_side,
            "server_side": self.server_side,
            "body": self.body,
            "status": self.status,
            "requested_status": self.requested_status,
            "additional_categories": self.additional_categories,
            "issues_url": self.issues_url,
            "source_url": self.source_url,
            "wiki_url": self.wiki_url,
            "discord_url": self.discord_url,
            "donation_urls": [d.to_json() for d in self.donation_urls],
            "project_type": self.project_type,
            "downloads": self.downloads,
            "icon_url": self.icon_url,
            "color": None if self.color is None else self.color.to_rgb_int(),
            "thread_id": self.thread_id,
            "monetization_status": self.monetization_status,
            "id": self.id,
            "team": self.team,
            "body_url": self.body_url,
            "moderator_message": self.moderator_message.to_json(),
            "published": self.published.strftime(DATE_FORMAT),
            "updated": self.updated.strftime(DATE_FORMAT),
            "approved": (
                None if self.approved is None else self.approved.strftime(DATE_FORMAT)
            ),
            "queued": (
                None if self.queued is None else self.queued.strftime(DATE_FORMAT)
            ),
            "followers": self.followers,
            "license": self.license.to_json(),
            "versions": self.versions,
            "game_versions": self.game_versions,
            "loaders": self.loaders,
            "gallery": [g.to_json() for g in self.gallery],
        }


@dataclass
class ProjectCreate:
    """
    A modrinth project.

    Documentation: https://docs.modrinth.com/api/operations/getproject/#responses
    """

    slug: MODRINTH_TEMP_ID | Empty
    title: str | Empty
    description: str | Empty
    categories: list[str] | Empty
    client_side: SUPPORT | Empty
    server_side: SUPPORT | Empty
    body: str | Empty
    status: PROJECT_STATUS | Empty
    requested_status: REQUESTED_PROJECT_STATUS | None | Empty
    additional_categories: list[str] | Empty
    issues_url: str | None | Empty
    source_url: str | None | Empty
    wiki_url: str | None | Empty
    discord_url: str | None | Empty
    donation_urls: list[DonationLink] | Empty
    license_id: str | Empty
    license_url: str | None | Empty
    project_type: PROJECT_TYPE
    initial_versions: Empty
    is_draft: Literal[True]
    gallery_items: Empty

    @classmethod
    def from_json(cls, json_: dict) -> "ProjectCreate":
        """
        :param json_: The dictionary containing the same keys expected by `ProjectCreate`
        :raise KeyError: If any required values for `ProjectCreate` are not defined.
        """
        donation_urls: list[DonationLink] | Empty = EMPTY
        if x := json_.get("donation_urls", EMPTY) != EMPTY:
            [DonationLink.from_json(d) for d in x]

        return ProjectCreate(
            slug=json_.get("slug", EMPTY),
            title=json_.get("title", EMPTY),
            description=json_.get("description", EMPTY),
            categories=json_.get("categories", EMPTY),
            client_side=json_.get("client_side", EMPTY),
            server_side=json_.get("server_side", EMPTY),
            body=json_.get("body", EMPTY),
            status=json_.get("status", EMPTY),
            requested_status=json_.get("requested_status"),
            additional_categories=json_.get("additional_categories", EMPTY),
            issues_url=json_.get("issues_url"),
            source_url=json_.get("source_url"),
            wiki_url=json_.get("wiki_url"),
            discord_url=json_.get("discord_url"),
            donation_urls=donation_urls,
            license_id=json_.get("license_id", EMPTY),
            license_url=json_.get("license_url", EMPTY),
            project_type=json_["project_type"],
            initial_versions=EMPTY,
            is_draft=True,
            gallery_items=EMPTY,
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `ProjectCreate` object.
        """
        output: dict = {
            "project_type": self.project_type,
        }

        if not isinstance(self.slug, Empty):
            output["slug"] = self.slug
        if not isinstance(self.title, Empty):
            output["title"] = self.title
        if not isinstance(self.description, Empty):
            output["description"] = self.description
        if not isinstance(self.categories, Empty):
            output["categories"] = self.categories
        if not isinstance(self.client_side, Empty):
            output["client_side"] = self.client_side
        if not isinstance(self.server_side, Empty):
            output["server_side"] = self.server_side
        if not isinstance(self.body, Empty):
            output["body"] = self.body
        if not isinstance(self.status, Empty):
            output["status"] = self.status
        if not isinstance(self.requested_status, Empty):
            output["requested_status"] = self.requested_status
        if not isinstance(self.additional_categories, Empty):
            output["additional_categories"] = self.additional_categories
        if not isinstance(self.issues_url, Empty):
            output["issues_url"] = self.issues_url
        if not isinstance(self.source_url, Empty):
            output["source_url"] = self.source_url
        if not isinstance(self.wiki_url, Empty):
            output["wiki_url"] = self.wiki_url
        if not isinstance(self.discord_url, Empty):
            output["discord_url"] = self.discord_url
        if not isinstance(self.donation_urls, Empty):
            output["donation_urls"] = [d.to_json() for d in self.donation_urls]
        if not isinstance(self.license_id, Empty):
            output["license_id"] = self.license_id
        if not isinstance(self.license_url, Empty):
            output["license_url"] = self.license_url
        if not isinstance(self.initial_versions, Empty):
            output["initial_versions"] = self.initial_versions
        if not isinstance(self.is_draft, Empty):
            output["is_draft"] = self.is_draft
        if not isinstance(self.gallery_items, Empty):
            output["gallery_items"] = self.gallery_items

        return output


@dataclass
class ProjectPatch:
    """
    Data to update a Modrinth project.

    Documentation: https://docs.modrinth.com/api/operations/modifyproject/#request-body
    """

    slug: MODRINTH_TEMP_ID | Empty
    title: str | Empty
    description: str | Empty
    categories: list[str] | Empty
    client_side: SUPPORT | Empty
    server_side: SUPPORT | Empty
    body: str | Empty
    status: PROJECT_STATUS | Empty
    requested_status: (
        Literal["approved", "archived", "unlisted", "private", "draft"] | None | Empty
    )
    additional_categories: list[str] | Empty
    issues_url: str | None | Empty
    source_url: str | None | Empty
    wiki_url: str | None | Empty
    discord_url: str | None | Empty
    donation_urls: list[DonationLink] | Empty
    license_id: str | Empty
    license_url: str | None | Empty
    moderation_message: str | None | Empty
    moderation_message_body: str | None | Empty

    @classmethod
    def from_json(cls, json_: dict) -> "ProjectPatch":
        """
        :param json_: The dictionary containing the same keys expected by `ProjectPatch`
        :raise KeyError: If any required values for `ProjectPatch` are not defined.
        """

        return ProjectPatch(
            slug=json_.get("slug", EMPTY),
            title=json_.get("title", EMPTY),
            description=json_.get("description", EMPTY),
            categories=json_.get("categories", EMPTY),
            client_side=json_.get("client_side", EMPTY),
            server_side=json_.get("server_side", EMPTY),
            body=json_.get("body", EMPTY),
            status=json_.get("status", EMPTY),
            requested_status=json_.get("requested_status", EMPTY),
            additional_categories=json_.get("additional_categories", EMPTY),
            issues_url=json_.get("issues_url", EMPTY),
            source_url=json_.get("source_url", EMPTY),
            wiki_url=json_.get("wiki_url", EMPTY),
            discord_url=json_.get("discord_url", EMPTY),
            donation_urls=json_.get("donation_urls", EMPTY),
            license_id=json_.get("license_id", EMPTY),
            license_url=json_.get("license_url", EMPTY),
            moderation_message=json_.get("moderation_message", EMPTY),
            moderation_message_body=json_.get("moderation_message_body", EMPTY),
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `ProjectPatch` object.
        """
        output: dict = {}

        if not isinstance(self.slug, Empty):
            output["slug"] = self.slug
        if not isinstance(self.title, Empty):
            output["title"] = self.title
        if not isinstance(self.description, Empty):
            output["description"] = self.description
        if not isinstance(self.categories, Empty):
            output["categories"] = self.categories
        if not isinstance(self.client_side, Empty):
            output["client_side"] = self.client_side
        if not isinstance(self.server_side, Empty):
            output["server_side"] = self.server_side
        if not isinstance(self.body, Empty):
            output["body"] = self.body
        if not isinstance(self.status, Empty):
            output["status"] = self.status
        if not isinstance(self.requested_status, Empty):
            output["requested_status"] = self.requested_status
        if not isinstance(self.additional_categories, Empty):
            output["additional_categories"] = self.additional_categories
        if not isinstance(self.issues_url, Empty):
            output["issues_url"] = self.issues_url
        if not isinstance(self.source_url, Empty):
            output["source_url"] = self.source_url
        if not isinstance(self.wiki_url, Empty):
            output["wiki_url"] = self.wiki_url
        if not isinstance(self.discord_url, Empty):
            output["discord_url"] = self.discord_url
        if not isinstance(self.donation_urls, Empty):
            output["donation_urls"] = self.donation_urls
        if not isinstance(self.license_id, Empty):
            output["license_id"] = self.license_id
        if not isinstance(self.license_url, Empty):
            output["license_url"] = self.license_url
        if not isinstance(self.moderation_message, Empty):
            output["moderation_message"] = self.moderation_message
        if not isinstance(self.moderation_message_body, Empty):
            output["moderation_message_body"] = self.moderation_message_body

        return output


T = TypeVar("T")


class ProjectPatchesAdjustments[T]:
    """
    Represents the options for modifying multiple projects at the same time.

    This doesn't exactly match the structure of the JSON,
    but it does better represent the relationship between data.
    Specifically, it represents how you can not both set and modify
    an array of data in the same request.

    Documentation: https://docs.modrinth.com/api/operations/patchprojects/
    """

    def __init__(self) -> None:
        """
        Constructor for the option of neither setting nor adjusting an array.
        """
        self.set_items: list[T] | Empty = EMPTY
        self.add_items: list[T] | Empty = EMPTY
        self.remove_items: list[T] | Empty = EMPTY

    @classmethod
    def with_set_items(cls, *, set_items: list[T]) -> "ProjectPatchesAdjustments[T]":
        """
        Constructor for the option of setting an array with specific items.

        :param set_items: The new values to set this field to for all specified projects.
        """
        out = cls()
        out.set_items = set_items
        return out

    @classmethod
    def with_adjust_items(
        cls,
        *,
        add_items: list[T],
        remove_items: list[T],
    ) -> "ProjectPatchesAdjustments[T]":
        """
        Constructor for the option of adjusting an array with specific items.

        :param add_items: The values to add to this field to for all specified projects.
        :param remove_items: The values to remove from this field to for all specified projects.
        """
        out = cls()
        out.add_items = add_items
        out.remove_items = remove_items
        return out


@dataclass
class ProjectPatches:
    """
    Data to update multiple Modrinth projects.

    Documentation: https://docs.modrinth.com/api/operations/modifyproject/#request-body
    """

    categories: ProjectPatchesAdjustments[str]
    additional_categories: ProjectPatchesAdjustments[str]
    donation_urls: ProjectPatchesAdjustments[DonationLink]
    issues_url: str | None | Empty
    source_url: str | None | Empty
    wiki_url: str | None | Empty
    discord_url: str | None | Empty

    @classmethod
    def from_json(cls, json_: dict) -> "ProjectPatches":
        """
        :param json_: The dictionary containing the same keys expected by `ProjectPatches`
        :raise ValueError: If one of categories, additional_categories, or donation_urls is both set and modified.
        """

        # Do error checking categories
        categories: ProjectPatchesAdjustments[str]
        if "categories" in json_ and (
            "add_categories" in json_ or "remove_categories" in json_
        ):
            raise ValueError(
                "Cannot simultaneously set `categories` and adjust (with `add_categories` or `remove_categories`)"
            )

        # Do error checking additional_categories
        additional_categories: ProjectPatchesAdjustments[str]
        if "additional_categories" in json_ and (
            "add_additional_categories" in json_
            or "remove_additional_categories" in json_
        ):
            raise ValueError(
                "Cannot simultaneously set `additional_categories` and adjust (with `add_additional_categories` or `remove_additional_categories`)"
            )

        # Do error checking donation_urls
        donation_urls: ProjectPatchesAdjustments[DonationLink]
        if "donation_urls" in json_ and (
            "add_donation_urls" in json_ or "remove_donation_urls" in json_
        ):
            raise ValueError(
                "Cannot simultaneously set `donation_urls` and adjust (with `add_donation_urls` or `remove_donation_urls`)"
            )

        # Setup categories
        if "categories" in json_:
            categories = ProjectPatchesAdjustments[str].with_set_items(
                set_items=json_.get("categories", [])
            )
        elif "add_categories" in json_ or "remove_categories" in json_:
            categories = ProjectPatchesAdjustments[str].with_adjust_items(
                add_items=json_.get("add_categories", []),
                remove_items=json_.get("remove_categories", []),
            )
        else:
            categories = ProjectPatchesAdjustments[str]()

        # Setup additional_categories
        if "additional_categories" in json_:
            additional_categories = ProjectPatchesAdjustments[str].with_set_items(
                set_items=json_.get("additional_categories", [])
            )
        elif (
            "add_additional_categories" in json_
            or "remove_additional_categories" in json_
        ):
            additional_categories = ProjectPatchesAdjustments[str].with_adjust_items(
                add_items=json_.get("add_additional_categories", []),
                remove_items=json_.get("remove_additional_categories", []),
            )
        else:
            additional_categories = ProjectPatchesAdjustments[str]()

        # Setup donation_urls
        if "donation_urls" in json_:
            donation_urls = ProjectPatchesAdjustments[DonationLink].with_set_items(
                set_items=[
                    DonationLink.from_json(d) for d in json_.get("donation_urls", [])
                ]
            )
        elif "add_donation_urls" in json_ or "remove_donation_urls" in json_:
            donation_urls = ProjectPatchesAdjustments[DonationLink].with_adjust_items(
                add_items=[
                    DonationLink.from_json(d)
                    for d in json_.get("add_donation_urls", [])
                ],
                remove_items=[
                    DonationLink.from_json(d)
                    for d in json_.get("remove_donation_urls", [])
                ],
            )
        else:
            donation_urls = ProjectPatchesAdjustments[DonationLink]()

        return ProjectPatches(
            categories=categories,
            additional_categories=additional_categories,
            donation_urls=donation_urls,
            issues_url=json_.get("issues_url", Empty),
            source_url=json_.get("source_url", Empty),
            wiki_url=json_.get("wiki_url", Empty),
            discord_url=json_.get("discord_url", Empty),
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `ProjectPatches` object.
        """
        output: dict = {}

        if not isinstance(self.categories.set_items, Empty):
            output["categories"] = self.categories.set_items
        if not isinstance(self.categories.add_items, Empty):
            output["add_categories"] = self.categories.add_items
        if not isinstance(self.categories.remove_items, Empty):
            output["remove_categories"] = self.categories.remove_items
        if not isinstance(self.additional_categories.set_items, Empty):
            output["additional_categories"] = self.additional_categories.set_items
        if not isinstance(self.additional_categories.add_items, Empty):
            output["add_additional_categories"] = self.additional_categories.add_items
        if not isinstance(self.additional_categories.remove_items, Empty):
            output["remove_additional_categories"] = (
                self.additional_categories.remove_items
            )
        if not isinstance(self.donation_urls.set_items, Empty):
            output["donation_urls"] = [
                d.to_json() for d in self.donation_urls.set_items
            ]
        if not isinstance(self.donation_urls.add_items, Empty):
            output["add_donation_urls"] = [
                d.to_json() for d in self.donation_urls.add_items
            ]
        if not isinstance(self.donation_urls.remove_items, Empty):
            output["remove_donation_urls"] = [
                d.to_json() for d in self.donation_urls.remove_items
            ]

        if not isinstance(self.issues_url, Empty):
            output["issues_url"] = self.issues_url
        if not isinstance(self.source_url, Empty):
            output["source_url"] = self.source_url
        if not isinstance(self.wiki_url, Empty):
            output["wiki_url"] = self.wiki_url
        if not isinstance(self.discord_url, Empty):
            output["discord_url"] = self.discord_url

        return output


@dataclass
class ProjectDependencies:
    """
    All projects and versions a project depends on.

    Documentation: https://docs.modrinth.com/api/operations/getdependencies/#responses
    """

    projects: list[Project]
    versions: list[Version]

    @classmethod
    def from_json(cls, json_: dict) -> "ProjectDependencies":
        """
        :param json_: The dictionary containing the same keys expected by `ProjectDependencies`
        :raise KeyError: If any required values for `ProjectDependencies` are not defined.
        """
        return ProjectDependencies(
            projects=[Project.from_json(p) for p in json_["projects"]],
            versions=[Version.from_json(v) for v in json_["versions"]],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `ProjectDependencies` object.
        """
        return {
            "projects": [p.to_json() for p in self.projects],
            "versions": [v.to_json() for v in self.versions],
        }


@dataclass
class Permissions:
    """
    Any permissions a user has.

    The data is sent as a number bitfield with 10 bits.
    This data is only available with authorization.

    Documentation: https://docs.modrinth.com/api/operations/getprojectteammembers/
    See permissions
    """

    UPLOAD_VERSION: bool
    DELETE_VERSIONS: bool
    EDIT_DETAILS: bool
    EDIT_BODY: bool
    MANAGE_INVITES: bool
    REMOVE_MEMBER: bool
    EDIT_MEMBER: bool
    DELETE_PROJECT: bool
    VIEW_ANALYTICS: bool
    VIEW_PAYOUTS: bool

    @classmethod
    def from_bitfield(cls, bitfield: int) -> "Permissions":
        """
        :param bitfield: The bitfield encoded as an integer.
        """
        return Permissions(
            UPLOAD_VERSION=bitfield & 1 == 1,
            DELETE_VERSIONS=bitfield & 2 == 1,
            EDIT_DETAILS=bitfield & 4 == 1,
            EDIT_BODY=bitfield & 8 == 1,
            MANAGE_INVITES=bitfield & 16 == 1,
            REMOVE_MEMBER=bitfield & 32 == 1,
            EDIT_MEMBER=bitfield & 64 == 1,
            DELETE_PROJECT=bitfield & 128 == 1,
            VIEW_ANALYTICS=bitfield & 256 == 1,
            VIEW_PAYOUTS=bitfield & 512 == 1,
        )

    def to_bitfield(self) -> int:
        """
        Convert the boolean flags back into a bitfield.

        :returns: The reconstructed bitfield encoded as an integer.
        """
        return (
            self.UPLOAD_VERSION
            + (self.DELETE_VERSIONS * 2)
            + (self.EDIT_DETAILS * 4)
            + (self.EDIT_BODY * 8)
            + (self.MANAGE_INVITES * 16)
            + (self.REMOVE_MEMBER * 32)
            + (self.EDIT_MEMBER * 64)
            + (self.DELETE_PROJECT * 128)
            + (self.VIEW_ANALYTICS * 256)
            + (self.VIEW_PAYOUTS * 512)
        )


@dataclass
class TeamMember:
    """
    Team information about a user.

    Documentation: https://docs.modrinth.com/api/operations/getprojectteammembers/
    """

    team_id: MODRINTH_ID
    user: User
    role: str
    permissions: Permissions | None
    accepted: bool | None
    payouts_split: int
    ordering: int

    @classmethod
    def from_json(cls, json_: dict) -> "TeamMember":
        """
        :param json_: The dictionary containing the same keys expected by `TeamMember`
        :raise KeyError: If any required values for `TeamMember` are not defined.
        """
        permissions = json_.get("permissions")

        return TeamMember(
            team_id=json_["team_id"],
            user=json_["user"],
            role=json_["role"],
            permissions=(
                None if permissions is None else Permissions.from_bitfield(permissions)
            ),
            accepted=json_.get("accepted"),
            payouts_split=json_["payouts_split"],
            ordering=json_["ordering"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `TeamMember` object.
        """
        return {
            "team_id": self.team_id,
            "user": self.user,
            "role": self.role,
            "permissions": (
                None if self.permissions is None else self.permissions.to_bitfield()
            ),
            "accepted": self.accepted,
            "payouts_split": self.payouts_split,
            "ordering": self.ordering,
        }


@dataclass
class Category:
    """
    The information about a category, including its icons and project types.

    Documentation: https://docs.modrinth.com/api/operations/categorylist/
    """

    icon: SVG
    name: str
    project_type: PROJECT_TYPE
    header: str

    @classmethod
    def from_json(cls, json_: dict) -> "Category":
        """
        :param json_: The dictionary containing the same keys expected by `Category`
        :raise KeyError: If any required values for `Category` are not defined.
        """
        permissions = json_.get("permissions")

        return Category(
            icon=json_["icon"],
            name=json_["name"],
            project_type=json_["project_type"],
            header=json_["header"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `Category` object.
        """
        return {
            "icon": self.icon,
            "name": self.name,
            "project_type": self.project_type,
            "header": self.header,
        }


@dataclass
class Loader:
    """
    The information about a loader, including its icons and project types.

    Documentation: https://docs.modrinth.com/api/operations/loaderlist/
    """

    icon: SVG
    name: str
    project_type: PROJECT_TYPE
    header: str

    @classmethod
    def from_json(cls, json_: dict) -> "Loader":
        """
        :param json_: The dictionary containing the same keys expected by `Loader`
        :raise KeyError: If any required values for `Loader` are not defined.
        """
        permissions = json_.get("permissions")

        return Loader(
            icon=json_["icon"],
            name=json_["name"],
            project_type=json_["project_type"],
            header=json_["header"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `Loader` object.
        """
        return {
            "icon": self.icon,
            "name": self.name,
            "project_type": self.project_type,
            "header": self.header,
        }


@dataclass
class GameVersion:
    """
    The information about a game version.

    Documentation: https://docs.modrinth.com/api/operations/versionlist/
    """

    version: GAME_VERSION
    version_type: Literal["release", "snapshot", "alpha", "beta"]
    date: datetime
    major: bool

    @classmethod
    def from_json(cls, json_: dict) -> "GameVersion":
        """
        :param json_: The dictionary containing the same keys expected by `GameVersion`
        :raise KeyError: If any required values for `GameVersion` are not defined.
        """
        return GameVersion(
            version=json_["version"],
            version_type=json_["version_type"],
            date=datetime.fromisoformat(json_["date"]),
            major=json_["major"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `GameVersion` object.
        """
        return {
            "version": self.version,
            "version_type": self.version_type,
            "date": self.date.strftime(DATE_FORMAT),
            "major": self.major,
        }


@dataclass
class DeprecatedLicense:
    """
    The information about a game version.

    The endpoint which uses this object is deprecated.

    Documentation: https://docs.modrinth.com/api/operations/versionlist/
    """

    short: str
    name: str

    @classmethod
    def from_json(cls, json_: dict) -> "DeprecatedLicense":
        """
        :param json_: The dictionary containing the same keys expected by `DeprecatedLicense`
        :raise KeyError: If any required values for `DeprecatedLicense` are not defined.
        """
        return DeprecatedLicense(
            short=json_["short"],
            name=json_["name"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `DeprecatedLicense` object.
        """
        return {
            "short": self.short,
            "name": self.name,
        }


@dataclass
class DonationPlatform:
    """
    The information about a game version.

    Documentation: https://docs.modrinth.com/api/operations/donationplatformlist/
    """

    short: str
    name: str

    @classmethod
    def from_json(cls, json_: dict) -> "DonationPlatform":
        """
        :param json_: The dictionary containing the same keys expected by `DonationPlatform`
        :raise KeyError: If any required values for `DonationPlatform` are not defined.
        """
        return DonationPlatform(
            short=json_["short"],
            name=json_["name"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `DonationPlatform` object.
        """
        return {
            "short": self.short,
            "name": self.name,
        }


@dataclass
class ForgeUpdates:
    """
    The information used by Forge to notify users of new versions.

    Documentation: https://docs.modrinth.com/api/operations/forgeupdates/
    """

    homepage: str
    promos: dict[str, str]
    """
    The available and most recent mod versions for each game version.

    Follows the format:
    * {game_version}-recommended: str
    * {game_version}-latest: str

    This means a mod with support for 3 game versions will have 6 items in the list.
    """

    @classmethod
    def from_json(cls, json_: dict) -> "ForgeUpdates":
        """
        :param json_: The dictionary containing the same keys expected by `ForgeUpdates`
        :raise KeyError: If any required values for `ForgeUpdates` are not defined.
        """
        return ForgeUpdates(
            homepage=json_["homepage"],
            promos=json_["promos"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `ForgeUpdates` object.
        """
        return {
            "homepage": self.homepage,
            "promos": self.promos,
        }


@dataclass
class ModrinthStatistics:
    """
    The information about a game version.

    Documentation: https://docs.modrinth.com/api/operations/statistics/
    """

    projects: int
    versions: int
    files: int
    authors: int

    @classmethod
    def from_json(cls, json_: dict) -> "ModrinthStatistics":
        """
        :param json_: The dictionary containing the same keys expected by `ModrinthStatistics`
        :raise KeyError: If any required values for `ModrinthStatistics` are not defined.
        """
        return ModrinthStatistics(
            projects=json_["projects"],
            versions=json_["versions"],
            files=json_["files"],
            authors=json_["authors"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `ModrinthStatistics` object.
        """
        return {
            "projects": self.projects,
            "versions": self.versions,
            "files": self.files,
            "authors": self.authors,
        }


@dataclass
class PayoutEvent:
    """
    Information about a user's previous payout.

    Documentation: https://docs.modrinth.com/api/operations/getpayouthistory/
    See payouts
    """

    created: datetime
    amount: int
    status: str

    @classmethod
    def from_json(cls, json_: dict) -> "PayoutEvent":
        """
        :param json_: The dictionary containing the same keys expected by `PayoutEvent`
        :raise KeyError: If any required values for `PayoutEvent` are not defined.
        """
        return PayoutEvent(
            created=datetime.fromisoformat(json_["created"]),
            amount=json_["amount"],
            status=json_["status"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `PayoutEvent` object.
        """
        return {
            "created": self.created.strftime(DATE_FORMAT),
            "amount": self.amount,
            "status": self.status,
        }


@dataclass
class PayoutHistory:
    """
    Information about a user's previous payouts.

    Documentation: https://docs.modrinth.com/api/operations/getpayouthistory/
    """

    all_time: str
    last_month: str
    payouts: list[PayoutEvent]

    @classmethod
    def from_json(cls, json_: dict) -> "PayoutHistory":
        """
        :param json_: The dictionary containing the same keys expected by `PayoutHistory`
        :raise KeyError: If any required values for `PayoutHistory` are not defined.
        """
        return PayoutHistory(
            all_time=json_["all_time"],
            last_month=json_["last_month"],
            payouts=[PayoutEvent.from_json(p) for p in json_["payouts"]],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `PayoutHistory` object.
        """
        return {
            "all_time": self.all_time,
            "last_month": self.last_month,
            "payouts": [p.to_json() for p in self.payouts],
        }


@dataclass
class ActionRoute:
    """
    The api endpoint necessary to perform the action.

    Documentation: https://docs.modrinth.com/api/operations/getusernotifications/#response
    See actions/action_route
    """

    http_method: str
    path: str

    @classmethod
    def from_json(cls, json_: list[str]) -> "ActionRoute":
        """
        :param json_: The dictionary containing the same keys expected by `ActionRoute`
        :raise KeyError: If any required values for `ActionRoute` are not defined.
        """
        try:
            return ActionRoute(
                http_method=json_[0],
                path=json_[1],
            )
        except IndexError as index_error:
            raise KeyError(index_error)

    def to_json(self) -> list[str]:
        """
        Convert back into a dictionary representation of a JSON `ActionRoute` object.
        """
        return [
            self.http_method,
            self.path,
        ]


@dataclass
class NotificationAction:
    """
    Actions that can be performed based on a notification.

    Documentation: https://docs.modrinth.com/api/operations/getusernotifications/#response
    See actions
    """

    title: str
    action_route: list[ActionRoute]

    @classmethod
    def from_json(cls, json_: dict) -> "NotificationAction":
        """
        :param json_: The dictionary containing the same keys expected by `NotificationAction`
        :raise KeyError: If any required values for `NotificationAction` are not defined.
        """
        return NotificationAction(
            title=json_["title"],
            action_route=[ActionRoute.from_json(r) for r in json_["action_route"]],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `NotificationAction` object.
        """
        return {
            "title": self.title,
            "action_route": [r.to_json() for r in self.action_route],
        }


@dataclass
class Notification:
    """
    An individual user notification.

    Documentation: https://docs.modrinth.com/api/operations/getusernotifications/
    """

    id: MODRINTH_ID  # TODO: is this a modrinth ID or a different kind of ID?
    user_id: MODRINTH_ID
    type: (
        Literal["project_update", "team_invite", "status_change", "moderator_message"]
        | None
    )
    title: str
    text: str
    link: str
    read: bool
    created: datetime
    actions: list[NotificationAction]

    @classmethod
    def from_json(cls, json_: dict) -> "Notification":
        """
        :param json_: The dictionary containing the same keys expected by `Notification`
        :raise KeyError: If any required values for `Notification` are not defined.
        """
        return Notification(
            id=json_["id"],
            user_id=json_["user_id"],
            type=json_.get("type", None),
            title=json_["title"],
            text=json_["text"],
            link=json_["link"],
            read=json_["read"],
            created=datetime.fromisoformat(json_["created"]),
            actions=[NotificationAction.from_json(a) for a in json_["actions"]],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `Notification` object.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "title": self.title,
            "text": self.text,
            "link": self.link,
            "read": self.read,
            "created": self.created.strftime(DATE_FORMAT),
            "actions": [a.to_json() for a in self.actions],
        }


@dataclass
class Report:
    """
    An individual report accessible to the user.

    Documentation: https://docs.modrinth.com/api/operations/getopenreports/
    """

    report_type: str
    item_id: MODRINTH_ID
    item_type: Literal["project", "user", "version"]
    body: str
    id: MODRINTH_ID
    reporter: MODRINTH_ID
    created: datetime
    closed: bool
    thread_id: MODRINTH_ID

    @classmethod
    def from_json(cls, json_: dict) -> "Report":
        """
        :param json_: The dictionary containing the same keys expected by `Report`
        :raise KeyError: If any required values for `Report` are not defined.
        """
        return Report(
            report_type=json_["report_type"],
            item_id=json_["item_id"],
            item_type=json_["item_type"],
            body=json_["body"],
            id=json_["id"],
            reporter=json_["reporter"],
            created=datetime.fromisoformat(json_["created"]),
            closed=json_["closed"],
            thread_id=json_["thread_id"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `Report` object.
        """
        return {
            "report_type": self.report_type,
            "item_id": self.item_id,
            "item_type": self.item_type,
            "body": self.body,
            "id": self.id,
            "reporter": self.reporter,
            "created": self.created.strftime(DATE_FORMAT),
            "closed": self.closed,
            "thread_id": self.thread_id,
        }


@dataclass
class MessageBody:
    """
    An individual message as part of a thread.

    Documentation: https://docs.modrinth.com/api/operations/getthread/#response
    See messages
    """

    type: Literal["status_change", "text", "thread_closure", "deleted"]

    @classmethod
    def from_json(cls, json_: dict) -> "MessageBody":
        """
        :param json_: The dictionary containing the same keys expected by `MessageBody`
        :raise KeyError: If any required values for `MessageBody` are not defined.
        """
        return MessageBody(
            type=json_["type"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `MessageBody` object.
        """
        return {
            "type": self.type,
        }


@dataclass
class MessageTextBody(MessageBody):
    """
    An individual text message as part of a thread.

    Documentation: https://docs.modrinth.com/api/operations/getthread/#response
    See messages
    """

    body: str
    private: bool
    replying_to: MODRINTH_ID | None

    @classmethod
    def from_json(cls, json_: dict) -> "MessageTextBody":
        """
        :param json_: The dictionary containing the same keys expected by `MessageTextBody`
        :raise KeyError: If any required values for `MessageTextBody` are not defined.
        """
        return MessageTextBody(
            type=json_["type"],
            body=json_["body"],
            private=json_["private"],
            replying_to=json_["replying_to"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `MessageTextBody` object.
        """
        return {
            "type": self.type,
            "body": self.body,
            "private": self.private,
            "replying_to": self.replying_to,
        }


@dataclass
class MessageStatusChangeBody(MessageBody):
    """
    An individual text message as part of a thread.

    Documentation: https://docs.modrinth.com/api/operations/getthread/#response
    See messages
    """

    old_status: PROJECT_STATUS
    new_status: PROJECT_STATUS

    @classmethod
    def from_json(cls, json_: dict) -> "MessageStatusChangeBody":
        """
        :param json_: The dictionary containing the same keys expected by `MessageStatusChangeBody`
        :raise KeyError: If any required values for `MessageStatusChangeBody` are not defined.
        """
        return MessageStatusChangeBody(
            type=json_["type"],
            old_status=json_["old_status"],
            new_status=json_["new_status"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `MessageStatusChangeBody` object.
        """
        return {
            "type": self.type,
            "old_status": self.old_status,
            "new_status": self.new_status,
        }


@dataclass
class Message:
    """
    An individual message as part of a thread.

    Documentation: https://docs.modrinth.com/api/operations/getthread/#response
    See messages
    """

    id: MODRINTH_ID
    author_id: MODRINTH_ID | None
    body: MessageBody
    created: datetime

    @classmethod
    def from_json(cls, json_: dict) -> "Message":
        """
        :param json_: The dictionary containing the same keys expected by `Message`
        :raise KeyError: If any required values for `Message` are not defined.
        """
        body: MessageBody
        body_json: dict = json_["body"]
        match body_json["type"]:
            case "text":
                body = MessageTextBody.from_json(body_json)
            case "status_change":
                body = MessageStatusChangeBody.from_json(body_json)
            case _:
                body = MessageBody.from_json(body_json)

        return Message(
            id=json_["id"],
            author_id=json_["author_id"],
            body=body,
            created=datetime.fromisoformat(json_["created"]),
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `Message` object.
        """
        return {
            "id": self.id,
            "author_id": self.author_id,
            "body": self.body.to_json(),
            "created": self.created.strftime(DATE_FORMAT),
        }


@dataclass
class Thread:
    """
    An individual thread available to the user.

    Documentation: https://docs.modrinth.com/api/operations/getthread/
    """

    id: MODRINTH_ID
    type: Literal["project", "report", "direct_message"]
    project_id: MODRINTH_ID | None
    report_id: MODRINTH_ID | None
    messages: list[Message]
    members: list[User]

    @classmethod
    def from_json(cls, json_: dict) -> "Thread":
        """
        :param json_: The dictionary containing the same keys expected by `Thread`
        :raise KeyError: If any required values for `Thread` are not defined.
        """
        return Thread(
            id=json_["id"],
            type=json_["type"],
            project_id=json_["project_id"],
            report_id=json_["report_id"],
            messages=[Message.from_json(m) for m in json_["messages"]],
            members=[User.from_json(m) for m in json_["members"]],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `Thread` object.
        """
        return {
            "id": self.id,
            "type": self.type,
            "project_id": self.project_id,
            "report_id": self.report_id,
            "messages": [m.to_json() for m in self.messages],
            "members": [m.to_json() for m in self.members],
        }


@dataclass
class SearchResult:
    """
    Results from completing a project search.

    Documentation: https://docs.modrinth.com/api/operations/searchprojects/
    """

    hits: list[Project]
    offset: int
    limit: int
    total_hits: int

    @classmethod
    def from_json(cls, json_: dict) -> "SearchResult":
        """
        :param json_: The dictionary containing the same keys expected by `SearchResult`
        :raise KeyError: If any required values for `SearchResult` are not defined.
        """
        return SearchResult(
            hits=[Project.from_json(p) for p in json_["hits"]],
            offset=json_["offset"],
            limit=json_["limit"],
            total_hits=json_["total_hits"],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `SearchResult` object.
        """
        return {
            "hits": [p.to_json() for p in self.hits],
            "offset": self.offset,
            "limit": self.limit,
            "total_hits": self.total_hits,
        }


NON_COMPARABLE = Literal[":", "=", "!="]


@dataclass
class Facet:
    operation: Literal[":", "=", "!=", ">=", ">", "<=", "<"]
    value: Any
    type: Literal[
        "project_type",
        "categories",
        "versions",
        "client_side",
        "server_side",
        "open_source",
        "title",
        "author",
        "follows",
        "project_id",
        "license",
        "downloads",
        "color",
        "created_timestamp",
        "modified_timestamp",
    ]

    def __repr__(self) -> str:
        return (
            f"Facet(operation={self.operation}, value={self.value}, type={self.type})"
        )

    def __str__(self) -> str:
        return f"{self.type}{self.operation}{str(self.value)}"


@dataclass
class ProjectTypeFacet(Facet):
    operation: NON_COMPARABLE
    value: PROJECT_TYPE
    type: Literal["project_type"] = "project_type"


@dataclass
class CategoryFacet(Facet):
    operation: NON_COMPARABLE
    value: Literal[
        "Adventure",
        "Cursed",
        "Decoration",
        "Economy",
        "Equipment",
        "Food",
        "Game Mechanics",
        "Library",
        "Magic",
        "Management",
        "Minigame",
        "Mobs",
        "Optimization",
        "Social",
        "Storage",
        "Technology",
        "Transportation",
        "Utility",
        "World Generation",
    ]
    type: Literal["categories"] = "categories"


@dataclass
class VersionFacet(Facet):
    value: GAME_VERSION
    type: Literal["versions"] = "versions"


@dataclass
class ClientSideFacet(Facet):
    operation: NON_COMPARABLE
    value: SUPPORT
    type: Literal["client_side"] = "client_side"


@dataclass
class ServerSideFacet(Facet):
    operation: NON_COMPARABLE
    value: SUPPORT
    type: Literal["server_side"] = "server_side"


@dataclass
class OpenSourceFacet(Facet):
    operation: NON_COMPARABLE
    value: bool
    type: Literal["open_source"] = "open_source"


@dataclass
class TitleFacet(Facet):
    operation: NON_COMPARABLE
    value: str
    type: Literal["title"] = "title"


@dataclass
class AuthorFacet(Facet):
    operation: NON_COMPARABLE
    value: str
    type: Literal["author"] = "author"


@dataclass
class FollowsFacet(Facet):
    value: int
    type: Literal["follows"] = "follows"


@dataclass
class ProjectIdFacet(Facet):
    operation: NON_COMPARABLE
    value: MODRINTH_ID
    type: Literal["project_id"] = "project_id"


@dataclass
class LicenseFacet(Facet):
    operation: NON_COMPARABLE
    value: str
    type: Literal["license"] = "license"


@dataclass
class DownloadsFacet(Facet):
    value: int
    type: Literal["downloads"] = "downloads"


@dataclass
class ColorFacet(Facet):
    value: Color
    type: Literal["color"] = "color"


@dataclass
class CreatedTimestampFacet(Facet):
    value: datetime
    type: Literal["created_timestamp"] = "created_timestamp"


@dataclass
class ModifiedTimestampFacet(Facet):
    value: datetime
    type: Literal["modified_timestamp"] = "modified_timestamp"


_AnyFacetsTuple: TypeAlias = tuple[Facet | "AnyFacets", ...]


class AllFacets:
    """
    Search filters that must all be true.

    Documentation: https://docs.modrinth.com/api/operations/searchprojects/#query-parameters
    See facets
    """

    any_facets: _AnyFacetsTuple

    def __init__(self, any_facet_groups: Iterable[Facet | "AnyFacets"]) -> None:
        self.any_facets = tuple(any_facet_groups)

    def to_json(self) -> list:
        return [(x if isinstance(x, Facet) else x.to_json()) for x in self.any_facets]


class AnyFacets:
    """
    Search filters where at least one filter must be true.

    Documentation: https://docs.modrinth.com/api/operations/searchprojects/#query-parameters
    See facets
    """

    all_facets: tuple[AllFacets, ...]

    def __init__(self, facets: Iterable[AllFacets]) -> None:
        self.all_facets = tuple(facets)

    def to_json(self) -> list:
        return [x.to_json() for x in self.all_facets]
