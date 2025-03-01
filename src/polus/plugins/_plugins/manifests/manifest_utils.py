"""Utilities for manifest parsing and validation."""
import json
import logging
import pathlib
import typing
from urllib.parse import urlparse

import github
import requests
from pydantic import ValidationError, errors
from tqdm import tqdm

from polus.plugins._plugins.models import ComputeSchema, WIPPPluginManifest
from polus.plugins._plugins.utils import cast_version

logger = logging.getLogger("polus.plugins")

# Fields that must be in a plugin manifest
REQUIRED_FIELDS = [
    "name",
    "version",
    "description",
    "author",
    "containerId",
    "inputs",
    "outputs",
    "ui",
]


class InvalidManifest(Exception):
    """Raised when manifest has validation errors."""


def is_valid_manifest(plugin: dict) -> bool:
    """Validate basic attributes of a plugin manifest.

    Args:
        plugin: A parsed plugin json file

    Returns:
        True if the plugin has the minimal json fields
    """
    fields = list(plugin.keys())

    try:
        for field in REQUIRED_FIELDS:
            assert field in fields, f"Missing json field, {field}, in plugin manifest."
    except AssertionError:
        return False

    return True


def _load_manifest(m: typing.Union[str, dict, pathlib.Path]) -> dict:
    """Convert to dictionary if pathlib.Path or str."""
    if isinstance(m, dict):
        return m
    elif isinstance(m, pathlib.Path):
        assert (
            m.suffix == ".json"
        ), "Plugin manifest must be a json file with .json extension."

        with open(m) as fr:
            manifest = json.load(fr)

    elif isinstance(m, str):
        if urlparse(m).netloc == "":
            manifest = json.loads(m)
        else:
            manifest = requests.get(m).json()
    else:
        raise ValueError("invalid manifest")
    return manifest


def validate_manifest(
    manifest: typing.Union[str, dict, pathlib.Path]
) -> typing.Union[WIPPPluginManifest, ComputeSchema]:
    """Validate a plugin manifest against schema."""
    manifest = _load_manifest(manifest)
    manifest["version"] = cast_version(
        manifest["version"]
    )  # cast version to semver object
    if "name" in manifest:
        name = manifest["name"]
    else:
        raise InvalidManifest(f"{manifest} has no value for name")

    if "pluginHardwareRequirements" in manifest:
        # Parse the manifest
        try:
            plugin = ComputeSchema(**manifest)
        except ValidationError as e:
            raise InvalidManifest(f"{name} does not conform to schema") from e
        except BaseException as e:
            raise e
    else:
        # Parse the manifest
        try:
            plugin = WIPPPluginManifest(**manifest)
        except ValidationError as e:
            raise InvalidManifest(
                f"{manifest['name']} does not conform to schema"
            ) from e
        except BaseException as e:
            raise e
    return plugin


def _scrape_manifests(
    repo: typing.Union[str, github.Repository.Repository],  # type: ignore
    gh: github.Github,
    min_depth: int = 1,
    max_depth: typing.Optional[int] = None,
    return_invalid: bool = False,
) -> typing.Union[list, typing.Tuple[list, list]]:
    if max_depth is None:
        max_depth = min_depth
        min_depth = 0

    assert max_depth >= min_depth, "max_depth is smaller than min_depth"

    if isinstance(repo, str):
        repo = gh.get_repo(repo)

    contents = list(repo.get_contents(""))  # type: ignore
    next_contents = []
    valid_manifests = []
    invalid_manifests = []

    for d in range(0, max_depth):
        for content in tqdm(contents, desc=f"{repo.full_name}: {d}"):
            if content.type == "dir":
                next_contents.extend(repo.get_contents(content.path))  # type: ignore
            elif content.name.endswith(".json"):
                if d >= min_depth:
                    manifest = json.loads(content.decoded_content)
                    if is_valid_manifest(manifest):
                        valid_manifests.append(manifest)
                    else:
                        invalid_manifests.append(manifest)

        contents = next_contents.copy()
        next_contents = []

    if return_invalid:
        return valid_manifests, invalid_manifests
    else:
        return valid_manifests


def _error_log(val_err, manifest, fct):
    report = []

    for err in val_err.args[0]:
        if isinstance(err, list):
            err = err[0]

        if isinstance(err, AssertionError):
            report.append(
                "The plugin ({}) failed an assertion check: {}".format(
                    manifest["name"], err.args[0]
                )
            )
            logger.critical(f"{fct}: {report[-1]}")
        elif isinstance(err.exc, errors.MissingError):
            report.append(
                "The plugin ({}) is missing fields: {}".format(
                    manifest["name"], err.loc_tuple()
                )
            )
            logger.critical(f"{fct}: {report[-1]}")
        elif errors.ExtraError:
            if err.loc_tuple()[0] in ["inputs", "outputs", "ui"]:
                report.append(
                    "The plugin ({}) had unexpected values in the {} ({}): {}".format(
                        manifest["name"],
                        err.loc_tuple()[0],
                        manifest[err.loc_tuple()[0]][err.loc_tuple()[1]]["name"],
                        err.exc.args[0][0].loc_tuple(),
                    )
                )
            else:
                report.append(
                    "The plugin ({}) had an error: {}".format(
                        manifest["name"], err.exc.args[0][0]
                    )
                )
            logger.critical(f"{fct}: {report[-1]}")
        else:
            logger.warning(
                "{}: Uncaught manifest Error in ({}): {}".format(
                    fct,
                    manifest["name"],
                    str(val_err).replace("\n", ", ").replace("  ", " "),
                )
            )
