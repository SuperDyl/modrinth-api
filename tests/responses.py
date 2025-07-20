from contextlib import contextmanager
from enum import auto, StrEnum
from functools import cache
import os
from typing import Callable, Generator
from unittest.mock import patch

import requests
from requests import Response

RESPONSE_DIR = "tests/responses"


class ResponseFiles(StrEnum):
    GET_PROJECT_LEDGER = auto()
    GET_PROJECT_TAG_GAME = auto()
    GET_PROJECTS = auto()


files: dict[str, str] = {
    ResponseFiles.GET_PROJECT_LEDGER: "get-project-ledger.json",
    ResponseFiles.GET_PROJECT_TAG_GAME: "get-project-tag-game.json",
    ResponseFiles.GET_PROJECTS: "get-projects.json",
}


@cache
def get_response(response_file: ResponseFiles) -> str:
    file_name = files[response_file]

    with open(f"{RESPONSE_DIR}/{file_name}", "r") as file:
        return file.read()


@contextmanager
def capture_request(response_file: str) -> Generator:

    _delete = requests.delete
    _get = requests.get
    _patch = requests.patch
    _post = requests.post

    def capture(__method: Callable, *args, **kwargs) -> Response:
        response: Response = __method(*args, **kwargs)

        response_path = files[response_file]

        with open(f"{RESPONSE_DIR}/{response_path}", "w") as file:
            file.write(response.content.decode())

        return response

    patch_delete = patch.object(
        requests,
        "delete",
        new=lambda *args, **kwargs: capture(_delete, *args, **kwargs),
    )
    patch_get = patch.object(
        requests,
        "get",
        new=lambda *args, **kwargs: capture(_get, *args, **kwargs),
    )
    patch_patch = patch.object(
        requests,
        "patch",
        new=lambda *args, **kwargs: capture(_patch, *args, **kwargs),
    )
    patch_post = patch.object(
        requests,
        "post",
        new=lambda *args, **kwargs: capture(_post, *args, **kwargs),
    )

    try:
        patch_delete.start()
        patch_get.start()
        patch_patch.start()
        patch_post.start()
        yield
    finally:
        patch_delete.stop()
        patch_get.stop()
        patch_patch.stop()
        patch_post.stop()


def cached_capture(response_file: ResponseFiles, request: Callable) -> str:
    if not os.path.isfile(f"{RESPONSE_DIR}/{response_file}"):
        with capture_request(response_file):
            request()
    return get_response(response_file)
