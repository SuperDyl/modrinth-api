from contextlib import contextmanager
from enum import StrEnum
from functools import cache
import os
from typing import Callable, Generator
from unittest.mock import patch

import requests
from requests import Response

RESPONSE_DIR = "tests/responses"


class ResponseFiles(StrEnum):
    GET_PROJECT_LITHIUM = "get-project-lithium.json"
    GET_PROJECT_TAG_GAME = "get-project-tag-game.json"
    GET_PROJECTS = "get-projects.json"
    GET_RANDOM_PROJECTS = "get-random-projects.json"
    GET_PROJECT_DEPENDENCIES_LEDGER = "get-project-dependencies-ledger.json"
    GET_PROJECT_VERSIONS_LITHIUM = "get-project-versions-lithium.json"
    GET_PROJECT_VERSIONS_LITHIUM_FILTERED = "get-project-versions-lithium-filtered.json"
    GET_VERSION_LITHIUM = "get-version-lithium.json"
    GET_VERSION_BY_ID_LITHIUM = "get-version-by-id-lithium.json"
    GET_VERSION_BY_NUMBER_LITHIUM = "get-version-by-number-lithium.json"
    GET_VERSIONS = "get-versions.json"
    GET_VERSION_FROM_HASH_SHA1 = "get-version-from-hash-sha1.json"
    GET_VERSIONS_FROM_HASH_SINGULAR_SHA512 = (
        "get-versions-from-hash-singular-sha512.json"
    )
    GET_VERSIONS_FROM_HASH_MULTIPLE_SHA512 = (
        "get-versions-from-hash-multiple-sha512.json"
    )
    GET_LATEST_VERSION = "get-latest-version.json"
    GET_VERSIONS_FROM_HASHES_SHA1 = "get-versions-from-hashes-sha1.json"
    GET_LATEST_VERSIONS = "get-latest-versions.json"
    GET_USER = "get-user.json"


used_files: set[ResponseFiles] = set()


@cache
def get_response(response_file: ResponseFiles) -> str:

    if response_file in used_files:
        raise ValueError(f"Reused response file '{response_file}'")
    used_files.add(response_file)

    with open(f"{RESPONSE_DIR}/{response_file}", "r") as file:
        return file.read()


@contextmanager
def capture_request(response_file: str) -> Generator:

    _delete = requests.delete
    _get = requests.get
    _patch = requests.patch
    _post = requests.post

    def capture(__method: Callable, *args, **kwargs) -> Response:
        response: Response = __method(*args, **kwargs)

        with open(f"{RESPONSE_DIR}/{response_file}", "w") as file:
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

    if not os.path.exists(f"{RESPONSE_DIR}/{response_file}"):
        with capture_request(response_file):
            request()
    return get_response(response_file)
