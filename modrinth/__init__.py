import json
from datetime import datetime
from typing import Any, Iterable, Literal, Protocol
from warnings import deprecated

import requests
from requests_toolbelt import MultipartEncoder

from modrinth.constants import API_V2_PRODUCTION
from modrinth.model import (
    AllFacets,
    Category,
    DATE_FORMAT,
    DeprecatedLicense,
    DonationPlatform,
    ForgeUpdates,
    GameVersion,
    LicenseText,
    Loader,
    MessageTextBody,
    ModrinthStatistics,
    Notification,
    PayoutHistory,
    Permissions,
    Project,
    ProjectCreate,
    ProjectPatch,
    ProjectPatches,
    ProjectDependencies,
    PersonalUser,
    Report,
    SearchResult,
    TeamMember,
    Thread,
    User,
    UserPatch,
    Version,
    VersionCreate,
    VersionPatch,
)
from modrinth.types import (
    GAME_VERSION,
    HASH,
    HASH_ALGORITHM,
    IMAGE,
    IMAGE_FILE_EXTENSION,
    LOADER,
    MODRINTH_ID,
    MODRINTH_TEMP_ID,
    REQUESTED_PROJECT_STATUS,
    VERSION_NUMBER,
)


class Auth(Protocol):
    def get_auth_token(self) -> str:
        """
        Returns what should be the value of the Authorization header.

        This may require a decent amount of work and throw errors.
        This will be updated later when OAuth2 support is implemented.
        """
        ...


class PersonalAccessTokenAuth(Auth):
    def __init__(self, personal_access_token: str):
        super().__init__()
        self.personal_access_token = personal_access_token

    def get_auth_token(self) -> str:
        return self.personal_access_token


class OAuth2Auth(Auth):
    """
    A placeholder for if OAuth2 authentication is added.
    """

    def get_auth_token(self) -> str:
        raise NotImplementedError(
            "Support for OAuth2 is not yet implemented in this library"
        )


class ModrinthApi2:
    """
    Used to make requests to Modrinth's API which do not require authentication.

    Authentication can still be provided, in which case it will be used.
    """

    def __init__(
        self,
        *,
        user_agent: str,
        authentication: Auth | None = None,
        api_url: str = API_V2_PRODUCTION,
        always_use_auth: bool = False,
    ):
        """
        :param user_agent: The owner of the app making the API requests. See https://docs.modrinth.com/api/#user-agents
        :param api_url: Allows setting a different API endpoint.
        """
        self.api_url = api_url
        self.user_agent = user_agent
        self.authorization = authentication
        self.always_use_auth = always_use_auth

    def __repr__(self) -> str:
        return f"ModrinthApi2(user_agent='{self.user_agent}', authentication='{self.authorization}',api_url='{self.api_url}', always_use_auth='{self.always_use_auth}')"

    def _get_headers(self) -> dict[str, str]:
        headers = {"User-Agent": self.user_agent}
        if self.always_use_auth and self.authorization is not None:
            headers["Authorization"] = self.authorization.get_auth_token()

        return headers

    __get_headers = _get_headers

    def search_projects(
        self,
        query: str | None = None,
        facets: AllFacets | None = None,
        index: (
            Literal["relevance", "downloads", "follows", "newest", "updated"] | None
        ) = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[SearchResult]:
        """
        Gets all data for a project.

        Documentation: https://docs.modrinth.com/api/operations/getprojectversions/

        :param query: The text to search for.
        :param facets: Filters on the search.
        :param index: The sorting method. Defaults to "relevance".
        :param offset: The number of results to skip.
        :param limit: The number of results to collect. Must be in the range 1..100 Defaults to 10.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """
        params: dict = {}
        if query is not None:
            params["query"] = query
        if facets is not None:
            params["facets"] = json.dumps(facets.to_json())
        if index is not None:
            params["index"] = index
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit

        response = requests.get(
            f"{self.api_url}/search",
            headers=self.__get_headers(),
            params=params,
        )
        response.raise_for_status()

        return [SearchResult.from_json(s) for s in response.json()]

    def get_project(self, project_id: MODRINTH_TEMP_ID | MODRINTH_ID) -> Project:
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
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return Project.from_json(response.json())

    def get_projects(
        self,
        project_ids: Iterable[MODRINTH_TEMP_ID | MODRINTH_ID],
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
            headers=self.__get_headers(),
            params={"ids": json.dumps(tuple(project_ids))},
        )
        response.raise_for_status()

        return [Project.from_json(p) for p in response.json()]

    def get_random_projects(self, count: int) -> list[Project]:
        """
        Gets a random set of `count` projects.

        Documentation: https://docs.modrinth.com/api/operations/randomprojects/

        :param count: The number of projects to return. Must be in the range 0..100 inclusive.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/projects_random",
            headers=self.__get_headers(),
            params={"count": count},
        )
        response.raise_for_status()

        return [Project.from_json(p) for p in response.json()]

    def is_project_id_valid(self, project_id: MODRINTH_TEMP_ID | MODRINTH_ID) -> bool:
        """
        Check if the project id or slug (temporary/friendly id) is valid and accessible.

        If the project exists but is inaccessible to the current user,
        this will still return `False`.

        Documentation: https://docs.modrinth.com/api/operations/checkprojectvalidity/

        :param project_id: The project id or slug to test the validity of.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises RuntimeError: If a successful (200..299) status code is received but it isn't the documented 200.
        :returns: True if the project id is valid and accessible to the current user.
        """

        response = requests.get(
            f"{self.api_url}/project/{project_id}/check",
            headers=self.__get_headers(),
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
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
    ) -> ProjectDependencies:
        """
        Gets data about all projects and versions that the specified project depends on.

        Documentation: https://docs.modrinth.com/api/operations/getdependencies/

        :param project_id: The ID or slug of the project.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/project/{project_id}/dependencies",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return ProjectDependencies.from_json(response.json())

    def get_project_versions(
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
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
            filters["featured"] = "true" if featured else "false"

        response = requests.get(
            f"{self.api_url}/project/{project_id}/version",
            headers=self.__get_headers(),
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
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return Version.from_json(response.json())

    def get_version_by_version_id(
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        version_id: MODRINTH_ID,
    ) -> Version:
        """
        Gets data for a specific project version by version id.

        This specific option is redundant as `get_version()` exists.

        Documentation: https://docs.modrinth.com/api/operations/getversion/

        :param project_id: The ID or slug of the project.
        :param version_id: The ID of the version.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/project/{project_id}/version/{version_id}",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return Version.from_json(response.json())

    def get_version_by_version_number(
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        version_number: VERSION_NUMBER,
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
            f"{self.api_url}/project/{project_id}/version/{version_number}",
            headers=self.__get_headers(),
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
            headers=self.__get_headers(),
            params={"ids": json.dumps(tuple(version_ids))},
        )
        response.raise_for_status()

        return [Version.from_json(r) for r in response.json()]

    def get_version_from_hash(
        self,
        file_hash: HASH,
        algorithm: HASH_ALGORITHM | Literal["auto"] | None = "auto",
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
            headers=self.__get_headers(),
            params=query_parameters,
        )
        response.raise_for_status()

        return Version.from_json(response.json())

    def get_versions_from_hash(
        self,
        file_hash: HASH,
        algorithm: HASH_ALGORITHM | Literal["auto"] | None = "auto",
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
            headers=self.__get_headers(),
            params=query_parameters,
        )
        response.raise_for_status()

        return [Version.from_json(r) for r in response.json()]

    def get_latest_version_from_hash(
        self,
        loaders: Iterable[LOADER],
        game_versions: Iterable[GAME_VERSION],
        file_hash: HASH,
        algorithm: HASH_ALGORITHM | Literal["auto"] = "auto",
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
        :param file_hash: The hash of the file encoded as hexadecimal.
        :param algorithm: The hashing algorithm used for the hash.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        if algorithm == "auto":
            algorithm = "sha512" if len(file_hash) == 128 else "sha1"

        response = requests.post(
            f"{self.api_url}/version_file/{file_hash}/update",
            headers=self.__get_headers(),
            params={"algorithm": algorithm},
            json={
                "loaders": loaders,
                "game_versions": game_versions,
            },
        )
        response.raise_for_status()

        return Version.from_json(response.json())

    def get_versions_from_hashes(
        self,
        file_hashes: Iterable[HASH],
        algorithm: HASH_ALGORITHM,
    ) -> dict[HASH, Version]:
        """
        Gets all versions matching the file hashes.

        All hashes must use the same hashing algorithm.

        Documentation: https://docs.modrinth.com/api/operations/versionsfromhashes/

        :param file_hashes: The hashes of the files.
        :param algorithm: The hashing algorithm used for all the hashes.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        :returns: A mapping of each file_hash to its Version.
        """

        response = requests.post(
            f"{self.api_url}/version_files",
            headers=self.__get_headers(),
            json={
                "hashes": file_hashes,
                "algorithm": algorithm,
            },
        )
        response.raise_for_status()

        return {hash: Version.from_json(version) for hash, version in response.json()}

    def get_latest_versions_from_hashes(
        self,
        loaders: Iterable[LOADER],
        game_versions: Iterable[GAME_VERSION],
        file_hashes: Iterable[HASH],
        algorithm: HASH_ALGORITHM,
    ) -> dict[HASH, Version]:
        """
        Gets the latest versions of each project based on the file hash.

        Documentation: https://docs.modrinth.com/api/operations/getlatestversionsfromhashes/

        :param loaders: The types of loaders to filter for (i.e. ["fabric"]).
        :param game_versions: The game versions to filter for (i.e. ["1.18.1"]).
        :param file_hashes: The hashes of the files encoded as hexadecimal.
        :param algorithm: The hashing algorithm used for the hashes.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        :returns: A mapping of each file_hash to its `Version`.
        """

        response = requests.post(
            f"{self.api_url}/version_files/update",
            headers=self.__get_headers(),
            json={
                "loaders": loaders,
                "game_versions": game_versions,
                "hashes": file_hashes,
                "algorithm": algorithm,
            },
        )
        response.raise_for_status()

        return {
            hash: Version.from_json(version)
            for hash, version in response.json().items()
        }

    def get_user(self, user_id: MODRINTH_TEMP_ID | MODRINTH_ID) -> User:
        """
        Gets data for a specific user.

        Documentation: https://docs.modrinth.com/api/operations/getuser/

        :param user_id: The ID or slug of the user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/user/{user_id}",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return User.from_json(response.json())

    def get_users(
        self, user_ids: Iterable[MODRINTH_TEMP_ID | MODRINTH_ID]
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
            headers=self.__get_headers(),
            params={"ids": json.dumps(tuple(user_ids))},
        )
        response.raise_for_status()

        return [User.from_json(u) for u in response.json()]

    def get_projects_by_user(
        self,
        user_id: MODRINTH_TEMP_ID | MODRINTH_ID,
    ) -> list[Project]:
        """
        Gets all projects owned by specific user.

        Documentation: https://docs.modrinth.com/api/operations/getuserprojects/

        :param user_ids: The ID or slug of the user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/user/{user_id}/projects",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return [Project.from_json(p) for p in response.json()]

    def get_team_members_of_project(
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
    ) -> list[TeamMember]:
        """
        Gets all team members who are part of a project.

        Documentation: https://docs.modrinth.com/api/operations/getprojectteammembers/

        :param project_id: The ID or slug of the project.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/project/{project_id}/members",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return [TeamMember.from_json(t) for t in response.json()]

    def get_team_members_teams(
        self,
        team_ids: Iterable[MODRINTH_ID],
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
            headers=self.__get_headers(),
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
            headers=self.__get_headers(),
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
            headers=self.__get_headers(),
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
            headers=self.__get_headers(),
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
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return [DeprecatedLicense.from_json(l) for l in response.json()]

    def get_license_text(self, license_id: str) -> LicenseText:
        """
        Gets information connected to a license id.

        Documentation: https://docs.modrinth.com/api/operations/licensetext/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/tag/license/{license_id}",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return LicenseText.from_json(response.json())

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
            headers=self.__get_headers(),
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
            headers=self.__get_headers(),
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
            headers=self.__get_headers(),
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
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return response.json()

    def get_forge_update(
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
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
            headers=self.__get_headers(),
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
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return ModrinthStatistics.from_json(response.json())


class ModrinthAuthenticatedApi2(ModrinthApi2):
    """
    Used to make requests to Modrinth's API which require authentication.

    This is a very incomplete definition of v2 of Modrinth's API.
    """

    def __init__(
        self,
        *,
        user_agent: str,
        authentication: Auth,
        api_url: str = API_V2_PRODUCTION,
        always_use_auth: bool = False,
    ):
        super().__init__(
            user_agent=user_agent,
            api_url=api_url,
            authentication=authentication,
            always_use_auth=always_use_auth,
        )

    def __repr__(self) -> str:
        return f"ModrinthAuthenticatedApi2(user_agent='{self.user_agent}', authentication='{self.authorization}',api_url='{self.api_url}')"

    def _get_headers(self) -> dict[str, str]:
        headers = {"User-Agent": self.user_agent}
        if self.authorization is not None:
            headers["Authorization"] = self.authorization.get_auth_token()

        return headers

    __get_headers = _get_headers

    def delete_project(self, project_id: MODRINTH_TEMP_ID | MODRINTH_ID) -> None:
        """
        Delete a project the user owns.

        Documentation: https://docs.modrinth.com/api/operations/deleteproject/

        :param project_id: The ID or slug of a project_id the current user owns.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.delete(
            f"{self.api_url}/project/{project_id}",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

    def modify_project(
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        project_data: ProjectPatch,
    ) -> None:
        """
        Updates/patches data for a specific project.

        Documentation: https://docs.modrinth.com/api/operations/modifyproject/

        :param project_id: The ID or slug of a project owned by the current user.
        :param project_data: The data to update for the project.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.patch(
            f"{self.api_url}/project/{project_id}",
            headers=self.__get_headers(),
            json=project_data.to_json(),
        )
        response.raise_for_status()

    def modify_projects(
        self,
        project_ids: Iterable[MODRINTH_TEMP_ID | MODRINTH_ID],
        shared_project_data: ProjectPatches,
    ) -> None:
        """
        Updates/patches data for multiple projects at the same time.

        Documentation: https://docs.modrinth.com/api/operations/modifyproject/

        :param project_ids: The IDs/slugs of projects owned by the current user.
        :param shared_project_data: The data to update for all the listed projects.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.patch(
            f"{self.api_url}/project",
            headers=self.__get_headers(),
            params={"ids": json.dumps(project_ids)},
            json=shared_project_data.to_json(),
        )
        response.raise_for_status()

    def create_project(
        self,
        project: ProjectCreate,
        icon: IMAGE | None = None,
    ) -> Project:
        """
        Creates a new project.

        Documentation: https://docs.modrinth.com/api/operations/createproject/

        :param project: Data for the new project.
        :param icon: The icon for the project.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """
        fields: dict = {"data": project.to_json()}
        if icon is not None:
            fields["icon"] = icon

        multipart_encoder = MultipartEncoder(fields=fields)

        headers = self.__get_headers()
        headers["Content-Type"] = multipart_encoder.content_type

        response = requests.post(
            f"{self.api_url}/project",
            headers=headers,
            json=multipart_encoder,
        )
        response.raise_for_status()

        return Project.from_json(response.json())

    def delete_project_icon(self, project_id: MODRINTH_TEMP_ID | MODRINTH_ID) -> None:
        """
        Deletes the icon for a project.

        Documentation: https://docs.modrinth.com/api/operations/deleteprojecticon/

        :param project_id: The ID or slug of a project_id the current user owns.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.delete(
            f"{self.api_url}/project/{project_id}/icon",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

    def change_project_icon(
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        icon: IMAGE,
        file_type: IMAGE_FILE_EXTENSION,
    ) -> None:
        """
        Updates/patches data for a specific project.

        Documentation: https://docs.modrinth.com/api/operations/modifyproject/

        :param project_id: The ID or slug of a project owned by the current user.
        :param icon: The new icon. Must be <= 256KiB in size.
        :param file_type: The type of file being uploaded.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        headers: dict = self.__get_headers()
        headers["Content-Type"] = file_type

        response = requests.patch(
            f"{self.api_url}/project/{project_id}/icon",
            headers=headers,
            params={"ext": file_type},
            json=icon,
        )
        response.raise_for_status()

    def add_gallery_image(
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        image: IMAGE | None,
        file_type: IMAGE_FILE_EXTENSION,
        featured: bool,
        title: str | None,
        description: str | None,
        ordering: int | None,
    ) -> Project:
        """
        Add a new image to a project's gallery.

        Documentation: https://docs.modrinth.com/api/operations/addgalleryimage/

        :param project_id: The ID or slug of a project owned by the current user.
        :param image: The image for the gallery. Must be <= 5MiB.
        :param file_type: The type of image being uploaded.
        :param featured: Whether or not the image is featured.
        :param title: The image's title.
        :param description: A description to be displayed with the image.
        :param ordering: The ordering of the image. Order is sort by ordering and then by age.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        headers = self.__get_headers()
        headers["Content-Type"] = f"image/{file_type}"

        params: dict = {
            "ext": file_type,
            "featured": featured,
        }

        if title is not None:
            params["title"] = title

        if description is not None:
            params["description"] = title

        if ordering is not None:
            params["ordering"] = title

        response = requests.post(
            f"{self.api_url}/project/{project_id}/gallery",
            headers=headers,
            params=params,
            json=image,
        )
        response.raise_for_status()

        return Project.from_json(response.json())

    def delete_gallery_image(
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        image_url: str,
    ) -> None:
        """
        Deletes the icon for a project.

        Documentation: https://docs.modrinth.com/api/operations/deleteprojecticon/

        :param project_id: The ID or slug of a project_id the current user owns.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.delete(
            f"{self.api_url}/project/{project_id}/gallery",
            headers=self.__get_headers(),
            params={"url": image_url},
        )
        response.raise_for_status()

    def modify_gallery_image_data(
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        url: str,
        featured: bool | None = None,
        title: str | None = None,
        description: str | None = None,
        ordering: int | None = None,
    ) -> None:
        """
        Modify the data associated with a gallery image.

        Documentation: https://docs.modrinth.com/api/operations/modifygalleryimage/

        :param project_id: The ID or slug of a project owned by the current user.
        :param url: Url to the image to modify the data of.s
        :param featured: Whether or not the image is featured.
        :param title: The image's title.
        :param description: A description to be displayed with the image.
        :param ordering: The ordering of the image. Order is sort by ordering and then by age.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        params: dict = {
            "url": url,
        }

        if featured is not None:
            params["featured"] = "true" if featured else "false"

        if title is not None:
            params["title"] = title

        if description is not None:
            params["description"] = title

        if ordering is not None:
            params["ordering"] = title

        response = requests.post(
            f"{self.api_url}/project/{project_id}/gallery",
            headers=self.__get_headers(),
            params=params,
        )
        response.raise_for_status()

    def follow_project(self, project_id: MODRINTH_TEMP_ID | MODRINTH_ID) -> None:
        """
        Makes the current user follow the specified project.

        Documentation: https://docs.modrinth.com/api/operations/followproject/

        :param project_id: Project id/slug to follow.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.post(
            f"{self.api_url}/project/{project_id}/follow",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

    def unfollow_project(self, project_id: MODRINTH_TEMP_ID | MODRINTH_ID) -> None:
        """
        Makes the current user unfollow the specified project.

        Documentation: https://docs.modrinth.com/api/operations/unfollowproject/

        :param project_id: Project id/slug to unfollow.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.delete(
            f"{self.api_url}/project/{project_id}/follow",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

    def schedule_project(
        self,
        project_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        time: datetime,
        requested_status: REQUESTED_PROJECT_STATUS,
    ) -> None:
        """
        Schedules a status change for the specified project at a particular datetime.

        Documentation: https://docs.modrinth.com/api/operations/scheduleproject/

        :param project_id: Project id/slug to schedule.
        :param time: The time to change the project status.
        :param requested_status: The status to change the project to.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.post(
            f"{self.api_url}/project/{project_id}/schedule",
            headers=self.__get_headers(),
            json={
                "time": time.strftime(DATE_FORMAT),
                "requested_status": requested_status,
            },
        )
        response.raise_for_status()

    def delete_version(self, version_id: MODRINTH_ID) -> None:
        """
        Delete a version from a project.

        Documentation: https://docs.modrinth.com/api/operations/deleteversion/

        :param version_id: The ID of a version the current user owns.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.delete(
            f"{self.api_url}/project/{version_id}",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

    def modify_version(
        self,
        version_id: MODRINTH_ID,
        version_data: VersionPatch,
    ) -> None:
        """
        Updates/patches data for a specific project.

        Documentation: https://docs.modrinth.com/api/operations/modifyversion/

        :param version_id: The ID of a version owned by the current user.
        :param version_data: The data to update for the version.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.patch(
            f"{self.api_url}/version/{version_id}",
            headers=self.__get_headers(),
            json=version_data.to_json(),
        )
        response.raise_for_status()

    def create_version(
        self,
        version: VersionCreate,
        files: dict[str, bytes] | None,
    ) -> Version:
        """
        Creates a new version.

        Each file must be referenced within the `file_parts`.
        If you choose a `primary_file`, it must be one of the uploaded files.

        `files` can be None only if the upload type is `draft`.

        Accepted file types are `.mrpack`, `.jar`, `.zip`, and `.litemod`.

        Documentation: https://docs.modrinth.com/api/operations/createversion/

        :param version: Data for the new version.
        :param files: The files which are part of the version where each key is a file name.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """
        fields: dict = {"data": version.to_json()}
        if files is not None:
            for filename, file in files.items():
                fields[filename] = file

        multipart_encoder = MultipartEncoder(fields=fields)

        headers = self.__get_headers()
        headers["Content-Type"] = multipart_encoder.content_type

        response = requests.post(
            f"{self.api_url}/version",
            headers=headers,
            json=multipart_encoder,
        )
        response.raise_for_status()

        return Version.from_json(response.json())

    def schedule_version(
        self,
        version_id: MODRINTH_ID,
        time: datetime,
        requested_status: REQUESTED_PROJECT_STATUS,  # TODO: is this correct
    ) -> None:
        """
        Schedules a status change for the specified version at a particular datetime.

        Documentation: https://docs.modrinth.com/api/operations/scheduleversion/

        :param version_id: ID of the version to schedule.
        :param time: The time to change the project status.
        :param requested_status: The status to change the project to.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.post(
            f"{self.api_url}/version/{version_id}/schedule",
            headers=self.__get_headers(),
            json={
                "time": time.strftime(DATE_FORMAT),
                "requested_status": requested_status,
            },
        )
        response.raise_for_status()

    def add_files_to_version(
        self,
        version_id: MODRINTH_ID,
        files: dict[str, bytes] | None,
    ) -> Version:
        """
        Adds files to the specified version.

        Each filename must match the names listed in the version's file parts.

        Accepted files are `.mrpack` and `.jar`.

        Documentation: https://docs.modrinth.com/api/operations/addfilestoversion/
        Should be similar to https://docs.modrinth.com/api/operations/createversion/

        :param version_id: ID of the version to add files to.
        :param files: The files which are part of the version where each key is a file name.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """
        fields: dict = {}
        if files is not None:
            for filename, file in files.items():
                fields[filename] = file

        multipart_encoder = MultipartEncoder(fields=fields)

        headers = self.__get_headers()
        headers["Content-Type"] = multipart_encoder.content_type

        response = requests.post(
            f"{self.api_url}/version/{version_id}",
            headers=headers,
            json=multipart_encoder,
        )
        response.raise_for_status()

        return Version.from_json(response.json())

    def delete_version_file(
        self,
        file_hash: HASH,
        algorithm: HASH_ALGORITHM | Literal["auto"] = "auto",
        version_id: MODRINTH_ID | None = None,
    ) -> None:
        """
        Delete a file from a project version.

        If `algorithm` is left as `"auto"`,
        the algorithm will be automatically chosen based on the length of `file_hash`.
        If `file_hash` is `128` bytes long,
        it will be set to `sha512`,
        else it will be set to `sha1`.

        Documentation: https://docs.modrinth.com/api/operations/deletefilefromhash/

        :param file_hash: A `sha1` or `sha512` hash of the file.
        :param algorithm: The hashing algorithm used for the has.
        :param version_id: The ID of a version the current user owns.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """
        if algorithm == "auto":
            algorithm = "sha512" if len(file_hash) == 128 else "sha1"

        params: dict = {"algorithm": algorithm}
        if version_id is not None:
            params["version_id"] = version_id

        response = requests.delete(
            f"{self.api_url}/version_file/{file_hash}",
            headers=self.__get_headers(),
            params=params,
        )
        response.raise_for_status()

    def modify_user(
        self,
        user_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        user_data: UserPatch,
    ) -> None:
        """
        Updates/patches data for a specific user.

        Documentation: https://docs.modrinth.com/api/operations/modifyuser/

        :param user_id: The ID or slug of the user. Must match the current user.
        :param user_data: The data to update for the user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.patch(
            f"{self.api_url}/user/{user_id}",
            headers=self.__get_headers(),
            json=user_data.to_json(),
        )
        response.raise_for_status()

    def get_self_user(self) -> PersonalUser:
        """
        Gets data for your own user.

        Documentation: https://docs.modrinth.com/api/operations/getuser/

        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/user/",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return PersonalUser.from_json(response.json())

    def delete_user_avatar(self, user_id: MODRINTH_TEMP_ID | MODRINTH_ID) -> None:
        """
        Gets data for your own user.

        Documentation: https://docs.modrinth.com/api/operations/deleteusericon/

        :param user_id: The ID or slug of the user. Must match the current user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.delete(
            f"{self.api_url}/user/{user_id}/icon",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

    def change_user_avatar(
        self,
        user_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        image: IMAGE,
        format: IMAGE_FILE_EXTENSION | None = None,
    ) -> None:
        """
        Gets data for your own user.

        Documentation: https://docs.modrinth.com/api/operations/changeusericon/

        :param user_id: The ID or slug of the user. Must match the current user.
        :param image: The actual image data. Must be no more than 2MiB.
        :param format: The image format. Will be provided as the `Content-Type` if provided.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """
        headers = self.__get_headers()
        if format is not None:
            headers["Content-Type"] = f"image/{format}"

        response = requests.patch(
            f"{self.api_url}/user/{user_id}/icon",
            headers=headers,
            json=image,
        )
        response.raise_for_status()

    def get_followed_projects(
        self,
        user_id: MODRINTH_TEMP_ID | MODRINTH_ID,
    ) -> list[Project]:
        """
        Gets data for your own user.

        Documentation: https://docs.modrinth.com/api/operations/getpayouthistory/

        :param user_id: The ID or slug of the user. Must match the current user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/user/{user_id}/follows",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return [Project.from_json(p) for p in response.json()]

    def get_payout_history(
        self,
        user_id: MODRINTH_TEMP_ID | MODRINTH_ID,
    ) -> list[PayoutHistory]:
        """
        Gets payout history for your user.

        Documentation: https://docs.modrinth.com/api/operations/getpayouthistory/

        :param user_id: The ID or slug of the user. Must match the current user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/user/{user_id}/payouts",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return [PayoutHistory.from_json(p) for p in response.json()]

    def withdraw_payout_balance(
        self,
        user_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        amount: int,
        *,
        i_understand_the_withdrawal_fees: Literal[True],
    ) -> None:
        """
        Makes a withdrawer of the specified number of US dollars.

        Documentation: https://docs.modrinth.com/api/operations/withdrawpayout/

        :param user_id: The ID or slug of the user. Must match the current user.
        :param amount:
        :param i_have_acknowledged_the_withdrawal_fees: Shows that you have read the warnings in the web GUI for withdrawals. Must be True
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """
        if i_understand_the_withdrawal_fees is not True:
            raise ValueError(
                "You haven't acknowledged the withdrawal warnings in the GUI (including fees). The value `i_have_acknowledged_the_withdrawal_fees` must be set to `True` after doing so."
            )

        response = requests.post(
            f"{self.api_url}/user/{user_id}/payouts",
            headers=self.__get_headers(),
            params={"amount": amount},
        )
        response.raise_for_status()

    def get_all_notifications(
        self,
        user_id: MODRINTH_TEMP_ID | MODRINTH_ID,
    ) -> list[Notification]:
        """
        Gets payout history for your user.

        Documentation: https://docs.modrinth.com/api/operations/getpayouthistory/

        :param user_id: The ID or slug of the user. Must match the current user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/user/{user_id}/notifications",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return [Notification.from_json(n) for n in response.json()]

    def get_notification(
        self,
        notification_id: MODRINTH_ID,
    ) -> Notification:
        """
        Gets payout history for your user.

        Documentation: https://docs.modrinth.com/api/operations/getpayouthistory/

        :param notification_id: The ID of the notification. Must belong to the current user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/notification/{notification_id}",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return Notification.from_json(response.json())

    def delete_notification(self, notification_id: MODRINTH_ID) -> None:
        """
        Delete a notification the user owns.

        Documentation: https://docs.modrinth.com/api/operations/deletenotification/

        :param notification_id: The ID of the notification. Must belong to the current user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.delete(
            f"{self.api_url}/notification/{notification_id}",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

    def mark_notification_as_read(self, notification_id: MODRINTH_ID) -> None:
        """
        Updates/patches data for a specific project.

        Documentation: https://docs.modrinth.com/api/operations/modifyproject/

        :param notification_id: The ID of the notification. Must belong to the current user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.patch(
            f"{self.api_url}/notification/{notification_id}",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

    def get_notifications(
        self,
        notification_ids: Iterable[MODRINTH_ID],
    ) -> list[Notification]:
        """
        Gets payout history for your user.

        Documentation: https://docs.modrinth.com/api/operations/getpayouthistory/

        :param notification_id: The IDs of the notifications. Must belong to the current user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/notifications",
            headers=self.__get_headers(),
            params={"ids": json.dumps(tuple(notification_ids))},
        )
        response.raise_for_status()

        return [Notification.from_json(n) for n in response.json()]

    def delete_notifications(self, notification_ids: Iterable[MODRINTH_ID]) -> None:
        """
        Delete a notification the user owns.

        Documentation: https://docs.modrinth.com/api/operations/deletenotification/

        :param notification_id: The ID of the notification. Must belong to the current user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.delete(
            f"{self.api_url}/notifications",
            headers=self.__get_headers(),
            params={"ids": json.dumps(tuple(notification_ids))},
        )
        response.raise_for_status()

    def mark_notifications_as_read(self, notification_ids: MODRINTH_ID) -> None:
        """
        Updates/patches data for a specific project.

        Documentation: https://docs.modrinth.com/api/operations/modifyproject/

        :param notification_id: The ID of the notification. Must belong to the current user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.patch(
            f"{self.api_url}/notifications",
            headers=self.__get_headers(),
            params={"ids": json.dumps(notification_ids)},
        )
        response.raise_for_status()

    def get_open_reports(
        self,
        count: int,
    ) -> list[Report]:
        """
        Gets payout history for your user.

        Documentation: https://docs.modrinth.com/api/operations/getpayouthistory/

        :param count: The maximum number of open reports to return.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/report",
            headers=self.__get_headers(),
            params={"count": count},
        )
        response.raise_for_status()

        return [Report.from_json(r) for r in response.json()]

    def make_report(
        self,
        report_type: str,
        item_id: MODRINTH_ID,
        item_type: Literal["project", "user", "version"],
        body: str,
    ) -> list[Report]:
        """
        Gets payout history for your user.

        Documentation: https://docs.modrinth.com/api/operations/submitreport/

        :param report_type: The type of report being sent. The categories are not listed.
        :param item_id: ID of the item being reported.
        :param item_type: Type of item being reported.
        :param body: Explanation text of the report.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.post(
            f"{self.api_url}/report",
            headers=self.__get_headers(),
            params={
                "report_type": report_type,
                "item_id": item_id,
                "item_type": item_type,
                "body": body,
            },
        )
        response.raise_for_status()

        return [Report.from_json(r) for r in response.json()]

    def get_report(self, report_id: MODRINTH_ID) -> Report:
        """
        Gets the specified report owned by the user.

        Documentation: https://docs.modrinth.com/api/operations/getreport/

        :param report_id: The ID of the report.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/report/{report_id}",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return Report.from_json(response.json())

    def modify_report(
        self,
        report_id: MODRINTH_ID,
        body: str | None = None,
        closed: bool | None = None,
    ) -> None:
        """
        Updates information for a report.

        Documentation: https://docs.modrinth.com/api/operations/modifyreport/

        :param report_id: The ID of the report.
        :param body: Explanation text of the report.
        :param closed: Whether the report should be closed or not.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """
        payload: dict = {}
        if body is not None:
            payload["body"] = body
        if closed is not None:
            payload["closed"] = "true" if closed else "false"

        response = requests.patch(
            f"{self.api_url}/report/{report_id}",
            headers=self.__get_headers(),
            json=payload,
        )
        response.raise_for_status()

    def get_reports(self, report_ids: Iterable[MODRINTH_ID]) -> list[Report]:
        """
        Gets multiple specified reports owned by the user.

        Documentation: https://docs.modrinth.com/api/operations/getreports/

        :param report_ids: The IDs of the reports.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/reports",
            headers=self.__get_headers(),
            params={"ids": json.dumps(tuple(report_ids))},
        )
        response.raise_for_status()

        return [Report.from_json(r) for r in response.json()]

    def get_thread(self, thread_id: MODRINTH_ID) -> Thread:
        """
        Gets the specified thread accessible to the user.

        Documentation: https://docs.modrinth.com/api/operations/getreport/

        :param thread_id: The ID of the thread.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/thread/{thread_id}",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return Thread.from_json(response.json())

    def send_text_message_in_thread(
        self,
        thread_id: MODRINTH_ID,
        message: MessageTextBody,
    ) -> Thread:
        """
        Sends a text message in a texting thread.

        Documentation: https://docs.modrinth.com/api/operations/sendthreadmessage/

        :param thread_id: The ID of the thread.
        :param message: The data to send as part of the text.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """
        response = requests.post(
            f"{self.api_url}/thread/{thread_id}",
            headers=self.__get_headers(),
            json=message.to_json(),
        )
        response.raise_for_status()

        return Thread.from_json(response.json())

    def get_threads(self, thread_ids: Iterable[MODRINTH_ID]) -> list[Thread]:
        """
        Gets the specified threads accessible to the user.

        Documentation: https://docs.modrinth.com/api/operations/getthreads/

        :param thread_id: The IDs of the threads.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/threads",
            headers=self.__get_headers(),
            json={"ids": json.dumps(tuple(thread_ids))},
        )
        response.raise_for_status()

        return [Thread.from_json(t) for t in response.json()]

    def delete_thread_message(self, thread_id: MODRINTH_ID) -> None:
        """
        Delete a thread message the user owns.

        Documentation: https://docs.modrinth.com/api/operations/deletethreadmessage/

        :param thread_id: The ID of the thread. Must belong to the current user.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.delete(
            f"{self.api_url}/message/{thread_id}", headers=self.__get_headers()
        )
        response.raise_for_status()

    def get_team_members(self, team_id: MODRINTH_ID) -> list[TeamMember]:
        """
        Gets members of a team accessible to the user.

        Documentation: https://docs.modrinth.com/api/operations/getreport/

        :param team_id: The ID of the team.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid json.
        :raises KeyError: If the response body is missing a required field.
        """

        response = requests.get(
            f"{self.api_url}/team/{team_id}/members",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

        return [TeamMember.from_json(u) for u in response.json()]

    def add_user_to_team(self, team_id: MODRINTH_ID, user_id: MODRINTH_ID) -> None:
        """
        Adds a the specified user to the specified team.

        Documentation: https://docs.modrinth.com/api/operations/sendthreadmessage/

        :param team_id: The ID of the team.
        :param user_id: The ID of the user to add. Cannot be their username.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """
        response = requests.post(
            f"{self.api_url}/team/{team_id}/members",
            headers=self.__get_headers(),
            json={"user_id": user_id},
        )
        response.raise_for_status()

    def join_team(self, team_id: MODRINTH_ID) -> None:
        """
        Joins the current user to the specified team.

        Documentation: https://docs.modrinth.com/api/operations/sendthreadmessage/

        :param team_id: The ID of the team.
        :param user_id: The ID of the user to add. Cannot be their username.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """
        response = requests.post(
            f"{self.api_url}/team/{team_id}/join",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

    def remove_team_member(
        self,
        team_id: MODRINTH_ID,
        user_id: MODRINTH_TEMP_ID | MODRINTH_ID,
    ) -> None:
        """
        Remove a user from the team.

        Documentation: https://docs.modrinth.com/api/operations/deleteteammember/

        :param team_id: The ID of the team.
        :param user_id: The ID or username of the user to add.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.delete(
            f"{self.api_url}/team/{team_id}/members/{user_id}",
            headers=self.__get_headers(),
        )
        response.raise_for_status()

    def modify_team_member(
        self,
        team_id: MODRINTH_ID,
        user_id: MODRINTH_TEMP_ID | MODRINTH_ID,
        role: str | None,
        permissions: Permissions | None,
        payouts_split: int | None,
        ordering: int | None,
    ) -> None:
        """
        Updates information for a team member.

        Documentation: https://docs.modrinth.com/api/operations/modifyteammember/

        :param team_id: The ID of the team.
        :param user_id: The ID or username of the team member to modify.
        :param role: The user's team role.
        :param permissions: The user's team permissions.
        :param payouts_split: The user's payout split.
        :param ordering: The user's ordering.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        payload: dict = {}
        if role is not None:
            payload["role"] = role
        if permissions is not None:
            payload["permissions"] = permissions
        if payouts_split is not None:
            payload["payouts_split"] = payouts_split
        if ordering is not None:
            payload["ordering"] = ordering

        response = requests.patch(
            f"{self.api_url}/team/{team_id}/members/{user_id}",
            headers=self.__get_headers(),
            json=payload,
        )
        response.raise_for_status()

    def transfer_team_ownership(
        self,
        team_id: MODRINTH_ID,
        user_id: MODRINTH_TEMP_ID | MODRINTH_ID,
    ) -> None:
        """
        Transfers ownership of the team to the other user.

        Documentation: https://docs.modrinth.com/api/operations/transferteamownership/

        :param team_id: The ID of the team.
        :param user_id: The ID or username of the team member to give the team to.
        :raises HTTPError: If the HTTP request to the Modrinth API fails.
        """

        response = requests.patch(
            f"{self.api_url}/team/{team_id}/owner",
            headers=self.__get_headers(),
            json={"user_id": user_id},
        )
        response.raise_for_status()
