import json
import unittest
from unittest.mock import patch

from responses import cached_capture, ResponseFiles
from modrinth.model import Project, ProjectDependencies
from modrinth import ModrinthApi2


class TestParse(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.api = ModrinthApi2(user_agent="SuperDyl/modrinth-api")

    def test_project_parse_lithium(self) -> None:
        expected_json = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECT_LITHIUM,
                lambda: self.api.get_project("gvQqBUqZ"),
            )
        )

        project = Project.from_json(expected_json)
        parsed_back = project.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_project_parse_tag_game(self) -> None:
        expected_json = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECT_TAG_GAME,
                lambda: self.api.get_project("8ZiCD9vV"),
            )
        )

        project = Project.from_json(expected_json)
        parsed_back = project.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_projects_parse(self) -> None:

        expected_json: list = json.loads(
            cached_capture(
                ResponseFiles.GET_PROJECTS,
                lambda: self.api.get_projects(["gvQqBUqZ", "8ZiCD9vV"]),
            )
        )

        projects = [Project.from_json(p) for p in expected_json]
        parsed_back = [p.to_json() for p in projects]

        self.assertListEqual(expected_json, parsed_back)

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
