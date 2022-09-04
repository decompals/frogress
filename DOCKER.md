# Docker

There are 3 images that make up this project:

- `frogress` - the app itself, based upon [python:3.10-slim](https://hub.docker.com/_/python) image.
- `caddy` - [caddy](https://hub.docker.com/_/caddy) running as a reverse proxy that also provides auto-https for production
- `postgres` - [postgresql](https://hub.docker.com/_/postgres) database

## Production

By default, `PRODUCTION=NO` is set in the `caddy.env` file which means the reverse proxy (Caddy) will listen on port 80/http. Changing this to `PRODUCTION=YES` will cause Caddy to listen on 443/https and will generate SSL certificates and attempt to confirm ownership of the domain (progress.deco.mp).

Note: The production domain can be overridden by setting `DOMAIN_NAME=www.mydomainname.com` environment variable within the `caddy.env`

## Persisted data

The database data is persisted to `./deployment/postgres/data`, this can be changed within the `docker-compose.yaml` file.

## Daemon

To run the project in the background, add the `--daemon` argument to `docker-compose up`.

## Monitoring

Check what containers are running:
```sh
$ docker-compose ps
       Name                      Command              State                                        Ports                                      
----------------------------------------------------------------------------------------------------------------------------------------------
frogress_caddy_1      /entrypoint.sh                  Up      2019/tcp, 0.0.0.0:443->443/tcp,:::443->443/tcp, 0.0.0.0:80->80/tcp,:::80->80/tcp
frogress_frogress_1   /entrypoint.sh                  Up      0.0.0.0:8000->8000/tcp,:::8000->8000/tcp                                        
frogress_postgres_1   docker-entrypoint.sh postgres   Up      0.0.0.0:5432->5432/tcp,:::5432->5432/tcp  
```

Jump inside the main frogress container:
```sh
$ docker exec -ti frogress_frogress_1 bash
root@7a1645fece43:/frogress#
```

Follow logs for the main frogress container:
```sh
$ docker logs -f frogress_frogress_1
Waiting for database to become available on postgres:5432...
Waiting for database to become available on postgres:5432...
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, frog_api, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying frog_api.0001_initial... OK
  Applying frog_api.0002_remove_entry_version_category_entry_category... OK
  Applying frog_api.0003_rename_decompiled_functions_entry_decompiled_chunks_and_more... OK
  Applying frog_api.0004_alter_category_options_alter_entry_options_and_more... OK
  Applying frog_api.0005_remove_entry_decompiled_bytes_and_more... OK
  Applying frog_api.0006_alter_project_auth_key... OK
  Applying frog_api.0007_alter_entry_timestamp... OK
  Applying frog_api.0008_project_discord_project_repository_project_website... OK
  Applying frog_api.0009_alter_project_discord_alter_project_repository_and_more... OK
  Applying sessions.0001_initial... OK
Watching for file changes with StatReloader
```
