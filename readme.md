# Party App

A web application for managing games for a party.

Powered by Django framework.

## Quickstart

```bash
# activate your python environment
# recommend python=3.12 and above
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -i https://artifact.stengglink.com/repository/pypi-proxy/simple

# set up your .env files (refer to section below)

python init_app.py
python main/manage.py runserver

```

## Environment

To generate a `DJANGO_SECRET_KEY`, you can run this command

`python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

### Example .env file

```shell
# ./.env
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

## Django Guide

```shell
django-admin startproject main
cd main
python manage.py startapp accounts
python manage.py startapp bingo
python manage.py startapp obstacle
python manage.py startapp knowledge
```

Always create your own custom user models. [Docs ref here](https://learndjango.com/tutorials/django-custom-user-model).
