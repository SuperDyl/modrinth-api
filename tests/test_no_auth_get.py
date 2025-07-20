import json
import unittest
from unittest.mock import patch

import requests
from requests import Response

from responses import get_response, ResponseFiles
from modrinth import ModrinthApi2
from modrinth.model import Project


class TestGetMethods(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = ModrinthApi2(user_agent="SuperDyl/modrinth-api")

    def setUp(self) -> None:
        super().setUp()

    def test_get_project_succeeds(self) -> None:
        expected = json.loads(get_response(ResponseFiles.GET_PROJECT_LEDGER))

        response = Response()
        response.status_code = 200
        response._content = str.encode(get_response(ResponseFiles.GET_PROJECT_LEDGER))

        with patch.object(requests, "get", new=lambda *x, **y: response):
            project = self.api.get_project("gvQqBUqZ")

        parsed_back = project.to_json()
        self.assertDictEqual(expected, parsed_back)


if __name__ == "__main__":
    unittest.main()
