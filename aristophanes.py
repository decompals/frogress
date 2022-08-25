#! /usr/bin/env python3
import argparse
import collections
import csv
from io import BytesIO, FileIO, StringIO
import json
import subprocess
import requests

BASE_URL = "http://127.0.0.1:8000/data"


def make_slug_url(args: argparse.Namespace) -> str:
    if BASE_URL:
        url_components = [BASE_URL]
    else:
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
    "code_matching",
    "code_total",
    "boot/matching",
    "boot/total",
    "code/matching",
    "code/total",
    "overlays/matching",
    "overlays/total",
    "asm",
    "nonmatching_functions_count",
    "assets_identified",
    "assets_total",
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
extra_fields = [
    "csv_version",
    "timestamp",
    "git_hash",
    "code_decompiled",
    "code_total",
    "boot/decompiled",
    "boot/total",
    "code/decompiled",
    "code/total",
    "overlays/decompiled",
    "overlays/total",
    "asm",
    "nonmatching_functions_count",
    "assets_debinarised",
    "assets_total",
    "archives/debinarised",
    "archives/total",
    "audio/debinarised",
    "audio/total",
    "interface/debinarised",
    "interface/total",
    "misc/debinarised",
    "misc/total",
    "objects/debinarised",
    "objects/total",
    "scenes/debinarised",
    "scenes/total",
    "text/debinarised",
    "text/total",
]
extra_filter = []

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


def double_csv_to_json(input: FileIO, extra_input: FileIO, output):
    csv_reader = csv.DictReader(input, fields)
    extra_csv_reader = csv.DictReader(extra_input, extra_fields)

    for row in csv_reader:
        new_row = {}
        for field in row:
            measure = str.split(field, "/")
            category = measure[0]
            if category in categories:
                if category not in new_row:
                    new_row[category] = {}
                new_row[category][measure[1]] = int(row.get(field))
            elif category in ["csv_version"]:
                continue
            elif category in ["git_hash"]:
                new_row[category] = row.get(field)
            elif category in ["timestamp"]:
                new_row[category] = int(row.get(field))
            else:
                if "default" not in new_row:
                    new_row["default"] = {}
                new_row["default"][category] = int(row.get(field))

        if extra_input:
            # For brevity this makes assumptions about the categories being present in the primary
            extra_row = extra_csv_reader.__next__()
            for field in extra_row:
                measure = str.split(field, "/")
                category = measure[0]
                if category in categories:
                    if category not in new_row:
                        new_row[category] = {}
                    if measure[1] not in new_row[category]:
                        new_row[category][measure[1]] = int(extra_row.get(field))
                elif category in ["csv_version", "timestamp", "git_hash"]:
                    continue
                #     new_row[category] = row.get(field)
                else:
                    if "default" not in new_row:
                        new_row["default"] = {}
                    if category not in new_row["default"]:
                        new_row["default"][category] = int(extra_row.get(field))

        output.append(new_row)

    # filter_fields = [
    #     "timestamp",
    #     "git_hash",
    #     "matching_bytes",
    #     "total_bytes",
    # ]
    # output = dict_filter(output, filter_fields)
    # print(output)


# def confuse_dicts(input, output: dict):
#     mid = []
#     for row in input:
#         newRow = {}
#         for category in categories:
#             newRow[category] = {}
#             for field in ["timestamp", "git_hash"]:
#                 newRow[category][field] = row.get(field)
#             for field in row.get(category):
#                 newRow[category][field] = row.get(category).get(field)
#         mid.append(newRow)

#     for category in categories:
#         output[category] = []
#         for row in mid:
#             output[category].append(row.get(category))


# def csv_to_category_json(args: argparse.Namespace, input):
#     ...


test_csv_input = """
2,1615435438,e788bfecbfb10afd4182332db99bb562ea75b1de,103860,4747584,31572,86064,58624,1065936,13664,3595584,4597948,49,0,40816656,0,434608,0,6029280,0,801520,0,3900928,0,13518304,0,15695712,0,436304
2,1660614141,bb96e47f8df9fa42e2120b7acda90432bacfde39,3143604,4747584,78172,86064,507828,1065936,2557604,3595584,1613196,31,3592092,40816656,0,434608,0,6029280,80976,801520,328616,3900928,3146908,13518304,35592,15695712,0,436304
"""

test_extra_csv_input = """
2,1615435438,e788bfecbfb10afd4182332db99bb562ea75b1de,120152,4747584,36352,86064,70136,1065936,13664,3595584,4582152,0,0,40816656,0,434608,0,6029280,0,801520,0,3900928,0,13518304,0,15695712,0,436304
2,1660614141,bb96e47f8df9fa42e2120b7acda90432bacfde39,3177404,4747584,78544,86064,522780,1065936,2576080,3595584,1579396,0,29774016,40816656,0,434608,0,6029280,80976,801520,479024,3900928,13518304,13518304,15695712,15695712,0,436304
"""


def main() -> None:
    description = "Talk to frogress."
    epilog = ""

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # parser.add_argument("base_url", help="")
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
    url = make_url(args)
    url += "/"
    url += "?format=json"
    print(url)

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

    # with StringIO(test_csv_input) as f:
    #     output = []
    #     csv_to_json(f, output)
    #     # for entry in output:
    #     #     string = json.dumps(entry, indent=4)
    #     #     print(string)

    #     # confused_output = []
    #     # confuse_dicts(output, confused_output)
    #     # for entry in confused_output:
    #     #     string = json.dumps(entry, indent=4)
    #     #     print(string)
    #     confused_output = {}
    #     confuse_dicts(output, confused_output)
    #     string = json.dumps(confused_output, indent=4)
    #     print(string)

    with StringIO(test_csv_input) as f:
        with StringIO(test_extra_csv_input) as g:
            output = []
            double_csv_to_json(f, g, output)
            request_body = {"api_key": "2", "data": output}
            string = json.dumps(request_body, indent=4)
            print(request_body)
            # for entry in output:
            #     string = json.dumps(entry, indent=4)
            #     print(string)

            # confused_output = []
            # confuse_dicts(output, confused_output)
            # for entry in confused_output:
            #     string = json.dumps(entry, indent=4)
            #     print(string)
            # confused_output = {}
            # confuse_dicts(output, confused_output)
            # string = json.dumps(confused_output, indent=4)
            # print(string)

    with requests.post(url, json=request_body) as r:
        print(r.status_code)
        print(r.text)


if __name__ == "__main__":
    main()
