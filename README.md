# Frogress

An API for storing/retrieving decompilation progress

## Development
For those interested in contributing to frogress's development, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## Docker

This project can be deployed locally using [Docker Compose](https://docs.docker.com/compose/).

```sh
docker-compose up --build
```

See [DOCKER.md](DOCKER.md) for more information.

## Usage
The API is hosted at https://progress.deco.mp. There are two main start routes: one for the structure of the data and one for the data itself.

Structure: [projects/](https://progress.deco.mp/projects/)

Data: Structure: [data/](https://progress.deco.mp/data/)

In order to push data for a project, you will need a site admin to create a project for you in the database and give you the project slug and API key. Please reach out to me on Github, Discord (ethteck), or wherever, if you'd like to use Frogress for your project.

Read [User Guide](GUIDE.md) to learn more.

## Database structure

In a nutshell, the db heirarchy goes `project` > `version` > `category` > `entry` > `measure`. The database is extremely flexible in that it allows you to organize your data however you want. That being said, there is a "standard" way of doing this that will be explained below. 

**Note**: Any time a "slug" field is mentioned, this field is used as a url-friendly identifier. A slug for the "Bunny's Birthday Bonanza project" might be `bbb`, for example.

### Project

A project is a decompilation project, which would usually be tied to a GitHub repo and game.

`slug`: A slug for the project ("bbb")

`name`: Human-friendly name ("Bunny's Birthday Bonanza")

`auth_key`: The secret key used to push data to this project, given to you by a site admin

The following 3 fields are optional:

`repository`: A url to the git repository for this project

`discord`: A url to the discord server for this project

`website`: A url to the website for this project

### Version

Each project contains any number of versions.

`slug`: A slug for the version ("us")

`name`: Human-friendly name ("US 1.0")

### Category

Each version contains any number of categories. A category can represent anything you want, but the original idea was to allow for categories to represent parts of the project, such as different files being decompiled, different categories of data, etc. The reason we added this layer is that there are arguably different kinds of metrics one may track for different aspects of a project. 

As an example, you could have a "documentation" category in which you estimate documentation % and track it in frogress. The documentation progress doesn't really align with the decompilation progress, so it makes sense to put it in a totally different bucket and have different entries associated with it.

If this extra layer isn't necessary for your project, feel free to just use one category.

`slug`: A slug for the category ("default", "actors", "documentation")

`name`: Human-friendly name

The above layers of the schema define the structure of the project in the database. Once you have an api key from a site admin, you can set this up yourself with [cli.py](cli.py). The below two layers are created upon data insertion.

### Entry

An entry represents a snapshot in time and is tied to a specific category. An entry holds a number of measures, which are bits of data.

`timestamp`: A unix timestamp associated with the entry, as an integer (12345)
`git_hash`: The git commit hash that the entry is based upon ("af03bc")

### Measure

Finally, we arrive at the actual data itself. Each measure has a type and value. 

`type`: The type of the measure, as as string ("code", "code/total", "functions", "functions_total")

`value`: An integer representing the value of this measure (300, 10000)

Most projects use the "/" convention, so the current decompiled "code" bytes would have the "code" type, and the type for the total amount of decompilable code would be "code/total". However, the types can be named however you want. This may change later on.

