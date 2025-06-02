from django.conf import settings


def get_sw_version(*args, **kwargs):
    """function to get version number from settings.py

    :return: version string
    :rtype: str
    """
    return {"APP_VERSION": settings.WEBAPP_VERSION}


def get_company_info(*args, **kwargs) -> dict:
    """function to get company information from settings.py

    :return: company information
    :rtype: dict
    """
    return {
        "INFO_COMPANY_NAME": settings.INFO_COMPANY_NAME,
        "INFO_COMPANY_DEPARTMENT": settings.INFO_COMPANY_DEPARTMENT,
        "INFO_COMPANY_COMMITTEE": settings.INFO_COMPANY_COMMITTEE,
    }


def is_development_environment(host) -> bool:
    if settings.IS_DEVELOPMENT_ENV:
        return {"is_development_env": True}
    return {"is_development_env": False}
