#! /usr/bin/env python3

import argparse
import configparser
from typing import Any
import requests
import dataclasses


def dprint(*args: object, **kwargs: Any) -> None:
    if CONFIG.verbosity > 0:
        print(*args, **kwargs)


@dataclasses.dataclass
class Config:
    domain: str
    api_key: str
    verbosity: int = 0


CONFIG = Config("", "", False)


def parse_config() -> Config:
    config = configparser.ConfigParser()
    config.read("cli.ini")  # TODO: think about what to do to get this

    if "frogress" not in config.sections():
        raise Exception("Missing [frogress] section in cli.ini")

    if "domain" not in config["frogress"]:
        raise Exception("Missing domain in cli.ini")

    if "api_key" not in config["frogress"]:
        raise Exception("Missing api_key in cli.ini")

    out = Config(
        domain=str(config["frogress"]["domain"]),
        api_key=str(config["frogress"]["api_key"]),
        verbosity=int(config.get("frogress", "verbosity", fallback=0)),
    )

    return out


def process_response(response: requests.Response) -> None:
    if not response.ok:
        print(f"error: HTTP status code {response.status_code}")
    print(response.text)
    if not response.ok:
        exit(1)


def create_version(args: argparse.Namespace) -> None:
    url = f"{CONFIG.domain}/projects/{args.project}/{args.slug}/"

    name = args.name or args.slug

    data = {
        "api_key": CONFIG.api_key,
        "name": name,
    }

    dprint("POST " + url)

    if args.dryrun:
        print(data)
        return
    response = requests.post(url, json=data)
    process_response(response)


def delete_version(args: argparse.Namespace) -> None:
    url = f"{CONFIG.domain}/projects/{args.project}/{args.slug}/"

    data = {"api_key": CONFIG.api_key}

    dprint("DELETE " + url)

    if args.dryrun:
        print(data)
        return

    response = requests.delete(url, json=data)
    process_response(response)


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--dryrun",
        help="Show request but do not actually send it",
        action="store_true",
    )

    subparsers = parser.add_subparsers(help="the action to perform", required=True)

    # Create
    create_parser = subparsers.add_parser("create", help="create a new db object")
    create_subparsers = create_parser.add_subparsers(
        help="the db layer on which to operate", required=True
    )
    create_version_parser = create_subparsers.add_parser(
        "version",
        help="create a new version",
    )
    create_version_parser.add_argument(
        "project", help="the project for which to create the version"
    )
    create_version_parser.add_argument("slug", help="the slug for the version")
    create_version_parser.add_argument("--name", help="the name for the version")
    create_version_parser.set_defaults(func=create_version)

    # Delete
    delete_parser = subparsers.add_parser("delete", help="delete a db object")
    delete_subparsers = delete_parser.add_subparsers(
        help="the db layer on which to operate", required=True
    )
    delete_version_parser = delete_subparsers.add_parser(
        "version",
        help="delete a version",
    )
    delete_version_parser.add_argument(
        "project", help="the project for which to delete the version"
    )
    delete_version_parser.add_argument("slug", help="the slug for the version")
    delete_version_parser.set_defaults(func=delete_version)

    args = parser.parse_args()

    global CONFIG
    CONFIG = parse_config()

    args.func(args)


if __name__ == "__main__":
    main()
