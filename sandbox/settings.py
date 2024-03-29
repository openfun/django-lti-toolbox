"""
Django settings for sandbox project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

from configurations import Configuration, values

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join("/", "data")

# Disable pylint error "W0232: Class has no __init__ method", because base Configuration
# class does not define an __init__ method.
# pylint: disable = W0232


class Base(Configuration):
    """
    This is the base configuration every configuration (aka environment) should inherit from. It
    is recommended to configure third-party applications by creating a configuration mixins in
    ./configurations and compose the Base configuration with those mixins.
    It depends on an environment variable that SHOULD be defined:
    * DJANGO_SECRET_KEY
    You may also want to override default configuration by setting the following environment
    variables:
    * DB_NAME
    * DB_HOST
    * DB_PASSWORD
    * DB_USER
    """

    AUTHENTICATION_BACKENDS = [
        "lti_toolbox.backend.LTIBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]

    DEBUG = False

    # Security
    ALLOWED_HOSTS = []
    SECRET_KEY = values.Value(None)

    # SECURE_PROXY_SSL_HEADER allows to fix the scheme in Django's HttpRequest
    # object when your application is behind a reverse proxy.
    #
    # Keep this SECURE_PROXY_SSL_HEADER configuration only if :
    # - your Django app is behind a proxy.
    # - your proxy strips the X-Forwarded-Proto header from all incoming requests
    # - Your proxy sets the X-Forwarded-Proto header and sends it to Django
    #
    # In other cases, you should comment the following line to avoid security issues.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Disable Samesite flag in session and csrf cookies, because a LTI tool provider app
    # is meant to run in an iframe on external websites.
    # Note : The better solution is to send a flag Samesite=none, because
    # modern browsers are considering Samesite=Lax by default when the flag is
    # not specified.
    # It will be possible to specify CSRF_COOKIE_SAMESITE="none" in Django 3.1
    CSRF_COOKIE_SAMESITE = None
    SESSION_COOKIE_SAMESITE = None

    # Privacy
    SECURE_REFERRER_POLICY = "same-origin"

    # Application definition
    ROOT_URLCONF = "urls"
    WSGI_APPLICATION = "wsgi.application"

    # Database
    DATABASES = {
        "default": {
            "ENGINE": values.Value(
                "django.db.backends.postgresql_psycopg2",
                environ_name="DB_ENGINE",
                environ_prefix=None,
            ),
            "NAME": values.Value("lti", environ_name="DB_NAME", environ_prefix=None),
            "USER": values.Value("fun", environ_name="DB_USER", environ_prefix=None),
            "PASSWORD": values.Value(
                "pass", environ_name="DB_PASSWORD", environ_prefix=None
            ),
            "HOST": values.Value(
                "localhost", environ_name="DB_HOST", environ_prefix=None
            ),
            "PORT": values.Value(5432, environ_name="DB_PORT", environ_prefix=None),
        }
    }

    # Templates
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [os.path.join(BASE_DIR, "sandbox", "templates")],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "django.template.context_processors.csrf",
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.media",
                    "django.template.context_processors.request",
                    "django.template.context_processors.tz",
                ],
            },
        },
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    ]

    # Django applications from the highest priority to the lowest
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        # LTI Toolbox
        "lti_toolbox",
        # Sandbox utilities
        "crispy_forms",
    ]

    CRISPY_TEMPLATE_PACK = "bootstrap4"

    # Cache
    CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    }


class Development(Base):
    """
    Development environment settings
    We set DEBUG to True and configure the server to respond from all hosts.
    """

    DEBUG = True
    ALLOWED_HOSTS = ["*"]

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[%(levelname)s] [%(asctime)s] [%(module)s] "
                "%(process)d %(thread)d %(message)s"
            }
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            }
        },
        "loggers": {
            "oauthlib": {"handlers": ["console"], "level": "DEBUG", "propagate": True},
            "lti_toolbox": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": True,
            },
            "django": {"handlers": ["console"], "level": "INFO", "propagate": True},
        },
    }


class Test(Base):
    """Test environment settings"""


class ContinuousIntegration(Test):
    """
    Continuous Integration environment settings
    nota bene: it should inherit from the Test environment.
    """


class Production(Base):
    """Production environment settings
    You must define the DJANGO_ALLOWED_HOSTS environment variable in Production
    configuration (and derived configurations):
    DJANGO_ALLOWED_HOSTS="foo.com,foo.fr"
    """

    # Security
    ALLOWED_HOSTS = values.ListValue(None)
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    # System check reference:
    # https://docs.djangoproject.com/en/2.2/ref/checks/#security
    SILENCED_SYSTEM_CHECKS = values.ListValue(
        [
            # Allow to disable django.middleware.clickjacking.XFrameOptionsMiddleware
            # It is necessary since the LTI tool provider application will be displayed
            # in an iframe on external LMS sites.
            "security.W002",
            # SECURE_SSL_REDIRECT is not defined in the base configuration
            "security.W008",
            # No value is defined for SECURE_HSTS_SECONDS
            "security.W004",
        ]
    )

    # For static files in production, we want to use a backend that includes a hash in
    # the filename, that is calculated from the file content, so that browsers always
    # get the updated version of each file.
    STORAGE = {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
        }
    }


class Feature(Production):
    """
    Feature environment settings

    nota bene: it should inherit from the Production environment.
    """


class Staging(Production):
    """
    Staging environment settings

    nota bene: it should inherit from the Production environment.
    """


class PreProduction(Production):
    """
    Pre-production environment settings

    nota bene: it should inherit from the Production environment.
    """
