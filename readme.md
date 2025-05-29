# Jetforge

A Django application server.

## Quickstart

```bash
# activate your python environment
# recommend python=3.12.x
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -i https://artifact.stengglink.com/repository/pypi-proxy/simple

# set up your .env files
```


## Example `.env` file

To generate a `DJANGO_SECRET_KEY`, you can run this command

`python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

### `.env` file for personal laptop development

```shell
DJANGO_SECRET_KEY="django-insecure-gkf$-u6kujne%(wx+md(+=82%93wvx$asc)"

## in production, point this to the shared volume for storing mediafiles
## leave it blank to create /media path in source code dir

DJANGO_MEDIA_ROOT="/www/media"
DJANGO_MEDIA_URL="media/"
DJANGO_STATIC_ROOT="/www/static"
DJANGO_STATIC_URL="static/"

DJANGO_SUPERUSER_USERNAME=nameyourownadmin
DJANGO_SUPERUSER_EMAIL=nameyourownadmin@stengg.com
DJANGO_SUPERUSER_PASSWORD=mysecretpassword

## Database path.
## If this is enabled, PGDB will be disabled
## Database mode will switch over to local sqlite3
DB_PATH="/jetforge_data/jetforge.db"
# PGDB_HOST=pgdb
# PGDB_HOST=localhost
# PGDB_DBNAME=jetforgedb
# PGDB_USER=jetforgeapp
# PGDB_PASSWORD='abcdef'
# PGDB_PORT=12345

# For debugging
IS_DEVELOPMENT_ENV=true

## This section is not implemented
# EMAIL_HOST="st_smtp_dummy.stengg.com"
# EMAIL_PORT=25
# DEFAULT_FROM_EMAIL="dummy@stengg.com"
# SERVER_EMAIL="dummy@stengg.com"

WEBD_DIRPATH=/var/data/www/media/webdocs
WEBD_DIRPATH_PREFIX_COMPONENTS=/var/data/www/media
WEBD_GIT_PULL_API_URL='http://nginx/api/v1/webdocs/api-pull?token=xx.yy.zz'
WEBD_PULL_HISTORY_URL='http://nginx/api/v1/webdocs/get_logs'

## This is for production
# WEBD_DIRPATH_PREFIX_COMPONENTS=/www/media
# WEBD_DIRPATH=/www/media/webdocs
```

### Change these variables for PROD server

```shell
DJANGO_SECRET_KEY='pleasegenerateyourownsecretkey-x+md(+=82%93wvx$asc)dimx#o5fs#ic+*p'
LOCALDB_DIR="/www/jetforge_data/jetforge.db"
DJANGO_MEDIA_ROOT="www/media"
DJANGO_MEDIA_URL="media/"
DJANGO_STATIC_ROOT="/www/static"
DJANGO_STATIC_URL="static/"
IS_DEVELOPMENT_ENV=false
```

## Django template start up

```shell
django-admin startproject main
cd main
python manage.py startapp accounts
python manage.py startapp automsa
```

## SQlite to Postgres Migration guide

1. On the exporting server with (default SqliteDB), run `python manage.py mlrsexport`
1. On the importing server with PosgresDB, run `python manage.py mlrsimport`
1. After import, the the `pg_serial_sequence` variable in the database is not updated to the latest
1. Run this command to reset sqlsequence for all the tables `python manage.py sqlsequencereset mlrs`
   1. It will output SQL script to stdout

      ```sql
      BEGIN;
      SELECT setval(pg_get_serial_sequence('"mlrs_areacode"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "mlrs_areacode";
      SELECT setval(pg_get_serial_sequence('"mlrs_enginetype"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "mlrs_enginetype";
      SELECT setval(pg_get_serial_sequence('"mlrs_engineplatform"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "mlrs_engineplatform";
      SELECT setval(pg_get_serial_sequence('"mlrs_approvalstatus"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "mlrs_approvalstatus";
      SELECT setval(pg_get_serial_sequence('"mlrs_macrohardnessunit"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "mlrs_macrohardnessunit";
      SELECT setval(pg_get_serial_sequence('"mlrs_microhardnessunit"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "mlrs_microhardnessunit";
      SELECT setval(pg_get_serial_sequence('"mlrs_shorehardnessunit"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "mlrs_shorehardnessunit";
      SELECT setval(pg_get_serial_sequence('"mlrs_labrecord"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "mlrs_labrecord";
      SELECT setval(pg_get_serial_sequence('"mlrs_labrecordgeneratedreport"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "mlrs_labrecordgeneratedreport";
      COMMIT;
      ```

   1. Use `pgsql` tool, DBeaver tool, or some other tool to execute the script in `jetforgedb` database

## Create new django app

### Always create a custom user model

Here is why:
`https://learndjango.com/tutorials/django-custom-user-model`

### To create django apps/modules

Use built-in Django features

```bash
python manage.py startapp devtools
python manage.py startapp webdocs
```
