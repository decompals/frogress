#! /usr/bin/env python3
import argparse
import collections
import csv
from io import BytesIO, FileIO, StringIO
import json
import subprocess
import requests


def make_slug_url(args: argparse.Namespace) -> str:
    url_components = [args.base_url]
    for arg in [args.project, args.version, args.category]:
        if arg != "":
            url_components.append(arg)

    return str.join("/", url_components)


def make_url_options(args: argparse.Namespace) -> str:
    options = []

    if args.all:
        options += "all=true"

    ret = str.join("&", options)
    if ret != "":
        return "?" + ret
    else:
        return ""


def make_url(args: argparse.Namespace) -> str:
    url = make_slug_url(args)
    url += make_url_options(args)
    return url


def dict_filter(input: list, *keys) -> dict:
    output: list = []
    for d in input:
        output.append(dict((k, d[k]) for k in keys))
    return output


fields = [
    "csv_version",
    "timestamp",
    "git_hash",
    "default/matching",
    "default/total",
    "boot/matching",
    "boot/total",
    "code/matching",
    "code/total",
    "overlays/matching",
    "overlays/total",
    "asm",
    "nonmatching_functions_count",
    "assets/identified",
    "assets/total",
    "archives/identified",
    "archives/total",
    "audio/identified",
    "audio/total",
    "interface/identified",
    "interface/total",
    "misc/identified",
    "misc/total",
    "objects/identified",
    "objects/total",
    "scenes/identified",
    "scenes/total",
    "text/identified",
    "text/total",
]
categories = [
    "default",
    "boot",
    "code",
    "overlays",
    "assets",
    "archives",
    "audio",
    "interface",
    "misc",
    "objects",
    "scenes",
    "text",
]


def csv_to_json(input: FileIO, output):
    csvReader = csv.DictReader(input, fields)
    for row in csvReader:
        newRow = {}
        for field in row:
            measure = str.split(field, "/")
            category = measure[0]
            if category in categories:
                if category not in newRow:
                    newRow[category] = {}
                newRow[category][measure[1]] = row.get(field)
            elif category in ["csv_version", "timestamp", "git_hash"]:
                newRow[category] = row.get(field)
            else:
                if "default" not in newRow:
                    newRow["default"] = {}
                newRow["default"][category] = row.get(field)

        output.append(newRow)

    # filter_fields = [
    #     "timestamp",
    #     "git_hash",
    #     "matching_bytes",
    #     "total_bytes",
    # ]
    # output = dict_filter(output, filter_fields)
    # print(output)


def confuse_dicts(input, output: dict):
    mid = []
    for row in input:
        newRow = {}
        for category in categories:
            newRow[category] = {}
            for field in ["timestamp", "git_hash"]:
                newRow[category][field] = row.get(field)
            for field in row.get(category):
                newRow[category][field] = row.get(category).get(field)
        mid.append(newRow)

    for category in categories:
        output[category] = []
        for row in mid:
            output[category].append(row.get(category))


def csv_to_category_json(args: argparse.Namespace, input):
    ...


test_csv_input = """
2,1660589498,78684187fefadb54ef551f189f159f2f8364e5e3,3133560,4747584,78172,86064,504556,1065936,2550832,3595584,1623240,40,3592092,40816656,0,434608,0,6029280,80976,801520,328616,3900928,3146908,13518304,35592,15695712,0,436304
2,1660589742,c5254084c26c749db81b721fdaf67f05a5da6095,3143604,4747584,78172,86064,507828,1065936,2557604,3595584,1613196,31,3592092,40816656,0,434608,0,6029280,80976,801520,328616,3900928,3146908,13518304,35592,15695712,0,436304
"""


def main() -> None:
    description = "Talk to frogress."
    epilog = ""

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("base_url", help="")
    parser.add_argument("-p", "--project", help="", default="")
    parser.add_argument("-v", "--version", help="", default="")
    parser.add_argument("-c", "--category", help="", default="")
    parser.add_argument(
        "-a",
        "--all",
        help="fetch history instead of just most recent entry",
        action="store_true",
    )

    args = parser.parse_args()

    # url = make_url(args)
    # url += "?format=json"
    # print(url)

    # with requests.get(url) as r:
    #     print(r.status_code)
    #     if r.status_code == 200:
    #         result = r.json()
    #         try:
    #             string = json.dumps(result, sort_keys=True, indent=4)
    #             print(string)
    #         except:
    #             print("No idea what this package thought was wrong")

    # result = subprocess.run(["curl", "-s", url], stdout=subprocess.PIPE)
    # print(result.stdout)
    # print(result)
    # try:
    #     data = json.loads(result.stdout.decode())
    #     string = json.dumps(data, sort_keys=True, indent=4)
    #     print(string)
    # except:
    #     print("Malformed JSON returned, is this URL not implemented yet?")
    with StringIO(test_csv_input) as f:
        output = []
        csv_to_json(f, output)
        # for entry in output:
        #     string = json.dumps(entry, indent=4)
        #     print(string)

        # confused_output = []
        # confuse_dicts(output, confused_output)
        # for entry in confused_output:
        #     string = json.dumps(entry, indent=4)
        #     print(string)
        confused_output = {}
        confuse_dicts(output, confused_output)
        string = json.dumps(confused_output, indent=4)
        print(string)


if __name__ == "__main__":
    main()
