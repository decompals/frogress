# Guide on how to monitor decomp progress using frogress

## Overview

This guide will provide a flow for how to use frogress for your project.

```mermaid
sequenceDiagram
    autonumber
    actor Contributor as Project contributor
    actor Monitor as Spectator
    Contributor->>+CI: Trigger
    CI->>CI: Build
    CI->>CI: Calculate progress
    CI->>-frogress: Upload progress
    Note over CI,frogress: POST /data/project:/version:/
    Monitor->>frogress: Fetch progress
    Note over Monitor,frogress: GET /data/project:/version:/?mode=all
    frogress->>Monitor: Return progress
    Monitor->>Monitor: Render progress
```

*CI: Continuous Integration services including GitHub Actions, Gitlab pipelines, Travis CI and Jenkins.*

## Steps

1. Contact frogress admin (Ethan) to add your project to the database and obtain an api_key

2. Create schema with `cli.py`

    2.1 Edit `cli.ini`
    
    ```ini
    [frogress]
    domain = https://progress.deco.mp
    api_key = api_key
    ```

    2.2 Create version

    ```bash
    # Usage
    ./cli.py create version -h
    # Example
    ./cli.py create version fireemblem8 us
    ```
    
    2.3 Create category

    ```bash
    # Usage
    ./cli.py create category -h
    # Example
    ./cli.py create category fireemblem8 us default
    ```

3. Configure CI to upload data on build

    3.1 API
    
    ```
    POST https://progress.deco.mp/data/project:/version:/
    ```

    ```python
    {
        "api_key": "",
        "entries": [
            "git_hash": "",
            "timestamp": "",
            "categories": {
                "default": {
                    # metrics
                }
            }
        ]
    }
    ```

    3.2 Example

    https://github.com/FireEmblemUniverse/fireemblem8u/pull/307

4. Supplement historical data (optional, one-time)

    Calculate progress for historical commits and upload it to frogress for the purpose of visualizing and tracking historical data

    [Example](https://github.com/laqieer/fireemblem8u/blob/master/.github/workflows/supplement-progress.yml)

5. Fetch project data

    5.1 API

    There are 3 "modes" for returning results: `all`, `latest`, and `shield`. The first two are pretty self explanatory, and `shield` can be used to generate badges for your repo's README.md (shields.io).

    ```
    GET https://progress.deco.mp/data/project:/version:/?mode=all
    ```
    ```
    GET https://progress.deco.mp/data/project:/version:/?mode=latest
    ```
    Note that the category and measure are required for mode `shield`.
    ```
    GET https://progress.deco.mp/data/project:/version:/category:/?mode=shield&measure=MEASURE
    ```

    **Note:** Specifying a category in the request URL is optional for `all` and `latest` modes. If the category is not specified, results from all categories will be returned. However, for `shield`, it is necessary to specify the category and measure in the request url, as shown above.

    `all` example:

    `https://progress.deco.mp/data/fireemblem8/us/?mode=all`

    `shield` example:

    `https://progress.deco.mp/data/dukezh/us/default/?mode=shield&measure=bytes`

    5.2 Build a website

    Build a website to display your progress!

    You can use the "latest" mode to retrieve just the latest datapoint or render full graphs using a library such as [uPlot](https://github.com/leeoniya/uPlot) or [Chart.js](https://www.chartjs.org)

      - https://pikmin.dev
      - https://axiodl.com
      - https://sotn.xee.dev/
      - https://laqieer.github.io/fe-decomp-portal
      - https://angheloalf.github.io/drmario64
      - https://angheloalf.github.io/puzzleleague64
