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


def create_category(args: argparse.Namespace) -> None:
    url = f"{domain}/projects/{args.project}/{args.version}/{args.slug}/"

    name = args.name or args.slug

    data = {
        "api_key": api_key,
        "name": name,
    }

    debug("POST " + url)

    response = requests.post(url, json=data)
    print(response.text)


def delete_category(args: argparse.Namespace) -> None:
    url = f"{domain}/projects/{args.project}/{args.version}/{args.slug}/"

    data = {"api_key": api_key}

    debug("DELETE " + url)

    response = requests.delete(url, json=data)
    print(response.text)


def prune_entries(args: argparse.Namespace) -> None:
    # Get entries

    url = f"{domain}/data/{args.project}/{args.version}?mode=all"

    debug("GET " + url)

    response = requests.get(url)
    print(response.text)

    categories = response.json().get(args.project, {}).get(args.version, {})

    if len(categories) == 0:
        return
    
    # Filter entries
    
    filtered = {}
    
    for category, entries in categories.items():
        if len(entries) == 0:
            continue
        for entry in entries:
            if entry["git_hash"] not in filtered:
                filtered[entry["git_hash"]] = {
                    "git_hash": entry["git_hash"],
                    "timestamp": entry["timestamp"],
                    "categories": {},
                }
            if category not in filtered[entry["git_hash"]]["categories"]:
                filtered[entry["git_hash"]]["categories"][category] = entry["measures"]
            else:
                for measure, value in entry["measures"].items():
                    if measure not in filtered[entry["git_hash"]]["categories"][category]:
                        filtered[entry["git_hash"]]["categories"][category][measure] = value

    entries = list(filtered.values())

    print(entries)

    # Clear entries

    for category in categories.keys():
        # Delete categories

        url = f"{domain}/projects/{args.project}/{args.version}/{category}/"

        data = {"api_key": api_key}

        debug("DELETE " + url)

        response = requests.delete(url, json=data)
        print(response.text)

        # Recreate categories

        data["name"] = category

        debug("POST " + url)

        response = requests.post(url, json=data)
        print(response.text)

    # Upload entries

    url = f"{domain}/data/{args.project}/{args.version}/"

    data = {"api_key": api_key, "entries": entries}

    debug("POST " + url)

    response = requests.post(url, json=data)
    print(response.status_code, response.text)

    # Check entries

    url = f"{domain}/data/{args.project}/{args.version}?mode=all"

    debug("GET " + url)

    response = requests.get(url)
    print(response.text)


def main() -> None:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help="the action to perform", required=True)

    # Create
    create_parser = subparsers.add_parser("create", help="create a new db object")
    create_subparsers = create_parser.add_subparsers(
        help="the db layer on which to operate", required=True
    )

    # Create version
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

    # Create category
    create_category_parser = create_subparsers.add_parser(
        "category",
        help="create a new category",
    )
    create_category_parser.add_argument(
        "project", help="the project for which to create the version"
    )
    create_category_parser.add_argument("version", help="the slug for the version")
    create_category_parser.add_argument("slug", help="the slug for the category")
    create_category_parser.add_argument("--name", help="the name for the category")
    create_category_parser.set_defaults(func=create_category)

    # Delete
    delete_parser = subparsers.add_parser("delete", help="delete a db object")
    delete_subparsers = delete_parser.add_subparsers(
        help="the db layer on which to operate", required=True
    )

    # Delete version
    delete_version_parser = delete_subparsers.add_parser(
        "version",
        help="delete a version",
    )
    delete_version_parser.add_argument(
        "project", help="the project for which to delete the version"
    )
    delete_version_parser.add_argument("slug", help="the slug for the version")
    delete_version_parser.set_defaults(func=delete_version)

    # Delete category
    delete_category_parser = delete_subparsers.add_parser(
        "category",
        help="delete a category",
    )
    delete_category_parser.add_argument(
        "project", help="the project for which to delete the version"
    )
    delete_category_parser.add_argument("version", help="the slug for the version")
    delete_category_parser.add_argument("slug", help="the slug for the category")
    delete_category_parser.set_defaults(func=delete_category)

    # Prune entries
    prune_parser = subparsers.add_parser(
        "prune",
        help="prune duplicate entries",
    )
    prune_parser.add_argument(
        "project", help="the project for which to prune the entries"
    )
    prune_parser.add_argument("version", help="the slug for the version")
    prune_parser.set_defaults(func=prune_entries)

    args = parser.parse_args()
    args.func(args)


config = parse_config()

dbg = bool(config["debug"])
domain = config["domain"]
api_key = config["api_key"]

if __name__ == "__main__":
    main()
