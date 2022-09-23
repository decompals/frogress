#! /usr/bin/env python3

import argparse
import configparser
import requests


def parse_config() -> configparser.SectionProxy:
    config = configparser.ConfigParser()
    config.read("cli.ini")

    if "frogress" not in config.sections():
        raise Exception("Missing [frogress] section in cli.ini")

    if "domain" not in config["frogress"]:
        raise Exception("Missing domain in cli.ini")

    if "api_key" not in config["frogress"]:
        raise Exception("Missing api_key in cli.ini")

    if "debug" not in config["frogress"]:
        config["frogress"]["debug"] = "false"

    return config["frogress"]


def debug(msg: str) -> None:
    if dbg:
        print(msg)


def create_version(args: argparse.Namespace) -> None:
    url = f"{domain}/projects/{args.project}/{args.slug}/"

    name = args.name or args.slug

    data = {
        "api_key": api_key,
        "name": name,
    }

    debug("POST " + url)

    response = requests.post(url, json=data)
    print(response.text)


def delete_version(args: argparse.Namespace) -> None:
    url = f"{domain}/projects/{args.project}/{args.slug}/"

    data = {"api_key": api_key}

    debug("DELETE " + url)

    response = requests.delete(url, json=data)
    print(response.text)


def main() -> None:
    parser = argparse.ArgumentParser()

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
    args.func(args)


config = parse_config()

dbg = bool(config["debug"])
domain = config["domain"]
api_key = config["api_key"]

if __name__ == "__main__":
    main()
