from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from modrinth.types import (
    GAME_VERSION,
    LOADER,
    MODRINTH_ID,
    MODRINTH_TEMP_ID,
    SHA1_HASH,
    SHA512_HASH,
    SVG,
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
    file_type: Literal[None, "required-resource-pack", "optional-resource-pack"]

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
    version_type: Literal["release", "beta", "alpha"]
    loaders: list[str]
    featured: bool
    status: Literal["listed", "archived", "draft", "unlisted", "scheduled", "unknown"]
    requested_status: Literal["listed", "archived", "draft", "unlisted"]
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
            requested_status=json_["requested_status"],
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
    client_side: Literal["required", "optional", "unsupported", "unknown"]
    server_side: Literal["required", "optional", "unsupported", "unknown"]
    body: str
    status: Literal[
        "approved",
        "archived",
        "rejected",
        "draft",
        "unlisted",
        "processing",
        "withheld",
        "scheduled",
        "private",
        "unknown",
    ]
    requested_status: Literal[
        None, "approved", "archived", "unlisted", "private", "draft"
    ]
    additional_categories: list[str]
    issues_url: str | None
    source_url: str | None
    wiki_url: str | None
    discord_url: str | None
    donation_urls: list[DonationLink]
    project_type: Literal["mod", "modpack", "resourcepack", "shader"]
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
    project_type: str
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
    project_type: str
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
            projects=json_['projects'],
            versions=json_['versions'],
            files=json_['files'],
            authors=json_['authors'],
        )

    def to_json(self) -> dict:
        """
        Convert back into a dictionary representation of a JSON `ModrinthStatistics` object.
        """
        return {
            'projects': self.projects,
            'versions': self.versions,
            'files': self.files,
            'authors': self.authors,
        }
