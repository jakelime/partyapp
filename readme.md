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
# refer to example below

python init_app.py
python main/manage.py runserver

```

## Example `.env` file

To generate a `DJANGO_SECRET_KEY`, you can run this command

`python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

### `.env` file for personal laptop development

```shell
DJANGO_SECRET_KEY='somesecret'
DJANGO_MEDIA_ROOT='/www/media'
DJANGO_MEDIA_URL='media/'
DJANGO_STATIC_ROOT='/www/static'
DJANGO_STATIC_URL='static/'
DJANGO_DEBUG=true
IS_DEVELOPMENT_ENV=true
INFO_COMPANY_NAME='myAwesomeCompany'
INFO_COMPANY_DEPARTMENT='DigitalTransformationDept'
INFO_COMPANY_COMMITTEE='Party Organisers'
ADMIN_EMAIL='admin@somecompany.com'
```

## Django template start up

```shell
django-admin startproject main
cd main
python manage.py startapp accounts
python manage.py startapp automsa
```

Here is why:
`https://learndjango.com/tutorials/django-custom-user-model`

### To create django apps/modules

Use built-in Django features

```bash
python manage.py startapp devtools
python manage.py startapp webdocs
```
