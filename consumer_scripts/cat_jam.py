#! /usr/bin/env python3
import argparse
import requests
from typing import List

BASE_URL = "http://127.0.0.1:8000/projects"


def make_slug_url(args: argparse.Namespace) -> str:
    if BASE_URL:
        url_components = [BASE_URL]
    else:
        url_components = [args.base_url]

    for arg in [args.project, args.version]:
        if arg != "":
            url_components.append(arg)

    return str.join("/", url_components)


def make_url_options(args: argparse.Namespace) -> str:
    options: List[str] = []

    ret = str.join("&", options)
    if ret != "":
        return "?" + ret
    else:
        return ""


def make_url(args: argparse.Namespace) -> str:
    url = make_slug_url(args)
    url += make_url_options(args)
    return url


categories = [
    # "default",
    # "boot",
    # "code",
    # "overlays",
    "assets",
    "archives",
    "audio",
    "interface",
    "misc",
    "objects",
    "scenes",
    "text",
]


def main() -> None:
    description = "Make categories."
    epilog = ""

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # parser.add_argument("base_url", help="")
    parser.add_argument("-p", "--project", help="", default="")
    parser.add_argument("-v", "--version", help="", default="")

    args = parser.parse_args()
    url = make_url(args)
    url += "/"
    url += "?format=json"
    print(url)

    request_data = {}
    for cat in categories:
        request_data[cat] = cat.capitalize()

    request_json = {"api_key": "2", "categories": request_data}

    print(request_json)

    with requests.post(url, json=request_json) as r:
        print(r.status_code)
        print(r.text)


if __name__ == "__main__":
    main()
