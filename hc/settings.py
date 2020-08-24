"""
Django settings for healthchecks project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings
"""

import os
import warnings

import ldap
from django_auth_ldap.config import LDAPSearch, LDAPGroupQuery, GroupOfNamesType, PosixGroupType


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def envbool(s, default):
    v = os.getenv(s, default=default)
    if v not in ("", "True", "False"):
        msg = "Unexpected value %s=%s, use 'True' or 'False'" % (s, v)
        raise Exception(msg)
    return v == "True"


def envint(s, default):
    v = os.getenv(s, default)
    if v == "None":
        return None

    return int(v)


SECRET_KEY = os.getenv("SECRET_KEY", "---")
METRICS_KEY = os.getenv("METRICS_KEY")
DEBUG = envbool("DEBUG", "True")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "healthchecks@example.org")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL")
USE_PAYMENTS = envbool("USE_PAYMENTS", "False")
REGISTRATION_OPEN = envbool("REGISTRATION_OPEN", "True")
VERSION = ""
with open(os.path.join(BASE_DIR, "CHANGELOG.md"), encoding="utf-8") as f:
    for line in f.readlines():
        if line.startswith("## v"):
            VERSION = line.split()[1]
            break


INSTALLED_APPS = (
    "hc.accounts",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "compressor",
    "hc.api",
    "hc.front",
    "hc.payments",
)

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "hc.accounts.middleware.TeamAccessMiddleware",
)

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    "hc.accounts.backends.EmailBackend",
    "hc.accounts.backends.ProfileBackend",
)

ROOT_URLCONF = "hc.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "hc.front.context_processors.branding",
                "hc.payments.context_processors.payments",
            ]
        },
    }
]

WSGI_APPLICATION = "hc.wsgi.application"
TEST_RUNNER = "hc.api.tests.CustomRunner"


# Default database engine is SQLite. So one can just check out code,
# install requirements.txt and do manage.py runserver and it works
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("DB_NAME", BASE_DIR + "/hc.sqlite"),
    }
}

# You can switch database engine to postgres or mysql using environment
# variable 'DB'. Travis CI does this.
if os.getenv("DB") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.getenv("DB_HOST", ""),
            "PORT": os.getenv("DB_PORT", ""),
            "NAME": os.getenv("DB_NAME", "hc"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "CONN_MAX_AGE": envint("DB_CONN_MAX_AGE", "0"),
            "TEST": {"CHARSET": "UTF8"},
            "OPTIONS": {
                "sslmode": os.getenv("DB_SSLMODE", "prefer"),
                "target_session_attrs": os.getenv(
                    "DB_TARGET_SESSION_ATTRS", "read-write"
                ),
            },
        }
    }

if os.getenv("DB") == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "HOST": os.getenv("DB_HOST", ""),
            "PORT": os.getenv("DB_PORT", ""),
            "NAME": os.getenv("DB_NAME", "hc"),
            "USER": os.getenv("DB_USER", "root"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "TEST": {"CHARSET": "UTF8"},
        }
    }

USE_TZ = True
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

SITE_ROOT = os.getenv("SITE_ROOT", "http://localhost:8000")
SITE_NAME = os.getenv("SITE_NAME", "Mychecks")
MASTER_BADGE_LABEL = os.getenv("MASTER_BADGE_LABEL", SITE_NAME)
PING_ENDPOINT = os.getenv("PING_ENDPOINT", SITE_ROOT + "/ping/")
PING_EMAIL_DOMAIN = os.getenv("PING_EMAIL_DOMAIN", "localhost")
PING_BODY_LIMIT = envint("PING_BODY_LIMIT", "10000")
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "static-collected")
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)
COMPRESS_OFFLINE = True
COMPRESS_CSS_HASHING_METHOD = "content"

# Discord integration
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")

# Email integration
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = envint("EMAIL_PORT", "587")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = envbool("EMAIL_USE_TLS", "True")
EMAIL_USE_VERIFICATION = envbool("EMAIL_USE_VERIFICATION", "True")

# Slack integration
SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")

# Pushover integration
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")
PUSHOVER_SUBSCRIPTION_URL = os.getenv("PUSHOVER_SUBSCRIPTION_URL")
PUSHOVER_EMERGENCY_RETRY_DELAY = int(os.getenv("PUSHOVER_EMERGENCY_RETRY_DELAY", "300"))
PUSHOVER_EMERGENCY_EXPIRATION = int(os.getenv("PUSHOVER_EMERGENCY_EXPIRATION", "86400"))

# Pushbullet integration
PUSHBULLET_CLIENT_ID = os.getenv("PUSHBULLET_CLIENT_ID")
PUSHBULLET_CLIENT_SECRET = os.getenv("PUSHBULLET_CLIENT_SECRET")

# Telegram integration -- override in local_settings.py
TELEGRAM_BOT_NAME = os.getenv("TELEGRAM_BOT_NAME", "ExampleBot")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# SMS and WhatsApp (Twilio) integration
TWILIO_ACCOUNT = os.getenv("TWILIO_ACCOUNT")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_USE_WHATSAPP = envbool("TWILIO_USE_WHATSAPP", "False")

# PagerDuty
PD_VENDOR_KEY = os.getenv("PD_VENDOR_KEY")

# Trello
TRELLO_APP_KEY = os.getenv("TRELLO_APP_KEY")

# Matrix
MATRIX_HOMESERVER = os.getenv("MATRIX_HOMESERVER")
MATRIX_USER_ID = os.getenv("MATRIX_USER_ID")
MATRIX_ACCESS_TOKEN = os.getenv("MATRIX_ACCESS_TOKEN")

# Apprise
APPRISE_ENABLED = envbool("APPRISE_ENABLED", "False")

# Local shell commands
SHELL_ENABLED = envbool("SHELL_ENABLED", "False")

# LDAP
# Baseline configuration.
AUTH_LDAP_SERVER_URI = os.getenv("AUTH_LDAP_SERVER_URI")

AUTH_LDAP_BIND_DN = os.getenv("AUTH_LDAP_BIND_DN")
AUTH_LDAP_BIND_PASSWORD = os.getenv("AUTH_LDAP_BIND_PASSWORD")

# Set up the basic user parameters.
AUTH_LDAP_USERS_BASE_DN = os.getenv("AUTH_LDAP_USERS_BASE_DN")
AUTH_LDAP_USER_SEARCH = LDAPSearch(AUTH_LDAP_USERS_BASE_DN,
                                   ldap.SCOPE_SUBTREE,
                                   '(&(objectclass=user)(|(username=%(user)s)(mail=%(user)s)))')

# Set up the basic group parameters.
AUTH_LDAP_GROUPS_BASE_DN = os.getenv("AUTH_LDAP_GROUPS_BASE_DN")
AUTH_LDAP_GROUP_TYPE = PosixGroupType(name_attr='cn')
# AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr='cn')
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(AUTH_LDAP_GROUPS_BASE_DN,
                                    ldap.SCOPE_SUBTREE,
                                    '(objectClass=posixGroup)')

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    'is_staff': LDAPGroupQuery('cn=admins,ou=groups,dc=cloudron'),
    'is_superuser': LDAPGroupQuery('cn=admins,ou=groups,dc=cloudron'),
}

AUTH_LDAP_MIRROR_GROUPS = True  # Will sync ldap groups to django, if not exist

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache distinguised names and group memberships for an hour to minimize
# LDAP traffic.
AUTH_LDAP_CACHE_TIMEOUT = 3600

if os.path.exists(os.path.join(BASE_DIR, "hc/local_settings.py")):
    from .local_settings import *
else:
    warnings.warn("local_settings.py not found, using defaults")
