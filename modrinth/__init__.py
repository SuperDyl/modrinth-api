import json
from typing import Any, Iterable, Literal
from warnings import deprecated

import requests

from modrinth.types import GAME_VERSION, HASH, LOADER, MODRINTH_ID, MODRINTH_TEMP_ID
from modrinth.model import (
    Category,
    DeprecatedLicense,
    DonationPlatform,
    ForgeUpdates,
    GameVersion,
    License,
    Loader,
    ModrinthStatistics,
    Project,
    ProjectDependencies,
    TeamMember,
    User,
    Version,
    VersionNumber,
)

class ModrinthApi:
    """
    Used to make requests to Modrinth's API.

    This is a very incomplete definition of v2 of Modrinth's API.
    """

    def __init__(
        self,
        *,
        user_agent: str,
        api_url: str = "https://api.modrinth.com/v2",
    ):
        """
        :param user_agent: The owner of the app making the API requests. See https://docs.modrinth.com/api/#user-agents
        :param api_url: Allows setting a different API endpoint.
        """
        self.api_url = api_url
        self.user_agent = user_agent

    def __repr__(self) -> str:
        return f"ModrinthApi(api_url='{self.api_url}', user_agent='{self.user_agent}')"

    def get_project(self, project_id: MODRINTH_ID | MODRINTH_TEMP_ID) -> Project:
        """
        Gets all data for a project.

        Documentation: https://docs.modrinth.com/api/operations/getprojectversions/

        :param project_id: The ID or slug of the project.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/project/{project_id}",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return Project.from_json(response.json())

    def get_projects(
        self, project_ids: Iterable[MODRINTH_ID | MODRINTH_TEMP_ID]
    ) -> list[Project]:
        """
        Gets all data for multiple projects

        Documentation: https://docs.modrinth.com/api/operations/getprojects/

        :param project_ids: A list of IDs and/or slugs of the projects.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/projects",
            headers={"User-Agent": self.user_agent},
            params={"ids": json.dumps(tuple(project_ids))},
        )
        response.raise_for_status()

        return [Project.from_json(p) for p in response.json()]

    def get_random_projects(self, count: int) -> list[Project]:
        """
        Gets all versions for the specified project.

        Documentation: https://docs.modrinth.com/api/operations/randomprojects/

        :param count: The number of projects to return. Must be in the range 0..100 inclusive.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/projects_random",
            headers={"User-Agent": self.user_agent},
            params={"count": count},
        )
        response.raise_for_status()

        return [Project.from_json(p) for p in response.json()]

    def is_project_id_valid(self, project_id: MODRINTH_ID | MODRINTH_TEMP_ID) -> bool:
        """
        Check if the project id or slug (temporary/friendly id) is valid and accessible.

        Documentation: https://docs.modrinth.com/api/operations/randomprojects/

        :param project_id: The project id or slug to test the validity of.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises RuntimeError: If a successful (200..299) status code is received but it isn't the documented 200.
        :returns: True is the project id is valid and accessible to the current user.
        """

        response = requests.get(
            f"{self.api_url}/project/{project_id}/check",
            headers={"User-Agent": self.user_agent},
        )

        if response.status_code == 404:
            return False

        if response.status_code == 200:
            return True

        response.raise_for_status()
        raise RuntimeError(
            f"It should be impossible to reach this exception. Response={response}"
        )

    def get_project_dependencies(
        self, project_id: MODRINTH_ID | MODRINTH_TEMP_ID
    ) -> ProjectDependencies:
        """
        Gets all data for a project.

        Documentation: https://docs.modrinth.com/api/operations/getprojectversions/

        :param project_id: The ID or slug of the project.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/project/{project_id}",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return ProjectDependencies.from_json(response.json())

    def get_project_versions(
        self,
        project_id: MODRINTH_ID | MODRINTH_TEMP_ID,
        *,
        loaders: Iterable[LOADER] | None = None,
        game_versions: Iterable[GAME_VERSION] | None = None,
        featured: bool | None = None,
    ) -> list[Version]:
        """
        Gets all versions for the specified project.

        Documentation: https://docs.modrinth.com/api/operations/getprojectversions/

        :param project_id: The ID or slug of the project.
        :param loaders: The types of loaders to filter for (i.e. ["fabric"]).
        :param game_versions: The game versions to filter for (i.e. ["1.18.1"]).
        :param featured: Allows to filter for featured or non-featured versions only.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        filters: dict[str, Any] = dict()

        if loaders is not None:
            filters["loaders"] = json.dumps(tuple(loaders))
        if game_versions is not None:
            filters["game_versions"] = json.dumps(tuple(game_versions))
        if featured is not None:
            filters["featured"] = featured

        response = requests.get(
            f"{self.api_url}/project/{project_id}/version",
            headers={"User-Agent": self.user_agent},
            params=filters,
        )
        response.raise_for_status()

        return [Version.from_json(r) for r in response.json()]

    def get_version(self, version_id: MODRINTH_ID) -> Version:
        """
        Gets data for a specific project version.

        Documentation: https://docs.modrinth.com/api/operations/getversion/

        :param version_id: The ID of the version.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/version/{version_id}",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return Version.from_json(response.json())

    def get_version_by_version_id(
        self, project_id: MODRINTH_ID | MODRINTH_TEMP_ID, version_id: MODRINTH_ID
    ) -> Version:
        """
        Gets data for a specific project version by version id.

        Documentation: https://docs.modrinth.com/api/operations/getversion/

        :param project_id: The ID or slug of the project.
        :param version_id: The ID of the version.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/project/{project_id}/version/{version_id}",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return Version.from_json(response.json())

    # TODO: Figure out what the default case for `multiple` is
    def get_version_by_version_number(
        self, project_id: MODRINTH_ID | MODRINTH_TEMP_ID, version_number: VersionNumber
    ) -> Version:
        """
        Gets data for a specific project version by version number.

        If the version number matches multiple versions, only the oldest matching version will be returned.

        Documentation: https://docs.modrinth.com/api/operations/getversion/

        :param project_id: The ID or slug of the project.
        :param version_number: The version number of the version.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/project/{project_id}/version/{str(version_number)}",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return Version.from_json(response.json())

    def get_versions(self, version_ids: Iterable[MODRINTH_ID]) -> list[Version]:
        """
        Gets multiple versions by their version ids.

        Documentation: https://docs.modrinth.com/api/operations/getversions/

        :param version_ids: The IDs of the versions.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/versions",
            headers={"User-Agent": self.user_agent},
            params={"ids": json.dumps(tuple(version_ids))},
        )
        response.raise_for_status()

        return [Version.from_json(r) for r in response.json()]

    def get_version_from_hash(
        self,
        file_hash: HASH,
        algorithm: Literal[None, "auto", "sha1", "sha512"] = "auto",
    ) -> Version:
        """
        Gets a version from a hash of its file.

        If multiple versions match, it's unclear from documentation which will be returned.

        If the algorithm is left as `'auto'`,
        the chosen algorithm will be based on the length of the hash.
        If the hash-string is 128 characters long,
        the algorithm will be set to `'sha512'`,
        else it will defer to the default
        (which will be `'sha1'`).

        Documentation: https://docs.modrinth.com/api/operations/versionfromhash/

        :param file_hash: The hash of the file.
        :param algorithm: The hashing algorithm used for the hash.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        if algorithm == "auto":
            algorithm = "sha512" if len(file_hash) == 128 else None

        query_parameters: dict[str, Any] = {"multiple": False}
        if algorithm is not None:
            query_parameters["algorithm"] = algorithm

        response = requests.get(
            f"{self.api_url}/version_file/{file_hash}",
            headers={"User-Agent": self.user_agent},
            params=query_parameters,
        )
        response.raise_for_status()

        return Version.from_json(response.json())

    def get_versions_from_hash(
        self,
        file_hash: HASH,
        algorithm: Literal[None, "auto", "sha1", "sha512"] = "auto",
    ) -> list[Version]:
        """
        Gets all versions matching a hash of a file.

        If the algorithm is left as `'auto'`,
        the chosen algorithm will be based on the length of the hash.
        If the hash-string is 128 characters long,
        the algorithm will be set to `'sha512'`,
        else it will defer to the default
        (which will be `'sha1'`).

        Documentation: https://docs.modrinth.com/api/operations/versionfromhash/

        :param file_hash: The hash of the file.
        :param algorithm: The hashing algorithm used for the hash.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        if algorithm == "auto":
            algorithm = "sha512" if len(file_hash) == 128 else None

        query_parameters: dict[str, Any] = {"multiple": True}
        if algorithm is not None:
            query_parameters["algorithm"] = algorithm

        response = requests.get(
            f"{self.api_url}/version_file/{file_hash}",
            headers={"User-Agent": self.user_agent},
            params=query_parameters,
        )
        response.raise_for_status()

        return [Version.from_json(r) for r in response.json()]

    def get_latest_version_from_hash(
        self,
        loaders: Iterable[LOADER],
        game_versions: Iterable[GAME_VERSION],
        file_hash: HASH,
        algorithm: Literal[None, "auto", "sha1", "sha512"] = "auto",
    ) -> Version:
        """
        Gets the latest version of a project from a file hash.

        If the algorithm is left as `'auto'`,
        the chosen algorithm will be based on the length of the hash.
        If the hash-string is 128 characters long,
        the algorithm will be set to `'sha512'`,
        else it will defer to the default
        (which will be `'sha1'`).

        Documentation: https://docs.modrinth.com/api/operations/getlatestversionfromhash/

        :param loaders: The types of loaders to filter for (i.e. ["fabric"]).
        :param game_versions: The game versions to filter for (i.e. ["1.18.1"]).
        :param file_hash: The hash of the file (not base64 encoded).
        :param algorithm: The hashing algorithm used for the hash.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        if algorithm == "auto":
            algorithm = "sha512" if len(file_hash) == 128 else None

        query_parameters: dict[str, Any] = {
            "loaders": json.dumps(tuple(loaders)),
            "game_versions": json.dumps(tuple(game_versions)),
        }
        if algorithm is not None:
            query_parameters["algorithm"] = algorithm

        response = requests.get(
            f"{self.api_url}/version_file/{file_hash}/update",
            headers={"User-Agent": self.user_agent},
            params=query_parameters,
        )
        response.raise_for_status()

        return Version.from_json(response.json())

    def get_versions_from_hashes(
        self,
        file_hashes: Iterable[HASH],
        algorithm: Literal["sha1", "sha512"],
    ) -> dict[HASH, Version]:
        """
        Gets all versions matching the file hashes.

        All hashes must use the same hashing algorithm.

        Documentation: https://docs.modrinth.com/api/operations/versionsfromhashes/

        :param file_hashes: The hash of the file.
        :param algorithm: The hashing algorithm used for all the hashes.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        :returns: A mapping of each file_hash to its Version.
        """

        response = requests.get(
            f"{self.api_url}/version_files",
            headers={"User-Agent": self.user_agent},
            params={"hashes": json.dumps(tuple(file_hashes)), "algorithm": algorithm},
        )
        response.raise_for_status()

        return {hash: Version.from_json(version) for hash, version in response.json()}

    def get_latest_versions_from_hashes(
        self,
        loaders: Iterable[LOADER],
        game_versions: Iterable[GAME_VERSION],
        file_hashes: Iterable[HASH],
        algorithm: Literal["sha1", "sha512"],
    ) -> dict[HASH, Version]:
        """
        Gets the latest versions of each project based on the file hash.

        Documentation: https://docs.modrinth.com/api/operations/getlatestversionsfromhashes/

        :param loaders: The types of loaders to filter for (i.e. ["fabric"]).
        :param game_versions: The game versions to filter for (i.e. ["1.18.1"]).
        :param file_hashes: The hash of the file (not base64 encoded).
        :param algorithm: The hashing algorithm used for the hash.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        :returns: A mapping of each file_hash to its Version.
        """

        query_parameters: dict[str, Any] = {
            "loaders": json.dumps(tuple(loaders)),
            "game_versions": json.dumps(tuple(game_versions)),
            "hashes": json.dumps(tuple(file_hashes)),
        }

        response = requests.get(
            f"{self.api_url}/version_files/update",
            headers={"User-Agent": self.user_agent},
            params=query_parameters,
        )
        response.raise_for_status()

        return {hash: Version.from_json(version) for hash, version in response.json()}

    def get_user(self, user_id: MODRINTH_ID | MODRINTH_TEMP_ID) -> User:
        """
        Gets data for a specific user.

        Documentation: https://docs.modrinth.com/api/operations/getuser/

        :param version_id: The ID or slug of the user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/user/{user_id}",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return User.from_json(response.json())

    def get_users(
        self, user_ids: Iterable[MODRINTH_ID | MODRINTH_TEMP_ID]
    ) -> list[User]:
        """
        Gets data for a list of users.

        Documentation: https://docs.modrinth.com/api/operations/getusers/

        :param user_ids: The IDs and/or slugs of the users.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/users",
            headers={"User-Agent": self.user_agent},
            params={"ids": json.dumps(tuple(user_ids))},
        )
        response.raise_for_status()

        return [User.from_json(u) for u in response.json()]

    def get_projects_by_user(
        self, user_id: MODRINTH_ID | MODRINTH_TEMP_ID
    ) -> list[Project]:
        """
        Gets all projects owned by specific user.

        Documentation: https://docs.modrinth.com/api/operations/getuserprojects/

        :param user_ids: The IDs and/or slugs of the users.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/user/{user_id}/projects",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return [Project.from_json(p) for p in response.json()]

    def get_team_members_of_project(
        self, project_id: MODRINTH_ID | MODRINTH_TEMP_ID
    ) -> list[TeamMember]:
        """
        Gets all projects owned by specific user.

        Documentation: https://docs.modrinth.com/api/operations/getprojectteammembers/

        :param project_id: The ID or slug of the project.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/project/{project_id}/members",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return [TeamMember.from_json(t) for t in response.json()]

    def get_team_members_teams(
        self, team_ids: Iterable[MODRINTH_ID]
    ) -> list[list[TeamMember]]:
        """
        Gets all members of each team specified.

        Documentation: https://docs.modrinth.com/api/operations/getteams/

        :param team_ids: The IDs of the teams.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        :returns: A list for each team, where each list contains a list of it's members.
        """

        response = requests.get(
            f"{self.api_url}/teams",
            headers={"User-Agent": self.user_agent},
            params={"ids": json.dumps(tuple(team_ids))},
        )
        response.raise_for_status()

        return [
            [TeamMember.from_json(member) for member in team]
            for team in response.json()
        ]

    def get_categories(self) -> list[Category]:
        """
        Gets all project categories.

        Documentation: https://docs.modrinth.com/api/operations/categorylist/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/tag/category",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return [Category.from_json(c) for c in response.json()]

    def get_loaders(self) -> list[Loader]:
        """
        Gets all project loaders.

        Documentation: https://docs.modrinth.com/api/operations/loaderlist/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/tag/loader",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return [Loader.from_json(l) for l in response.json()]

    def get_game_versions(self) -> list[GameVersion]:
        """
        Gets all game versions.

        Documentation: https://docs.modrinth.com/api/operations/versionlist/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/tag/game_version",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return [GameVersion.from_json(g) for g in response.json()]

    @deprecated("This API endpoint is deprecated. Use SPDX IDs instead.")
    def get_deprecated_licenses(self) -> list[DeprecatedLicense]:
        """
        Gets all licenses using the old, now-deprecated format.

        Documentation: https://docs.modrinth.com/api/operations/licenselist/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/tag/license",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return [DeprecatedLicense.from_json(l) for l in response.json()]

    def get_license(self, license_id: str) -> License:
        """
        Gets information connected to a license id.

        Documentation: https://docs.modrinth.com/api/operations/licensetext/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/tag/license/{license_id}",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return License.from_json(response.json())

    def get_donation_platforms(self) -> list[DonationPlatform]:
        """
        Gets all game versions.

        Documentation: https://docs.modrinth.com/api/operations/donationplatformlist/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/tag/donation_platform",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return [DonationPlatform.from_json(d) for d in response.json()]

    def get_report_types(self) -> list[str]:
        """
        Gets all report types.

        Documentation: https://docs.modrinth.com/api/operations/reporttypelist/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        """

        response = requests.get(
            f"{self.api_url}/tag/report_type",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return response.json()

    def get_project_types(self) -> list[str]:
        """
        Gets all project types.

        Documentation: https://docs.modrinth.com/api/operations/projecttypelist/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        """

        response = requests.get(
            f"{self.api_url}/tag/project_type",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return response.json()

    def get_side_types(self) -> list[str]:
        """
        Gets all side types. (i.e. 'required', 'optional', etc.)

        Documentation: https://docs.modrinth.com/api/operations/sidetypelist/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        """

        response = requests.get(
            f"{self.api_url}/tag/side_type",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return response.json()

    def get_forge_update(
        self,
        project_id: MODRINTH_ID | MODRINTH_TEMP_ID,
    ) -> list[ForgeUpdates]:
        """
        This is part of a system used by Forge to notify users when new mod updates are available.

        Documentation: https://docs.modrinth.com/api/operations/forgeupdates/

        :param project_id: The ID or slug of the project.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/tag/{project_id}/forge_updates.json",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return [ForgeUpdates.from_json(f) for f in response.json()]

    def get_modrinth_statistics(self) -> ModrinthStatistics:
        """
        Returns statistics Modrinth publishes about itself.

        Documentation: https://docs.modrinth.com/api/operations/statistics/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/statistics",
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        return ModrinthStatistics.from_json(response.json())
