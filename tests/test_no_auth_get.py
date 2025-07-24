import json
import unittest
from unittest.mock import patch

import requests
from requests import Response

from responses import cached_capture, ResponseFiles
from modrinth import ModrinthApi2
from modrinth.model import Project, ProjectDependencies, Version
from modrinth.types import MODRINTH_ID

LITHIUM_PROJECT_ID: MODRINTH_ID = "gvQqBUqZ"
TAG_GAME_PROJECT_ID: MODRINTH_ID = "8ZiCD9vV"
LEDGER_PROJECT_ID: MODRINTH_ID = "LVN9ygNV"

LITHIUM_VERSION_ID: MODRINTH_ID = "EhG1mQzx"
TAG_GAME_VERSION_ID: MODRINTH_ID = "yPKyu5Cc"


class TestGetMethods(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = ModrinthApi2(user_agent="SuperDyl/modrinth-api")

    def setUp(self) -> None:
        super().setUp()

    def test_get_project_lithium(self) -> None:
        expected_json: dict = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECT_LITHIUM,
                lambda: self.api.get_project(LITHIUM_PROJECT_ID),
            )
        )

        project = Project.from_json(expected_json)
        parsed_back = project.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_get_project_tag_game(self) -> None:
        expected_json: dict = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECT_TAG_GAME,
                lambda: self.api.get_project(TAG_GAME_PROJECT_ID),
            )
        )

        project = Project.from_json(expected_json)
        parsed_back = project.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_get_projects(self) -> None:

        expected_json: list = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECTS,
                lambda: self.api.get_projects(
                    [LITHIUM_PROJECT_ID, TAG_GAME_PROJECT_ID]
                ),
            )
        )

        projects = [Project.from_json(p) for p in expected_json]
        parsed_back = [p.to_json() for p in projects]

        self.assertListEqual(expected_json, parsed_back)

    def test_get_random_projects(self) -> None:
        COUNT = 3

        expected = json.loads(
            cached_capture(
                ResponseFiles.GET_RANDOM_PROJECTS,
                lambda: self.api.get_random_projects(COUNT),
            )
        )

        self.assertEqual(len(expected), COUNT)

    def test_check_invalid_project_id(self) -> None:

        response = Response()
        response.status_code = 404

        with patch.object(requests, "get", lambda *args, **kwargs: response):
            self.assertFalse(self.api.is_project_id_valid("ABC123"))

    def test_check_valid_project_id(self) -> None:

        response = Response()
        response.status_code = 200

        with patch.object(requests, "get", lambda *args, **kwargs: response):
            self.assertTrue(self.api.is_project_id_valid(TAG_GAME_PROJECT_ID))

    def test_get_project_dependencies_ledger(self) -> None:
        expected_json: dict = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECT_DEPENDENCIES_LEDGER,
                lambda: self.api.get_project_dependencies(LEDGER_PROJECT_ID),
            )
        )

        project = ProjectDependencies.from_json(expected_json)
        parsed_back = project.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_get_project_versions(self) -> None:
        expected_json: list = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECT_VERSIONS_LITHIUM,
                lambda: self.api.get_project_versions(LITHIUM_PROJECT_ID),
            )
        )

        versions = [Version.from_json(v) for v in expected_json]
        parsed_back = [v.to_json() for v in versions]

        self.assertListEqual(expected_json, parsed_back)

    def test_get_project_versions_filtered(self) -> None:
        expected_json: list = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECT_VERSIONS_LITHIUM_FILTERED,
                lambda: self.api.get_project_versions(
                    LITHIUM_PROJECT_ID,
                    loaders=["fabric", "forge"],
                    game_versions=["1.18", "1.18.1", "1.18.2"],
                    featured=False,
                ),
            )
        )

        versions = [Version.from_json(v) for v in expected_json]
        parsed_back = [v.to_json() for v in versions]

        self.assertListEqual(expected_json, parsed_back)

    def test_get_version(self) -> None:
        expected_json: dict = json.loads(
            cached_capture(
                ResponseFiles.GET_VERSION_LITHIUM,
                lambda: self.api.get_version(),
            )
        )

        version = Version.from_json(expected_json)
        parsed_back = version.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_get_version_by_version_id(self) -> None:
        expected_json: dict = json.loads(
            cached_capture(
                ResponseFiles.GET_VERSION_BY_ID_LITHIUM,
                lambda: self.api.get_version_by_version_id(
                    project_id=LITHIUM_PROJECT_ID,
                    version_id=LITHIUM_VERSION_ID,
                ),
            )
        )

        version = Version.from_json(expected_json)
        parsed_back = version.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_get_version_by_version_number(self) -> None:
        expected_json: dict = json.loads(
            cached_capture(
                ResponseFiles.GET_VERSION_BY_NUMBER_LITHIUM,
                lambda: self.api.get_version_by_version_number(
                    project_id=LITHIUM_PROJECT_ID,
                    version_number="mc1.18-0.7.6-rc1",
                ),
            )
        )

        version = Version.from_json(expected_json)
        parsed_back = version.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_get_versions(self) -> None:
        expected_json: list = json.loads(
            cached_capture(
                ResponseFiles.GET_VERSIONS,
                lambda: self.api.get_versions(
                    [
                        LITHIUM_VERSION_ID,
                        TAG_GAME_VERSION_ID,
                    ]
                ),
            )
        )

        versions = [Version.from_json(v) for v in expected_json]
        parsed_back = [v.to_json() for v in versions]

        self.assertListEqual(expected_json, parsed_back)

    def test_get_version_from_hash_sha1(self) -> None:
        expected_json: dict = json.loads(
            cached_capture(
                ResponseFiles.GET_VERSION_FROM_HASH_SHA1,
                lambda: self.api.get_version_from_hash(
                    "522f1eac7dedabace578fc61ae1ce9290c07ca3a",
                    None,
                ),
            )
        )

        version = Version.from_json(expected_json)
        parsed_back = version.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_get_versions_from_hash_singular_sha512(self) -> None:
        expected_json: dict = json.loads(
            cached_capture(
                ResponseFiles.GET_VERSIONS_FROM_HASH_SINGULAR_SHA512,
                lambda: self.api.get_versions_from_hash(
                    "d33a3877707720fa466a0dfc4c774904b2a4e73a6d30a718ce4448b2a75b176d6ac24fdec353f5adfb3fa4551d93a38994300d5261778baaa5f1efbe045af42b",
                    None,
                ),
            )
        )

        version = Version.from_json(expected_json)
        parsed_back = version.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    # TODO: Is it possible to find a file in multiple versions?
    # def test_get_versions_from_hash_multiple_sha512(self) -> None:
    #     expected_json: list = json.loads(
    #         cached_capture(
    #             ResponseFiles.GET_VERSIONS_FROM_HASH_MULTIPLE_SHA512,
    #             lambda: self.api.get_versions_from_hash(
    #                 "",
    #                 None,
    #             ),
    #         )
    #     )

    #     versions = [Version.from_json(v) for v in expected_json]
    #     parsed_back = [v.to_json() for v in versions]

    #     self.assertListEqual(expected_json, parsed_back)


if __name__ == "__main__":
    unittest.main()
