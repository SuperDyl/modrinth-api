import json
import unittest
from unittest.mock import patch

import requests
from requests import Response

from responses import cached_capture, ResponseFiles
from modrinth import ModrinthApi2
from modrinth.model import Project, ProjectDependencies


class TestGetMethods(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = ModrinthApi2(user_agent="SuperDyl/modrinth-api")

    def setUp(self) -> None:
        super().setUp()

    def test_get_project_lithium(self) -> None:
        expected_json = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECT_LITHIUM,
                lambda: self.api.get_project("gvQqBUqZ"),
            )
        )

        project = Project.from_json(expected_json)
        parsed_back = project.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_get_project_tag_game(self) -> None:
        expected_json = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECT_TAG_GAME,
                lambda: self.api.get_project("8ZiCD9vV"),
            )
        )

        project = Project.from_json(expected_json)
        parsed_back = project.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_get_projects(self) -> None:

        expected_json: list = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECTS,
                lambda: self.api.get_projects(["gvQqBUqZ", "8ZiCD9vV"]),
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
            self.assertTrue(self.api.is_project_id_valid("8ZiCD9vV"))

    def test_get_project_dependencies_ledger(self) -> None:
        expected_json = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECT_DEPENDENCIES_LEDGER,
                lambda: self.api.get_project_dependencies("LVN9ygNV"),
            )
        )

        project = ProjectDependencies.from_json(expected_json)
        parsed_back = project.to_json()

        self.assertDictEqual(expected_json, parsed_back)


if __name__ == "__main__":
    unittest.main()
