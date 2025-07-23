import json
import unittest
from unittest.mock import patch

import requests
from requests import Response

from responses import cached_capture, ResponseFiles
from modrinth import ModrinthApi2
from modrinth.model import Project


class TestGetMethods(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = ModrinthApi2(user_agent="SuperDyl/modrinth-api")

    def setUp(self) -> None:
        super().setUp()

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


if __name__ == "__main__":
    unittest.main()
