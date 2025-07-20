import json
import unittest

from modrinth.model import Project


class TestParse(unittest.TestCase):

    def test_project_parse_ledger(self) -> None:
        expected_json = json.loads(
            """
            {
                "client_side": "optional",
                "server_side": "optional",
                "game_versions": ["1.21", "1.21.8"],
                "id": "gvQqBUqZ",
                "slug": "lithium",
                "project_type": "mod",
                "team": "peSx5UYg",
                "organization": "LjcZDkRW",
                "title": "Lithium",
                "description": "Some description text!",
                "body": "This is a really long body text.\\n",
                "body_url": null,
                "published": "2021-01-03T00:56:52.292581Z",
                "updated": "2025-07-17T18:40:04.965338Z",
                "approved": "2021-01-03T00:56:52.292581Z",
                "queued": null,
                "status": "approved",
                "requested_status": null,
                "moderator_message": null,
                "license": {
                    "id": "LGPL-3.0-only",
                    "name": "GNU Lesser General Public License v3.0 only",
                    "url": null
                },
                "downloads": 36052308,
                "followers": 15914,
                "categories": [
                    "optimization"
                ],
                "additional_categories": [],
                "loaders": ["fabric", "neoforge", "quilt"],
                "versions": ["EhG1mQzx", "qV99i9jE"],
                "icon_url": "https://cdn.modrinth.com/data/gvQqBUqZ/bcc8686c13af0143adf4285d741256af824f70b7_96.webp",
                "issues_url": "https://github.com/caffeinemc/lithium-fabric/issues",
                "source_url": "https://github.com/caffeinemc/lithium-fabric",
                "wiki_url": null,
                "discord_url": "https://caffeinemc.net/discord",
                "donation_urls": [
                    {
                        "id": "patreon",
                        "platform": "Patreon",
                        "url": "https://www.patreon.com/2No2Name"
                    }
                ],
                "gallery": [],
                "color": 15395571,
                "thread_id": "gvQqBUqZ",
                "monetization_status": "monetized"
            }
            """
        )

        project = Project.from_json(expected_json)
        parsed_back = project.to_json()

        self.assertDictEqual(expected_json, parsed_back)

    def test_project_parse_tag_game(self) -> None:
        expected_json = json.loads(
            """
            {
                "client_side": "optional",
                "server_side": "required",
                "game_versions": ["1.21", "1.21.7"],
                "id": "8ZiCD9vV",
                "slug": "tag-game",
                "project_type": "mod",
                "team": "MwM4aDPK",
                "organization": null,
                "title": "Tag Game",
                "description": "Description text!",
                "body": "Why is body text always so long?\\n",
                "body_url": null,
                "published": "2024-07-27T05:33:08.434012Z",
                "updated": "2025-07-05T17:48:25.210584Z",
                "approved": "2024-07-28T04:07:29.012993Z",
                "queued": "2024-07-27T06:03:53.503384Z",
                "status": "approved",
                "requested_status": "approved",
                "moderator_message": null,
                "license": {
                    "id": "GPL-3.0-only",
                    "name": "GNU General Public License v3.0 only",
                    "url": null
                },
                "downloads": 361,
                "followers": 5,
                "categories": ["minigame"],
                "additional_categories": [],
                "loaders": ["datapack"],
                "versions": ["hGz3eq2G", "oaj6YGgc"],
                "icon_url": "https://cdn.modrinth.com/data/8ZiCD9vV/6f5b8e2fd91779c34ec7ba48cbdcb072d5162a93_96.webp",
                "issues_url": "https://github.com/SuperDyl/tag-game/issues",
                "source_url": "https://github.com/SuperDyl/tag-game",
                "wiki_url": null,
                "discord_url": null,
                "donation_urls": [],
                "gallery": [
                    {
                        "url": "https://cdn.modrinth.com/data/8ZiCD9vV/images/26f1bff01ef2ef2cd6d543dbd21d4c1e1f63b0ee_350.webp",
                        "raw_url": "https://cdn.modrinth.com/data/8ZiCD9vV/images/ab66f6626f41efa1e17c6afe00ffb562f617243d.png",
                        "featured": true,
                        "title": "Tagger surprise!",
                        "description": "Tagger sneaking up on a distracted player",
                        "created": "2024-07-27T05:34:49.633577Z",
                        "ordering": 0
                    },
                    {
                        "url": "https://cdn.modrinth.com/data/8ZiCD9vV/images/8f4a6800e9db52e9e963da63fa4d3d437fb3e73c.png",
                        "raw_url": "https://cdn.modrinth.com/data/8ZiCD9vV/images/8f4a6800e9db52e9e963da63fa4d3d437fb3e73c.png",
                        "featured": false,
                        "title": "The Tag",
                        "description": "The tag used by the taggers",
                        "created": "2024-07-27T06:12:06.178055Z",
                        "ordering": 1
                    }
                ],
                "color": 14529658,
                "thread_id": "xQxDvuIK",
                "monetization_status": "monetized"
            }
            """
        )

        project = Project.from_json(expected_json)
        parsed_back = project.to_json()

        self.assertDictEqual(expected_json, parsed_back)


if __name__ == "__main__":
    unittest.main()
