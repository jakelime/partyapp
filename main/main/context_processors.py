from django.conf import settings


def get_sw_version(*args, **kwargs):
    """function to get version number from settings.py

    :return: version string
    :rtype: str
    """
    return {"appVersion": settings.WEBAPP_VERSION}


def is_development_environment(host) -> bool:
    if settings.IS_DEVELOPMENT_ENV:
        return {"is_development_env": True}
    return {"is_development_env": False}
